import json
from collections import defaultdict
from datetime import datetime
from time import time
from typing import Optional

from airembr.model.system.answer import Answer
from airembr.sdk.ai.config import LLM_PROVIDER, LLM_PROVIDER_API_KEY, LLM_QUERY_MODEL, embedding_host, embedding_api_key
from airembr.sdk.ai.prompt import search_prompt
from airembr.sdk.ai.prompt.fact_search_prompt import observations_to_prompt, observation_hits_to_prompt
from airembr.sdk.service.remote.llm.llm_adapter import LLMAdapter
from airembr.sdk.service.retrieval.reranking.clustering import get_clustered_result
from airembr.sdk.service.retrieval.reranking.ranker import aggregate_results_hybrid
from airembr.system.adapter.bigdata.big_data_adapter import bd_entity_property_adapter, bd_observation_adapter
from airembr.system.command.eql.errors import EqlError
from airembr_sdk.logging.log_handler import get_logger

logger = get_logger(__name__)

adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=LLM_QUERY_MODEL
)


def _deduplcate(results, metrics_by_id, min_score: float = 0.0):
    seen = set()
    unique_items = []
    for rs in results:
        for item in rs:
            key = json.dumps(item, default=str, sort_keys=True)
            if key not in seen:
                seen.add(key)
                obs = dict(item)
                ranked = metrics_by_id.get(obs.get('id'), {})
                obs['_score'] = ranked.get('score', 0.0)
                obs['_occurrences'] = ranked.get('raw_occurrences', 0)
                obs['_best_pos'] = ranked.get('best_position_overall', 0)
                obs['_S_quality'] = ranked.get('S_quality', 0.0)
                obs['_R_standing'] = ranked.get('R_standing', 0.0)
                obs['_C_consensus'] = ranked.get('C_consensus', 0.0)
                obs['_A_agreement'] = ranked.get('A_agreement', 0.0)
                obs['_L_lexical'] = ranked.get('L_lexical', 0.0)
                unique_items.append(obs)
    if min_score > 0.0:
        unique_items = [i for i in unique_items if i['_score'] >= min_score]
    return unique_items


def _group_by_observation(unique_items: list[dict]) -> list[dict]:
    groups = {}
    order = []
    for item in unique_items:
        obs_id = item.get('id', '')
        if obs_id not in groups:
            order.append(obs_id)
            groups[obs_id] = {
                'id': obs_id,
                '_score': item['_score'],
                '_cluster_score': item.get('_cluster_score', 0.0),
                '_cluster_number': item.get('_cluster_number', 0),
                '_occurrences': item['_occurrences'],
                '_best_pos': item.get('_best_pos', 0),
                '_S_quality': item.get('_S_quality', 0.0),
                '_R_standing': item.get('_R_standing', 0.0),
                '_C_consensus': item.get('_C_consensus', 0.0),
                '_A_agreement': item.get('_A_agreement', 0.0),
                '_L_lexical': item.get('_L_lexical', 0.0),
                'label': item.get('label'),
                '_items': [],
            }
        groups[obs_id]['_items'].append(item)

    result = []
    for obs_id in order:
        g = groups[obs_id]
        items_sorted = sorted(g['_items'], key=lambda x: x.get('metadata_time_create') or '')

        summary_max_sim = {}
        desc_max_sim = {}
        for it in g['_items']:
            s = it.get('summary')
            d = it.get('description')
            sim = float(it.get('max_similarity') or 0.0)
            if s:
                summary_max_sim[s] = max(summary_max_sim.get(s, 0.0), sim)
            if d:
                desc_max_sim[d] = max(desc_max_sim.get(d, 0.0), sim)

        seen_summaries = set()
        seen_descriptions = set()
        summaries = []
        descriptions = []
        for it in items_sorted:
            s = it.get('summary')
            d = it.get('description')
            if s and s not in seen_summaries:
                seen_summaries.add(s)
                summaries.append({'text': s, 'similarity': summary_max_sim.get(s)})
            if d and d not in seen_descriptions:
                seen_descriptions.add(d)
                descriptions.append({'text': d, 'similarity': desc_max_sim.get(d)})

        sims = [float(it['max_similarity']) for it in g['_items'] if it.get('max_similarity') is not None]

        result.append({
            'id': obs_id,
            '_score': g['_score'],
            '_cluster_score': g['_cluster_score'],
            '_cluster_number': g['_cluster_number'],
            '_occurrences': g['_occurrences'],
            '_best_pos': g['_best_pos'],
            '_S_quality': g['_S_quality'],
            '_R_standing': g['_R_standing'],
            '_C_consensus': g['_C_consensus'],
            '_A_agreement': g['_A_agreement'],
            '_L_lexical': g['_L_lexical'],
            'label': g['label'],
            'max_similarity': sum(sims) / len(sims) if sims else 0.0,
            'metadata_time_create': items_sorted[0].get('metadata_time_create'),
            'metadata_time_insert': items_sorted[0].get('metadata_time_insert'),
            'summaries': summaries,
            'descriptions': descriptions,
        })

    return result


def _get_text_hits(vector_sim_result):
    ibs_2_text = defaultdict(list)
    seen_texts: dict[str, set] = defaultdict(set)
    for row in vector_sim_result:
        obs_id = row['id']
        text = row['text_string']
        ts = row['ts']
        if row['max_similarity'] < .6:
            continue
        if text not in seen_texts[obs_id]:
            seen_texts[obs_id].add(text)
            ibs_2_text[obs_id].append({
                "text_id": row['text_id'],
                "score": row['max_similarity'],
                "text": text,
                "ts": ts,
                "origin": row.get('origin'),
                "parent_id": row.get('parent_id'),
            })

    return ibs_2_text


