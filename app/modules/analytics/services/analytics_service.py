from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from datetime import datetime, timedelta
from app.modules.analytics.repositories.search_event_repository import SearchEventRepository
from app.modules.auth.repositories.user_repository import UserRepository
from app.common.exceptions.exceptions import NotFoundException


class AnalyticsService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.search_event_repo = SearchEventRepository(db_session)
        self.user_repo = UserRepository(db_session)

    async def get_user_analytics(self, user_id: int, days: int = 30) -> Dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()

        searches = await self.search_event_repo.get_user_searches(user_id, skip=0, limit=1000)

        total_searches = len(searches)
        ai_router_used = sum(1 for s in searches if s.ai_router_used)
        total_results = sum(s.results_count for s in searches)

        queries = {}
        for search in searches:
            queries[search.query] = queries.get(search.query, 0) + 1

        popular_queries = sorted(queries.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "user_id": user_id,
            "date_range": {
                "start": start_date,
                "end": end_date,
                "days": days
            },
            "total_searches": total_searches,
            "total_results_found": total_results,
            "ai_router_usage": {
                "used": ai_router_used,
                "percentage": round((ai_router_used / total_searches * 100) if total_searches > 0 else 0, 1)
            },
            "popular_queries": [{"query": q, "count": c} for q, c in popular_queries],
        }

    async def get_platform_analytics(self, days: int = 30) -> Dict:
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()

        popular_queries = await self.search_event_repo.get_popular_queries(limit=20)

        return {
            "date_range": {
                "start": start_date,
                "end": end_date,
                "days": days
            },
            "popular_queries": popular_queries,
        }

    async def get_search_trends(self, limit: int = 10) -> List[Dict]:
        return await self.search_event_repo.get_popular_queries(limit=limit)
