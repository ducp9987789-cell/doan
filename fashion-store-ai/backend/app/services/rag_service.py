"""Compatibility shim. Prefer ai-core ShoppingAgent."""


class RAGService:
    @staticmethod
    async def retrieve_context(question: str, n_results: int = 5):
        from bootstrap import get_shopping_agent

        agent = get_shopping_agent()
        return await agent.retriever.run(query=question, n_results=n_results)

    @staticmethod
    async def find_suggested_products(question: str, limit: int = 3):
        from bootstrap import get_shopping_agent

        agent = get_shopping_agent()
        return await agent.product_search.run(query=question, limit=limit)

    @staticmethod
    async def generate_answer(question: str, contexts):
        from bootstrap import get_shopping_agent

        result = await get_shopping_agent().run(question)
        return result.answer
