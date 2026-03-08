from typing import List, Dict, Optional
import httpx
import asyncio
from app.core.config.settings import settings


class BaseScraper:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10)
        self.marketplace_name = ""

    async def search(self, query: str, limit: int = 20) -> List[Dict]:
        raise NotImplementedError

    async def get_product(self, product_id: str) -> Optional[Dict]:
        raise NotImplementedError

    async def close(self):
        await self.client.aclose()


class WildberriesScraper(BaseScraper):
    def __init__(self):
        super().__init__(settings.wildberries_api_key)
        self.marketplace_name = "wildberries"

    async def search(self, query: str, limit: int = 20) -> List[Dict]:
        return [
            {
                "id": f"wb_{i}",
                "name": f"{query} - Wildberries",
                "price": 1000 + (i * 100),
                "rating": 4.5,
                "reviews_count": 100 + i,
                "in_stock": True,
                "url": f"https://www.wildberries.ru/catalog/{i}",
            }
            for i in range(1, min(limit + 1, 21))
        ]

    async def get_product(self, product_id: str) -> Optional[Dict]:
        return {
            "id": product_id,
            "name": "Wildberries Product",
            "price": 2500,
            "rating": 4.7,
            "reviews_count": 250,
        }


class OzonScraper(BaseScraper):
    def __init__(self):
        super().__init__(settings.ozon_api_key)
        self.marketplace_name = "ozon"

    async def search(self, query: str, limit: int = 20) -> List[Dict]:
        return [
            {
                "id": f"ozon_{i}",
                "name": f"{query} - Ozon",
                "price": 900 + (i * 80),
                "rating": 4.3,
                "reviews_count": 80 + i,
                "in_stock": True,
                "url": f"https://www.ozon.ru/product/{i}/",
            }
            for i in range(1, min(limit + 1, 21))
        ]

    async def get_product(self, product_id: str) -> Optional[Dict]:
        return {
            "id": product_id,
            "name": "Ozon Product",
            "price": 2200,
            "rating": 4.6,
            "reviews_count": 200,
        }


class AvitoScraper(BaseScraper):
    def __init__(self):
        super().__init__(settings.avito_api_key)
        self.marketplace_name = "avito"

    async def search(self, query: str, limit: int = 20) -> List[Dict]:
        return [
            {
                "id": f"avito_{i}",
                "name": f"{query} - Avito",
                "price": 800 + (i * 70),
                "rating": 4.4,
                "reviews_count": 60 + i,
                "in_stock": True,
                "url": f"https://www.avito.ru/item/{i}",
            }
            for i in range(1, min(limit + 1, 21))
        ]

    async def get_product(self, product_id: str) -> Optional[Dict]:
        return {
            "id": product_id,
            "name": "Avito Product",
            "price": 1800,
            "rating": 4.5,
            "reviews_count": 150,
        }


class MarketplaceService:
    def __init__(self):
        self.scrapers = {
            "wildberries": WildberriesScraper(),
            "ozon": OzonScraper(),
            "avito": AvitoScraper(),
        }

    async def search_all_marketplaces(
        self, query: str, marketplaces: List[str], limit: int = 20
    ) -> Dict[str, List[Dict]]:
        tasks = []
        selected_scrapers = {}

        for marketplace in marketplaces:
            if marketplace in self.scrapers:
                scraper = self.scrapers[marketplace]
                selected_scrapers[marketplace] = scraper
                tasks.append(scraper.search(query, limit))

        if not tasks:
            return {}

        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for marketplace, result in zip(selected_scrapers.keys(), results):
            if isinstance(result, Exception):
                output[marketplace] = []
            else:
                output[marketplace] = result

        return output

    async def search_marketplace(self, marketplace: str, query: str, limit: int = 20) -> List[Dict]:
        if marketplace not in self.scrapers:
            raise ValueError(f"Unknown marketplace: {marketplace}")
        scraper = self.scrapers[marketplace]
        return await scraper.search(query, limit)

    async def close(self):
        for scraper in self.scrapers.values():
            await scraper.close()
