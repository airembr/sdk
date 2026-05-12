from airembr.model.system.observation import Observation
from airembr.model.system.headers import Headers
from airembr.system.process.embedding.embedding_worker import embedding_worker


async def run_embedding(headers: Headers,
                        observation: Observation):
    if headers.should_process(service='embedding'):
        # Background worker
        await embedding_worker(observation,
                               queued=headers.should_queue(service='embedding'))
