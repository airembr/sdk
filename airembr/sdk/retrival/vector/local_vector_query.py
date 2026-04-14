import lancedb

def local_vector_table(database_path, table_name, data):

    db = lancedb.connect(database_path)

    # Drop table if exists (safe reset)
    try:
        db.drop_table(table_name)
    except Exception:
        pass
    # data = [
    #         {
    #             "vector": json.loads(data['vector']),
    #             "text": data['description'],
    #             "id": idx
    #         }
    #         for idx, data in enumerate(rows)
    #     ]
    table = db.create_table(table_name, data=data)

    return table

def local_table_search(table, vector, limit=10):
    results = (
        table.search(vector)
        .metric("cosine")
        .limit(limit)
        .to_list()
    )

    # -----------------------------------
    # Convert distance → cosine similarity
    # and sort explicitly descending
    # -----------------------------------

    return sorted(
        results,
        key=lambda x: 1 - x["_distance"],
        reverse=True
    )