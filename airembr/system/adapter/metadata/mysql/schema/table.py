from sqlalchemy import Index, Float, ForeignKeyConstraint, TIMESTAMP
from sqlalchemy import (Column, String, DateTime, Boolean, JSON,
                        ForeignKey, PrimaryKeyConstraint, Text, Integer, UniqueConstraint)
from sqlalchemy.orm import relationship

from airembr.sdk.storage.metadata.db_base import Base


class BridgeTable(Base):
    __tablename__ = 'sys_bridge'

    id = Column(String(40), unique=True)
    tenant = Column(String(40))
    name = Column(String(64), index=True)
    description = Column(Text)
    type = Column(String(48))
    config = Column(JSON)
    form = Column(JSON)
    manual = Column('manual', Text, nullable=True, quote=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
    )


class EventSourceTable(Base):
    __tablename__ = 'sys_source'

    id = Column(String(40), index=True)
    tenant = Column(String(40))
    production = Column(Boolean)
    timestamp = Column(DateTime)
    update = Column(DateTime)
    type = Column(String(32))
    bridge_id = Column(String(40), ForeignKey('sys_bridge.id'))
    bridge_name = Column(String(128))
    name = Column(String(64), index=True)
    description = Column(String(255))
    channel = Column(String(32))
    url = Column(String(255))
    enabled = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    transitional = Column(Boolean, default=False)
    tags = Column(String(128), nullable=True)
    groups = Column(String(255))
    icon = Column(String(32))
    config = Column(JSON)
    configurable = Column(Boolean)
    hash = Column(String(255))
    returns_profile = Column(Boolean)
    permanent_profile_id = Column(Boolean, default=False)
    requires_consent = Column(Boolean, default=False)
    synchronize_profiles = Column(Boolean)
    manual = Column('manual', Text, quote=True)
    endpoints_get_url = Column(String(255))
    endpoints_get_method = Column(String(255))
    endpoints_post_url = Column(String(255))
    endpoints_post_method = Column(String(255))

    bridge = relationship("BridgeTable")

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_tenant', 'tenant', 'production', 'enabled')
    )

    running: bool = False


class ResourceTable(Base):
    __tablename__ = 'sys_resource'

    id = Column(String(48))
    type = Column(String(48))
    timestamp = Column(DateTime)
    name = Column(String(64), index=True)
    description = Column(String(255))
    credentials = Column(Text)
    enabled = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    tags = Column(String(128), index=True)
    groups = Column(String(255))
    icon = Column(String(255))
    destination = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False

class DestinationTable(Base):
    __tablename__ = 'sys_destination'

    id = Column(String(48))
    name = Column(String(128), index=True)

    description = Column(Text)
    destination = Column(JSON)
    condition = Column(Text)
    mapping = Column(JSON)
    enabled = Column(Boolean, default=False)
    on_profile_change_only = Column(Boolean)
    trigger_type = Column(Integer)
    event_type_id = Column(String(48))
    event_type_name = Column(String(128))
    source_id = Column(String(48))
    source_name = Column(String(128))
    resource_id = Column(String(40), index=True)
    resource_type = Column(String(16), default="resource")
    tags = Column(String(128), nullable=True)

    trigger_type_id = Column(String(48))
    trigger_type_name = Column(String(128))
    trigger_config = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_dest_table', 'event_type_id', 'source_id', 'enabled', 'tenant', 'production'),

    )

    running: bool = False


class VersionTable(Base):
    __tablename__ = 'sys_version'

    es_schema_version = Column(String(64))
    api_version = Column(String(64))
    mysql_schema_version = Column(String(64))

    tenant = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('tenant', 'api_version'),
    )


class UserTable(Base):
    __tablename__ = 'sys_user'

    id = Column(String(48))
    password = Column(String(128))
    name = Column(String(128))
    email = Column(String(128), index=True)
    roles = Column(String(255))
    enabled = Column(Boolean)
    expiration_timestamp = Column(Integer)
    preference = Column(JSON)

    tenant = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'email'),
        UniqueConstraint('tenant', 'email', 'password', name='uiq_email_password')
    )


Index('index_email_password', UserTable.email, UserTable.password)


class EventValidationTable(Base):
    __tablename__ = 'sys_evt_validation'

    id = Column(String(48))
    name = Column(String(128))
    description = Column(Text)
    validation = Column(JSON)
    ttl = Column(Integer, default=-1)
    tags = Column(String(128), nullable=True)
    event_type = Column(String(64))
    entity_type = Column(String(64))
    enabled = Column(Boolean, default=False)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_event_validation', 'event_type', 'enabled', 'tenant', 'production'),
    )

    running: bool = False



class EventReshapingTable(Base):
    __tablename__ = 'sys_evt_reshaping'

    id = Column(String(48))
    entity_type = Column(String(64))
    name = Column(String(128))
    description = Column(Text)
    reshaping = Column(JSON)
    tags = Column(String(128), nullable=True)
    event_type = Column(String(64))
    event_source_id = Column(String(48))
    event_source_name = Column(String(128))
    enabled = Column(Boolean, default=False)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_event_reshaping', 'event_type', 'tenant', 'production', 'enabled')
    )

    running: bool = False


