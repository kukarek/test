from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
import asyncio
import time
import json
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.marketplace.repositories.offer_repository import OfferRepository
from app.modules.analytics.repositories.search_event_repository import SearchEventRepository
from app.modules.billing.repositories.subscription_repository import SubscriptionRepository
from app.common.exceptions.exceptions import QuotaExceededException, NotFoundException
from datetime import datetime
import httpx
from app.core.config.settings import settings


class AIRouter:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.openai_timeout)

    async def route_search(self, query: str, available_marketplaces: List[str]) -> Dict[str, str]:
        prompt = f"""
        User search query: "{query}"
        Available marketplaces: {', '.join(available_marketplaces)}

        Analyze the query and return a JSON object indicating which marketplaces would be best for this search.
        Only return JSON, no other text. Example format:
        {{"wildberries": "high", "ozon": "medium", "avito": "low"}}

        Values should be "high", "medium", "low", or "skip".
        """

        try:
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": "You are a search optimization assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 200
            }

            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                result = json.loads(content)
                return result
            else:
                return {marketplace: "high" for marketplace in available_marketplaces}
        except Exception:
            return {marketplace: "high" for marketplace in available_marketplaces}

    async def close(self):
        await self.client.aclose()


class SearchService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.product_repo = ProductRepository(db_session)
        self.offer_repo = OfferRepository(db_session)
        self.search_event_repo = SearchEventRepository(db_session)
        self.subscription_repo = SubscriptionRepository(db_session)
        self.ai_router = AIRouter()

    async def search(
        self,
        user_id: int,
        query: str,
        marketplaces: List[str],
        use_ai_router: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        start_time = time.time()

        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription:
            raise NotFoundException("No active subscription found")

        daily_limit = subscription.plan.daily_search_limit
        daily_searches = await self.search_event_repo.get_user_daily_searches(
            user_id, datetime.utcnow()
        )

        if daily_searches >= daily_limit:
            raise QuotaExceededException(
                f"Daily search limit ({daily_limit}) exceeded"
            )

        ai_used = False
        if use_ai_router:
            ai_used = True
            routing_strategy = await self.ai_router.route_search(query, marketplaces)
            marketplaces = [
                m for m in marketplaces
                if routing_strategy.get(m, "skip") != "skip"
            ]

        products = await self.product_repo.search(query, offset, limit)

        results_with_offers = []
        for product in products:
            filtered_offers = [
                offer for offer in product.offers
                if offer.marketplace in marketplaces
            ]

            if filtered_offers:
                product.offers = filtered_offers
                results_with_offers.append(product)

        execution_time_ms = int((time.time() - start_time) * 1000)

        search_event_data = {
            "user_id": user_id,
            "query": query,
            "results_count": len(results_with_offers),
            "execution_time_ms": execution_time_ms,
            "ai_router_used": ai_used,
            "marketplaces_searched": ",".join(marketplaces),
        }
        await self.search_event_repo.create(search_event_data)
        await self.db_session.commit()

        return {
            "query": query,
            "total_results": len(results_with_offers),
            "execution_time_ms": execution_time_ms,
            "ai_router_used": ai_used,
            "marketplaces_searched": marketplaces,
        }

    async def close(self):
        await self.ai_router.close()
