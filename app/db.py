from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.mongo_url, tls=True)
db = client[settings.database_name]
devices_collection = db[settings.devices_collection_name]
