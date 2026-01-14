from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://elwanblb_db_user:3i4Ye1Whtw1PHLpX@shareup.e1ebvub.mongodb.net/?appName=ShareUp"

client = AsyncIOMotorClient(MONGO_URL)
db = client.share_up_db
devices_collection = db.devices
