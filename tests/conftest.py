
import pytest
import asyncio

import pytest_asyncio
from testcontainers.mongodb import MongoDbContainer
from motor.motor_asyncio import AsyncIOMotorClient
import os

# evite de lancer ryuk, probleme avec fedora
# ryuk sert nettoyer les containers
os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"

# gerer test asynchrone
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop

    loop.close()

# permet de creer un container mongodb
@pytest.fixture(scope="session")
def mongo_container():
    mongo = MongoDbContainer("mongo:6.0")

    mongo.start()

    yield mongo

    mongo.stop()

# permet de creer un client asynchrone mongodb
@pytest_asyncio.fixture
async def mongo_client(mongo_container):
    client = AsyncIOMotorClient(mongo_container.get_connection_url())

    yield client

    client.close()


# permet d'acceder a la collection devices
@pytest_asyncio.fixture
async def devices_collection(mongo_client):
    db = mongo_client["test_db"]
    collection = db["devices"]

    await collection.create_index([("geolocalisation", "2dsphere")])

    yield collection

    await collection.delete_many({})