class EventMappingTable(Base):
    __tablename__ = 'sys_evt_mapping'

    id = Column(String(40), index=True)
    entity_type = Column(String(64))
    name = Column(String(128))
    description = Column(Text)
    event_type = Column(String(64), index=True, unique=True)
    tags = Column(String(128), nullable=True)
    journey = Column(String(64))
    enabled = Column(Boolean, default=False)
    index_schema = Column(JSON)

    # Additional fields for multi-tenancy
    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        UniqueConstraint('event_type', name='uiq_event_type'),
        Index('idx_event_mapping', 'event_type', 'tenant', 'production', 'enabled')
    )

    running: bool = False


class TaskTable(Base):
    __tablename__ = 'sys_task'

    id = Column(String(48))
    timestamp = Column(DateTime)
    status = Column(String(64))
    name = Column(String(128))
    type = Column(String(64))
    progress = Column(Float)
    task_id = Column(String(48))
    params = Column(JSON)
    message = Column(Text)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_gui', 'type', 'tenant', 'production')
    )

    running: bool = False


class SettingTable(Base):
    __tablename__ = 'sys_setting'

    id = Column(String(48))
    timestamp = Column(DateTime)
    name = Column(String(128))
    description = Column(Text)
    type = Column(String(64))
    enabled = Column(Boolean, default=False)
    content = Column(JSON)
    config = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class ConfigurationTable(Base):
    __tablename__ = 'sys_configuration'

    id = Column(String(48))
    timestamp = Column(DateTime)
    name = Column(String(128))
    description = Column(Text)
    enabled = Column(Boolean, default=False)
    tags = Column(String(128), nullable=True)
    config = Column(JSON)
    ttl = Column(Integer, default=0)
    # cluster_wide_value = Column(Boolean)

    tenant = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
    )


# Objects

class EntityObjectTable(Base):
    __tablename__ = 'sys_ent_object'

    id = Column(String(48), nullable=False)
    type = Column(String(128), nullable=False)  # used for properties as children
    description = Column(Text)
    label = Column(String(128))
    pk_id = Column(String(128))  # e.g., "data.contact.email.main"
    mg_id = Column(String(255))  # e.g., "data.contact.email.main"
    properties = Column(JSON)
    stitches = Column(JSON)
    consents = Column(String(255))  # e.g., "data.contact.email.main"
    requires_consent = Column(Boolean, default=False)
    requires_merging = Column(Boolean, default=False)
    lock = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    hash = Column(String(32), nullable=False)

    # Storage mapping
    table = Column(String(64), nullable=True)

    # Multi-tenancy fields
    tenant = Column(String(40), nullable=False)
    production = Column(Boolean, nullable=False)

    running: bool = False

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        UniqueConstraint('type', 'tenant', 'production'),
    )


# Event

class EntityEventTable(Base):
    __tablename__ = 'sys_ent_event'

    id = Column(String(48), nullable=False, primary_key=True)
    type = Column(String(128), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    entity_type = Column(String(48), nullable=False)
    properties = Column(JSON, nullable=True)
    tags = Column(String(128), nullable=True)
    state = Column(String(64), nullable=True)

    # Multi-tenancy fields
    tenant = Column(String(40), nullable=False)
    production = Column(Boolean, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['entity_type', 'tenant', 'production'],
            ['sys_ent_object.type', 'sys_ent_object.tenant', 'sys_ent_object.production']
        ),
        Index('idx_id_tenant_prod', 'id', 'tenant', 'production'),
        Index('idx_entity_type', 'entity_type'),
        Index('idx_type', 'type'),
        UniqueConstraint('type'),
    )


class SysEntSnapshotTimerTable(Base):
    __tablename__ = 'sys_ent_snapshot_timer'

    id = Column(String(40), nullable=False)
    ts = Column(TIMESTAMP, nullable=False)  # When set

    # Multi-tenancy fields
    tenant = Column(String(40), nullable=False)
    production = Column(Boolean, nullable=False)

    running: bool = False

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )


class SysEntSegmentTable(Base):
    __tablename__ = 'sys_ent_segment'

    id = Column(String(40), nullable=False)
    name = Column(String(128))
    description = Column(Text)
    tags = Column(String(128), nullable=True)
    enabled = Column(Boolean, default=False)

    ts = Column(TIMESTAMP, nullable=False)  # When set
    time_field = Column(String(64), nullable=False)
    time_start = Column(TIMESTAMP, nullable=True)
    time_end = Column(TIMESTAMP, nullable=True)

    entity_type = Column(String(64), nullable=False)
    entity_where = Column(String(512), nullable=True)
    sequence = Column(JSON, nullable=True)

    # Multi-tenancy fields
    tenant = Column(String(40), nullable=False)
    production = Column(Boolean, nullable=False)

    running: bool = False

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )


class EmbeddingTable(Base):
    __tablename__ = 'sys_embedding_setting'

    id = Column(String(48))
    timestamp = Column(DateTime)
    name = Column(String(128))
    description = Column(Text)
    event_type_id = Column(String(48))
    event_type_name = Column(String(128))
    enabled = Column(Boolean, default=False)
    tags = Column(String(128), nullable=True)
    source_id = Column(String(48))
    source_name = Column(String(64))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False