def _sort_text_hits(ibs_2_text):
    for key in ibs_2_text:
        ibs_2_text[key].sort(key=lambda x: x['score'], reverse=True)
    return ibs_2_text


def _group_observations(obs_result, score_by_id, obs_2_text, cluster_score_by_id=None, cluster_number_by_id=None, hits=True, items=False):
    memory_rows = [dict(row) for row in obs_result.list()] if obs_result else []
    cluster_score_by_id = cluster_score_by_id or {}
    cluster_number_by_id = cluster_number_by_id or {}
    group_by_id = {}
    for row in memory_rows:
        _obs_id = row.get('id')
        if _obs_id not in group_by_id:
            group_by_id[_obs_id] = {
                "_score": score_by_id.get(_obs_id, 0.0),
                "_cluster_score": cluster_score_by_id.get(_obs_id, 0.0),
                "_cluster_number": cluster_number_by_id.get(_obs_id, 0),
                "_hits": obs_2_text.get(_obs_id, []) if hits else [],
                "items": []
            }
        if items:
            group_by_id[_obs_id]['items'].append({
                "label": row.get('label'),
                "metadata_time_create": row.get('metadata_time_create'),
                "metadata_time_insert": row.get('metadata_time_insert'),
                "summary": row.get('summary'),
                "description": row.get('description'),
            }
            )
    return group_by_id


def _sort_grouped_observations(group_by_id):
    return dict(
        sorted(group_by_id.items(), key=lambda x: x[1]['_score'], reverse=True)
    )


# origin: 1=observation description, 2=fact description, 3=entity description
# (4/5 are machine-generated questions — excluded from the LLM prompt, kept in `memory`)
PROMPT_HIT_ORIGINS = {1, 2, 3}


def _filter_hits_for_prompt(memorized_facts, allowed_origins):
    return {
        obs_id: {
            **obs,
            "_hits": [hit for hit in obs.get("_hits", []) if hit.get("origin") in allowed_origins],
        }
        for obs_id, obs in memorized_facts.items()
    }


async def recall_with_text(query: str,
                           start: int = 0,
                           limit: int = 1000,
                           unmatched_entities: int = 0,
                           unmatched_traits: int = 0,
                           min_score: float = 0.65,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Answer:
    if not query.strip():
        return []

    if not embedding_host:
        raise EqlError(detail="Embedding service is not available. Missing EMBEDDING_HOST in config.",
                       status_code=503)

    if not embedding_api_key:
        raise EqlError(detail="Embedding service is not available. Missing EMBEDDING_API_KEY in config.",
                       status_code=503)

    t = time()

    limit_on_partial_search = 1500

    vector_sim_result = await bd_entity_property_adapter.semantic_search(
        query, limit=limit_on_partial_search, similarity=.65
    )

    # Vector search — returns [hit, ...] ordered by similarity DESC
    logger.info(f"Observation Vector Search Results: {len(vector_sim_result)}")

    obs_2_text = _get_text_hits(vector_sim_result)
    obs_2_text = _sort_text_hits(obs_2_text)

    results = [vector_sim_result]

    corpus = list({
        x['text_string']
        for lst in results
        for x in lst
        if isinstance(x.get('text_string'), str)
    })

    metrics = aggregate_results_hybrid(
        results,
        query=query,
        corpus=corpus,
        text_key="text_string",
        id_key="id",
        method_names=["vector", "eql", "fulltext"],
    )

    # Score lookup from metrics
    metrics_by_id = {m['id']: m for m in metrics}

    # Flatten and deduplicate by dict content
    unique_items = _deduplcate(results, metrics_by_id, min_score=min_score)
    logger.debug(f"Deduplicated observation: {len(unique_items)}")
    unique_items = get_clustered_result(unique_items, top_k=4)
    logger.debug(f"Clustered observation: {len(unique_items)}")
    unique_items.sort(key=lambda x: x['_score'], reverse=True)

    grouped = _group_by_observation(unique_items)

    grouped_ids = [g['id'] for g in grouped]
    score_by_id = {g['id']: g['_score'] for g in grouped}
    cluster_score_by_id = {g['id']: g['_cluster_score'] for g in grouped}
    cluster_number_by_id = {g['id']: g['_cluster_number'] for g in grouped}

    obs_result = await bd_observation_adapter.load_observations_by_ids(grouped_ids)

    use_hits = True
    use_observations = False

    memorized_facts = _group_observations(obs_result, score_by_id, obs_2_text, cluster_score_by_id, cluster_number_by_id, hits=use_hits, items=use_observations)
    memorized_facts = _sort_grouped_observations(memorized_facts)

    if use_hits:
        prompt_facts = _filter_hits_for_prompt(memorized_facts, PROMPT_HIT_ORIGINS)
        observation_prompt = observation_hits_to_prompt(prompt_facts)
    else:
        observation_prompt = observations_to_prompt(memorized_facts)

    logger.stat(f"Search Took: {time() - t:.4f}s")

    # DO NOT DELETE THIS
    answer, _ = await adapter.complete(
        system_prompt=search_prompt.system,
        user_prompt=search_prompt.prompt(observation_prompt.strip(), query),
    )
    logger.stat(f"Search+ Inference Took: {time() - t:.4f}s")
    return Answer(
        query=query,
        eql="None",
        memory=memorized_facts,
        answer=answer,
        entity_tolerance=unmatched_entities,
        traits_tolerance=unmatched_traits,
    )
