from app.db import devices_collection
from app.schemas import DeviceCreate, DeviceResponse, NearbyRequest
from datetime import datetime, timedelta, UTC
from typing import List
from app.logging_config import logger


async def create_or_update_device(device: DeviceCreate) -> dict:
    logger.info(f"Creating or updating device with UUID: {device.uuid}")
    result = await devices_collection.update_one(
        {"uuid": device.uuid},
        {"$set": device.model_dump()},
        upsert=True
    )

    if result.matched_count == 0 and result.upserted_id is not None:
        action = "inserted"
        _id = str(result.upserted_id)
        logger.info(f"Device inserted with ID: {_id}")
    else:
        action = "updated"
        _id = None
        logger.info(f"Device updated for UUID: {device.uuid}")

    return {
        "action": action,
        "id": _id,
        "uuid": device.uuid,
        "device_name": device.device_name,
        "os": device.os,
        "last_seen": device.last_seen,
        "geolocalisation": device.geolocalisation.model_dump(),
    }


async def get_all_devices() -> List[DeviceResponse]:
    logger.info("Retrieving all devices")
    devices = []
    async for d in devices_collection.find():
        devices.append(DeviceResponse.from_db(d))
    logger.info(f"Retrieved {len(devices)} devices")
    return devices


async def get_nearby_devices(request: NearbyRequest) -> List[DeviceResponse]:
    logger.info(f"Searching nearby devices for UUID: {request.uuid} at ({request.longitude}, {request.latitude})")
    ten_minutes_ago = datetime.now(UTC) - timedelta(minutes=10)

    query = {
        "geolocalisation": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [request.longitude, request.latitude],
                },
                "$maxDistance": 20,
            }
        },
        "last_seen": {
            "$gte": datetime.now(UTC) - timedelta(minutes=10)
        },
        "uuid": {
            "$ne": request.uuid
        }
    }

    devices = []
    async for d in devices_collection.find(query):
        devices.append(DeviceResponse.from_db(d))
    logger.info(f"Found {len(devices)} nearby devices")
    return devices
