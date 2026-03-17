from fastapi import APIRouter
from app.schemas import DeviceCreate, DeviceResponse, NearbyRequest, NearbyResponse
from app.services.device_service import create_or_update_device, get_all_devices, get_nearby_devices
from typing import List

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("/add_db")
async def add_device(device: DeviceCreate):
    uuid = device.uuid
    if not uuid:
        return {"error": "UUID manquant"}

    # Vérification minimale de la géolocalisation
    geo = device.geolocalisation
    if geo.type != "Point" or len(geo.coordinates) != 2:
        return {"error": "Format geolocalisation invalide"}

    result = await create_or_update_device(device)
    return result


@router.get("/read_db", response_model=List[DeviceResponse])
async def get_devices():
    devices = await get_all_devices()
    return devices


@router.post("/nearby", response_model=NearbyResponse)
async def get_nearby_devices_endpoint(data: NearbyRequest):
    devices = await get_nearby_devices(data)
    return NearbyResponse(count=len(devices), devices=devices)
