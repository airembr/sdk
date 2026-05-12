def generate_create_table_sql(schema):
    table_name = schema['table']
    distributed = schema.get('distributed', None)
    partitioned = schema.get('partitioned', None)
    pk = schema.get('pk', None)
    duplicate_key = schema.get('duplicate_key', None)
    engine = schema.get('engine', None)

    props = []

    if engine:
        engine = f"ENGINE={engine}"
        props.append(engine)

    if pk:
        pk = f"PRIMARY KEY({pk})"
        props.append(pk)

    if duplicate_key:
        duplicate_key = f"DUPLICATE KEY({', '.join(duplicate_key)})"
        props.append(duplicate_key)

    if partitioned:
        partitioned = f"PARTITION BY {partitioned}"
        props.append(partitioned)

    if distributed:
        distributed = f"DISTRIBUTED BY {distributed}"
        props.append(distributed)

    buckets = schema.get('buckets', None)
    if buckets:
        buckets = f"BUCKETS {buckets}"
        props.append(buckets)

    order = schema.get('order', None)
    if order:
        order = f"ORDER BY({order})"
        props.append(order)

    properties = schema.get('properties', {})
    if properties:
        properties = f"PROPERTIES ({','.join(properties)})"
        props.append(properties)

    columns = []
    column_defs = schema.get('columns', [])
    if not column_defs:
        raise ValueError(f"Table columns not defined.")

    for column in column_defs:
        stmt = []
        column_type = column['sr_column_type'].upper()
        stmt.append(column['column'])
        stmt.append(column_type)

        col_default_value = column.get('default_value', None)
        col_default = column.get('default', None)

        if col_default:
            if col_default == "NULL":
                stmt.append("NULL")
            else:
                stmt.append("NOT NULL")

        if col_default_value:
            stmt.append(f"DEFAULT {col_default_value}")

        columns.append("  " + " ".join(stmt))

    for index in schema.get('indexes', []):
        columns.append(f"  INDEX {index['index_name']}({','.join(index['columns'])}) USING {index['type']}")

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n" + ",\n".join(columns) + "\n)\n"
    create_table_sql += "\n".join(props)
    create_table_sql += ";"

    return create_table_sql
