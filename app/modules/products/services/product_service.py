from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.marketplace.repositories.offer_repository import OfferRepository
from app.common.exceptions.exceptions import NotFoundException, ConflictException
from app.common.models.models import Product, Offer


class ProductService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.product_repo = ProductRepository(db_session)
        self.offer_repo = OfferRepository(db_session)

    async def create_product(self, product_data: dict) -> Product:
        existing = await self.product_repo.get_by_sku(product_data["sku"])
        if existing:
            raise ConflictException("Product with this SKU already exists")

        product = await self.product_repo.create(product_data)
        await self.db_session.commit()
        return product

    async def get_product(self, product_id: int) -> Product:
        product = await self.product_repo.get_by_sku(product_id)
        if not product:
            raise NotFoundException("Product not found")
        return product

    async def get_product_by_sku(self, sku: str) -> Product:
        product = await self.product_repo.get_by_sku(sku)
        if not product:
            raise NotFoundException("Product not found")
        return product

    async def search_products(self, query: str, skip: int = 0, limit: int = 20) -> List[Product]:
        return await self.product_repo.search(query, skip, limit)

    async def get_products_by_category(self, category: str, skip: int = 0, limit: int = 20) -> List[Product]:
        return await self.product_repo.get_by_category(category, skip, limit)

    async def get_best_prices(self, product_id: int) -> Dict:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product not found")
        
        offers = await self.offer_repo.get_by_product(product_id)
        cheapest = await self.offer_repo.get_cheapest_offer(product_id)

        return {
            "product_id": product_id,
            "product_name": product.name,
            "cheapest_offer": {
                "marketplace": cheapest.marketplace,
                "price": cheapest.price,
                "url": cheapest.url,
            } if cheapest else None
        }

    async def update_product(self, product_id: int, update_data: dict) -> Product:
        product = await self.product_repo.update(product_id, update_data)
        if not product:
            raise NotFoundException("Product not found")
        await self.db_session.commit()
        return product
