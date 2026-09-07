import asyncio

from airembr.core.hash.hash import md5
from airembr.model.bigdata.flat_text import FlatText
from airembr.sdk.ai.config import LLM_PROVIDER, LLM_PROVIDER_API_KEY, LLM_ENTITY_EXTRACTION_MODEL, \
    MAX_QUESTIONS_PER_OBSERVATION
from airembr.sdk.service.remote.llm.llm_adapter import LLMAdapter
from airembr_sdk.core.date import now_in_utc
from airembr.system.adapter.bigdata.big_data_adapter import bd_text_adapter
from airembr.system.adapter.bigdata.general.utils.mapping import sys_text_mapping
from airembr.system.adapter.bigdata.tool.column_mapper import map_to_table_columns
from airembr.system.adapter.metadata.mysql.service.task_service import background_log
from airembr.system.process.ai.questions.question_prompt import get_questions_prompt
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)
_sys_text_mapping = sys_text_mapping()

BATCH_SIZE = 100
WORKER_COUNT = 5
SAVE_EVERY = 5

adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=LLM_ENTITY_EXTRACTION_MODEL
)


def _build_question_rows(row, questions, now):
    return [
        {
            FlatText.ID: md5(question),
            FlatText.PARENT_ID: row['id'],
            FlatText.OBSERVATION_ID: row['observation_id'],
            FlatText.TEXT: question,
            FlatText.ORIGIN: 4,
            FlatText.REQUIRE_NER: False,
            FlatText.CHUNKED: False,
            FlatText.TS: now
        }
        for question in questions
    ]


async def _flush(question_rows):
    if not question_rows:
        return
    rows_to_stream = list(map_to_table_columns(question_rows, mapping=_sys_text_mapping))
    await bd_text_adapter.stream(rows_to_stream)
    logger.info(f"Saved {len(rows_to_stream)} questions")


async def _process_row(row, now, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            text = row['text_string']
            if len(text) < 10:
                return []

            system_prompt, user_prompt, Questions, temperature = get_questions_prompt(
                text, max_questions=MAX_QUESTIONS_PER_OBSERVATION
            )
            result = await adapter.infer(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                structured_output=Questions
            )
            # print(f"[text_questions] TEXT ({row['id']}): {text}")
            # print(f"[text_questions] QUESTIONS: {result.questions}")
            return _build_question_rows(row, result.questions, now)
        except Exception as e:
            logger.error(e)
            return []


async def text_questions(context):
    count = await bd_text_adapter.count_observations_without_questions()
    logger.info(f"There are {count} observations without questions...")
    if count == 0:
        return

    async with background_log("Question Maker Worker", f"Generating questions in {context}") as (bts, task_id):
        semaphore = asyncio.Semaphore(WORKER_COUNT)
        total_generated = 0
        total_processed = 0

        for start in range(0, count, BATCH_SIZE):
            rows = list(await bd_text_adapter.load_observations_without_questions(start=start, limit=BATCH_SIZE))
            if not rows:
                break

            now = now_in_utc()
            tasks = [asyncio.create_task(_process_row(row, now, semaphore)) for row in rows]

            buffer = []
            unsaved_count = 0
            for task in asyncio.as_completed(tasks):
                question_rows = await task
                buffer.extend(question_rows)
                total_generated += len(question_rows)
                total_processed += 1
                unsaved_count += 1

                if unsaved_count >= SAVE_EVERY:
                    await _flush(buffer)
                    buffer = []
                    unsaved_count = 0
                    await bts.task_progress(task_id, min(99, int(total_processed / count * 100)))

            if buffer:
                await _flush(buffer)
                await bts.task_progress(task_id, min(99, int(total_processed / count * 100)))

            logger.info(f"Processed {len(rows)} observations "
                        f"(processed {total_processed}/{count})")

        await bts.task_progress(task_id, 100)
        logger.info(f"Generated {total_generated} questions for {total_processed} observations in total")
