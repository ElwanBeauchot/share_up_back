from fastapi import APIRouter
from app.db import devices_collection
from datetime import datetime, timedelta

router = APIRouter(prefix="/devices", tags=["devices"])

async def init_indexes():
    await devices_collection.create_index(
        [("geolocalisation", "2dsphere")]
    )


@router.post("/add_db")
async def add_device(device: dict):
    uuid = device.get("uuid")
    if not uuid:
        return {"error": "UUID manquant"}

    # Vérification minimale de la géolocalisation
    geo = device.get("geolocalisation", {})
    if "type" not in geo or "coordinates" not in geo:
        return {"error": "Format geolocalisation invalide"}

    result = await devices_collection.update_one(
        {"uuid": uuid},
        {"$set": device},
        upsert=True
    )

    if result.matched_count == 0 and result.upserted_id is not None:
        action = "inserted"
        _id = str(result.upserted_id)
    else:
        action = "updated"
        _id = None

    return {
        "action": action,
        "id": _id,
        "uuid": device.get("uuid"),
        "device_name": device.get("device_name"),
        "os": device.get("os"),
        "last_seen": device.get("last_seen"),
        "geolocalisation": device.get("geolocalisation"),
    }


@router.get("/read_db")
async def get_devices():
    devices = []
    async for d in devices_collection.find():
        coords = d.get("geolocalisation", {}).get("coordinates", [None, None])
        devices.append({
            "id": str(d["_id"]),
            "uuid": d.get("uuid"),
            "device_name": d.get("device_name"),
            "os": d.get("os"),
            "last_seen": d.get("last_seen"),
            "geolocalisation": {
                "type": d.get("geolocalisation", {}).get("type"),
                "coordinates": coords,
            },
            "longitude": coords[0],
            "latitude": coords[1],
        })
    return devices



@router.post("/nearby")
async def get_nearby_devices(data: dict):
    longitude = data.get("longitude")
    latitude = data.get("latitude")
    my_uuid = data.get("uuid")

    if longitude is None or latitude is None or my_uuid is None:
        return {"error": "longitude, latitude et uuid requis"}

    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

    query = {
        "geolocalisation": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "$maxDistance": 20,
            }
        },
        "last_seen": {
            "$gte": ten_minutes_ago.isoformat()
        },
        "uuid": {
            "$ne": my_uuid
        }
    }

    devices = []
    async for d in devices_collection.find(query):
        coords = d.get("geolocalisation", {}).get("coordinates", [None, None])
        devices.append({
            "id": str(d["_id"]),
            "uuid": d.get("uuid"),
            "device_name": d.get("device_name"),
            "os": d.get("os"),
            "last_seen": d.get("last_seen"),
            "longitude": coords[0],
            "latitude": coords[1],
        })

    return {
        "count": len(devices),
        "devices": devices
    }

