from airembr.system.config.global_config import global_settings
from airembr.system.config.log_config import logging_config
from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.config.server_config import server_config
from airembr.system.config.mysql_config import mysql_config
from airembr.model.settings import SystemSettings
from airembr.sdk.storage.cache.config import redis_config

system_settings = [
    SystemSettings(
        **{
            "label": "EFF_LATE_PROFILE_BINDING",
            "value": global_settings.eff_late_profile_binding,
            "desc": "Default: 'no'. Experimental feature. Late Profile Binding. By default disabled."
        }
    ),
    SystemSettings(
        **{
            "label": "PULSAR_HOST",
            "value": global_settings.pulsar_host,
            "desc": "Default: pulsar://localhost:6650. Pulsar broker connection."
        }
    ),
    SystemSettings(
        **{
            "label": "PULSAR_API",
            "value": global_settings.pulsar_api,
            "desc": "Default: http://localhost:8080. Pulsar API connection."
        }
    ),
    SystemSettings(
        **{
            "label": "PULSAR_AUTH_TOKEN",
            "value": bool(global_settings.pulsar_auth_token),
            "desc": "Default: None. Pulsar JWT API TOKEN."
        }
    ),
    SystemSettings(
        **{
            "label": "PULSAR_TENANT",
            "value": global_settings.pulsar_tenant,
            "desc": "Default: tracardi. Pulsar Tenant."
        }
    ),
    SystemSettings(
        **{
            "label": "PULSAR_CLUSTER",
            "value": global_settings.pulsar_cluster,
            "desc": "Default: 'standalone'. Pulsar Cluster."
        }
    ),
    SystemSettings(
        **{
            "label": "PULSAR_STORAGE_POOL",
            "value": global_settings.pulsar_storage_pool,
            "desc": "Default: 1000. Pulsar Storage Pool size."
        }
    ),
    SystemSettings(
        **{
            "label": "PULSAR_SERIALIZER",
            "value": global_settings.pulsar_serializer,
            "desc": "Default: 'json'. Pulsar Serializer."
        }
    ),
    SystemSettings(
        **{
            "label": "ENTITY_CACHE_TTL",
            "value": global_settings.entity_cache_ttl,
            "desc": "Default: 24h. How long keep cached entities in memory if they do not change (in seconds)."
        }
    ),
    SystemSettings(
        **{
            "label": "SYSTEM_EVENTS_FOR_PROPERTY_CHANGE",
            "value": global_settings.system_events_for_property_change,
            "desc": "Default: None. Enable monitoring of profile property change. Put property name here to collect system event `Property Changed`."
        }
    ),
    SystemSettings(
        **{
            "label": "API_DOCS",
            "value": server_config.api_docs,
            "desc": "Default: Yes. Turns off APi documentations at /docs."
        }
    ),
    SystemSettings(
        **{
            "label": "MULTI_TENANT",
            "value": sys_config.multi_tenant,
            "desc": "Default: No. Turns on multi tenancy feature for commercial versions."
        }
    ),
    SystemSettings(
        **{
            "label": "EXPOSE_GUI_API",
            "value": sys_config.expose_gui_api,
            "desc": "Expose GUI API or not, defaults to True, "
                    "can be changed by setting to 'yes' (then it's True) or 'no', "
                    "which makes it False."
        }
    ),
    SystemSettings(
        **{
            "label": "EVENT_TO_PROFILE_COPY_CACHE_TTL",
            "value": memory_cache_config.event_to_profile_coping_ttl,
            "desc": "Default: 15. Set caching time for the event to profile schema. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "SOURCE_CACHE_TTL",
            "value": memory_cache_config.source_ttl,
            "desc": "Default: 30. Each event source read is cached for given seconds. That means that when you change any "
                    "event source data, the change it wil be available with max 30 seconds."
        }
    ),
    SystemSettings(
        **{
            "label": "EVENT_VALIDATION_CACHE_TTL",
            "value": memory_cache_config.event_validation_cache_ttl,
            "desc": "Default: 15. Set event validation schema caching time. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "TRIGGER_RULE_CACHE_TTL",
            "value": memory_cache_config.trigger_rule_cache_ttl,
            "desc": "Default: 15. Set cache time for workflow triggers. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "DATA_COMPLIANCE_CACHE_TTL",
            "value": memory_cache_config.data_compliance_cache_ttl,
            "desc": "Default: 30. Set cache time for data compliance rules Set 0 for no caching."
        }
    ),

    SystemSettings(
        **{
            "label": "EVENT_METADATA_CACHE_TTL",
            "value": memory_cache_config.event_mapping_cache_ttl,
            "desc": "Default: 15. Set cache time for event tagging, indexing, etc. configuration. Set 0 for no caching."
        }
    ),

    SystemSettings(
        **{
            "label": "MYSQL_HOST",
            "value": mysql_config.mysql_host,
            "desc": "Mysql host."
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_PORT",
            "value": mysql_config.mysql_port,
            "desc": "Default: 3306, Mysql port."
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_SCHEMA_ASYNC",
            "value": mysql_config.mysql_schema_async,
            "desc": "Default: mysql+aiomysql://, Mysql schema."
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_SCHEMA_SYNC",
            "value": mysql_config.mysql_schema_sync,
            "desc": "Default: mysql+pymysql://, Mysql sync schema."
        }
    ),
    SystemSettings(
        **{
            "label": "LOGGING_LEVEL",
            "value": sys_config.logging_level,
            "desc": "The logging level. Defaults to logging.WARNING."
        }
    ),
    SystemSettings(
        **{
            "label": "PRODUCTION",
            "value": sys_config.version.production,
            "desc": "This variable defines default API context. If it is set to \"production,\" "
                    "the data will be accessible within the production GUI context."
        }
    ),

    SystemSettings(
        **{
            "label": "TENANT_NAME",
            "value": sys_config.version.name,
            "desc": "Default: None. This setting defines a prefix for all tracardi indices."
        }
    ),
    SystemSettings(
        **{
            "label": "SERVER_LOGGING_LEVEL",
            "value": server_config.server_logging_level,
            "desc": "Default WARNING. Sets logging level of uvicorn server. It may be useful to set it to INFO when"
                    " debugging Tracardi."
        }
    ),
    SystemSettings(
        **{
            "label": "REDIS_HOST",
            "value": redis_config.redis_host,
            "desc": "Default: redis://localhost:6379. This setting is used only when SYNC_PROFILE_TRACKS is equal to "
                    "yes. This is the host URI of Redis instance that is required to synchronize profile tracks. "
                    "Available only in commercial version of Tracardi."
        }
    ),
    SystemSettings(
        **{
            "label": "REDIS_USERNAME",
            "value": "Set" if redis_config.redis_user is not None else "Unset",
            "desc": "Default: None. This is Redis username"
        }
    ),
    SystemSettings(
        **{
            "label": "REDIS_PASSWORD",
            "value": "Set" if redis_config.redis_password is not None else "Unset",
            "desc": "Default: None. This is Redis password."
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_TRIGGERS",  # This is for GUI
            "value": sys_config.enable_triggers,
            "desc": "Default: no. Enables dispatching events to processes.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_EVENT_RESHAPING",
            "value": sys_config.enable_event_reshaping,
            "desc": "Default: yes. Enables event reshaping.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_EVENT_VALIDATION",
            "value": sys_config.enable_event_validation,
            "desc": "Default: yes. Enables event validation.",
            "expose": True
        }
    ),

    SystemSettings(
        **{
            "label": "DISALLOW_BOT_TRAFFIC",
            "value": sys_config.disallow_bot_traffic,
            "desc": "Default: Yes. If set to Yes then block bot traffic."
        }
    )
]

cluster_system_settings = [
    {
        "label": "SAVE_LOGS",
        "value": logging_config.save_logs,
        "desc": "Default: yes. When set to yes all logs will be saved in tracardi log."
    }
]


def get_system_envs():
    return {item.label: item.value for item in system_settings if item.expose}


async def list_system_envs():
    _cluster_settings = []
    for item in cluster_system_settings:
        _cluster_settings.append(SystemSettings(
            label=item["label"],
            value=item['value'],
            desc=item['desc'],
            cluster_wide=True
        ))

    return system_settings + _cluster_settings
