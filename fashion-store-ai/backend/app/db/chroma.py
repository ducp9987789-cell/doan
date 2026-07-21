"""Backward-compatible wrappers around ai-core vector memory."""


async def upsert_documents(documents):
    from bootstrap import get_vector_store_instance

    store = get_vector_store_instance()
    return await store.upsert(documents)


async def query_documents(query: str, n_results: int = 5):
    from bootstrap import get_vector_store_instance

    store = get_vector_store_instance()
    return await store.query(query, n_results=n_results)
