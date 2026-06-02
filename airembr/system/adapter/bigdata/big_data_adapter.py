from airembr.system.adapter.bigdata.starrocks.starrocks_text_adapter import StarrocksTextAdapter
from airembr.system.adapter.bigdata.starrocks.starrocks_text_vector_adapter import StarrocksTextVectorAdapter

from airembr.system.config.sys_config import sys_config
from airembr.system.decorator.run_once import run_once

_bd_adapter_var = sys_config.big_data_adapter

if _bd_adapter_var == 'starrocks':
    from airembr.system.adapter.bigdata.starrocks.starrocks_install_adapter import StarrocksInstallAdapter
    from airembr.system.adapter.bigdata.starrocks.starrocks_event_adapter import StarrocksEventAdapter
    from airembr.system.adapter.bigdata.starrocks.starrocks_entity_history_adapter import StarrocksEntityHistoryAdapter
    from airembr.system.adapter.bigdata.starrocks.starrocks_log_adapter import StarrocksLogAdapter
    from airembr.system.adapter.bigdata.starrocks.starrocks_entity_property_adapter import StarrocksEntityPropertyAdapter
    from airembr.system.adapter.bigdata.starrocks.starrocks_entity_property_state_adapter import \
        StarrocksEntityPropertyStateAdapter
    from airembr.system.adapter.bigdata.starrocks.starrocks_hyper_egde import BdHyperEdgeAdapter
else:
    raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

# Common
from airembr.system.adapter.bigdata.general.bd_entity_adapter import BdEntityAdapter
from airembr.system.adapter.bigdata.general.bd_gui_search_adapter import BdSearchAdapter
from airembr.system.adapter.bigdata.general.bd_count_adapter import BdCountAdapter
from airembr.system.adapter.bigdata.general.bd_metadata_adapter import BdMetadataAdapter
from airembr.system.adapter.bigdata.general.bd_semantic_adapter import BdSemanticAdapter
from airembr.system.adapter.bigdata.general.bd_timer_adapter import BdTimerAdapter
from airembr.system.adapter.bigdata.general.bd_event_job_adapter import DbEventJobAdapter
from airembr.system.adapter.bigdata.general.bd_gid_2_pk import BdGid2PKAdapter
from airembr.system.adapter.bigdata.general.bd_ender_adapter import BdObservationAdapter
from airembr.system.adapter.bigdata.general.bd_state_adapter import BdStateAdapter


@run_once
def _bd_install_adapter():
    return StarrocksInstallAdapter()


@run_once
def _bd_log_adapter():
    return StarrocksLogAdapter()


@run_once
def _bd_entity_adapter():
    return BdEntityAdapter()


@run_once
def _bd_text_adapter():
    return StarrocksTextAdapter()

@run_once
def _bd_text_vector_adapter():
    return StarrocksTextVectorAdapter()


@run_once
def _bd_entity_stitch_adapter():
    return BdGid2PKAdapter()


@run_once
def _bd_event_entity_adapter():
    return StarrocksEntityHistoryAdapter()


@run_once
def _bd_search_adapter():
    return BdSearchAdapter()


@run_once
def _bd_entity_property_adapter():
    return StarrocksEntityPropertyAdapter()


@run_once
def _bd_entity_property_state_adapter():
    return StarrocksEntityPropertyStateAdapter()


@run_once
def _bd_event_adapter():
    return  StarrocksEventAdapter()

@run_once
def _bd_metadata_adapter():
    return BdMetadataAdapter()


@run_once
def _bd_count_adapter():
    return BdCountAdapter()


@run_once
def _bd_timer_adapter():
    return BdTimerAdapter()


@run_once
def _bd_state_adapter():
    return BdStateAdapter()


@run_once
def _bd_observation_adapter():
    return BdObservationAdapter()


@run_once
def _bd_semantic_adapter():
    return BdSemanticAdapter()


@run_once
def _bd_hyper_edge_adapter():
    return BdHyperEdgeAdapter()


bd_install_adapter = _bd_install_adapter()
bd_raw_adapter = None
bd_log_adapter = _bd_log_adapter()
bd_apm_adapter = None
bd_entity_adapter = _bd_entity_adapter()
bd_event_adapter = _bd_event_adapter()
bd_search_adapter = _bd_search_adapter()
bd_event_entity_adapter = _bd_event_entity_adapter()
bd_metadata_adapter = _bd_metadata_adapter()
bd_count_adapter = _bd_count_adapter()
bd_timer_adapter = _bd_timer_adapter()
bd_observation_adapter = _bd_observation_adapter()
bd_semantic_adapter = _bd_semantic_adapter()
db_event_job_adapter = DbEventJobAdapter()
bd_entity_property_adapter = _bd_entity_property_adapter()
bd_entity_property_state_adapter = _bd_entity_property_state_adapter()
bd_hyper_edge_adapter = _bd_hyper_edge_adapter()
bd_entity_stitch_adapter = _bd_entity_stitch_adapter()
bd_state_adapter = _bd_state_adapter()
bd_text_adapter = _bd_text_adapter()
bd_text_vector_adapter = _bd_text_vector_adapter()
