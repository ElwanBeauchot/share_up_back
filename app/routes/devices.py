from fastapi import APIRouter
from app.db import devices_collection

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("/add_db")
async def add_device(device: dict):
    uuid = device.get("uuid")
    if not uuid:
        return {"error": "UUID manquant"}

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
        "geolocalisation": device.get("geolocalisation")
    }

@router.get("/read_db")
async def get_devices():
    devices = []
    async for d in devices_collection.find():
        devices.append({
            "id": str(d["_id"]),
            "uuid": d.get("uuid"),
            "device_name": d.get("device_name"),
            "os": d.get("os"),
            "longitude": d.get("geolocalisation", {}).get("coordinates", [None, None])[0],
            "latitude": d.get("geolocalisation", {}).get("coordinates", [None, None])[1],
        })
    return devices

