import pytest
import asyncio

import pytest_asyncio
from testcontainers.mongodb import MongoDbContainer
from motor.motor_asyncio import AsyncIOMotorClient
import os

os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def mongo_container():
    mongo = MongoDbContainer("mongo:6.0")
    mongo.start()
    yield mongo
    mongo.stop()


@pytest_asyncio.fixture
async def mongo_client(mongo_container):
    client = AsyncIOMotorClient(mongo_container.get_connection_url())
    yield client
    client.close()


@pytest_asyncio.fixture
async def devices_collection(mongo_client):
    db = mongo_client["test_db"]
    collection = db["devices"]

    # creqtion de l'index geospatial
    await collection.create_index([("geolocalisation", "2dsphere")])

    yield collection

    await collection.delete_many({})