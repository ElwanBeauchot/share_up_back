from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: list[float] = Field(..., min_length=2, max_length=2)  # [longitude, latitude]


class DeviceBase(BaseModel):
    uuid: str
    device_name: str
    os: str
    geolocalisation: GeoPoint
    last_seen: Optional[datetime] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass


class DeviceInDB(DeviceBase):
    id: str


class DeviceResponse(DeviceInDB):
    longitude: float
    latitude: float

    @classmethod
    def from_db(cls, data: dict):
        coords = data.get("geolocalisation", {}).get("coordinates", [0.0, 0.0])
        return cls(
            id=str(data["_id"]),
            uuid=data["uuid"],
            device_name=data["device_name"],
            os=data["os"],
            geolocalisation=data["geolocalisation"],
            last_seen=data.get("last_seen"),
            longitude=coords[0],
            latitude=coords[1]
        )


class NearbyRequest(BaseModel):
    longitude: float
    latitude: float
    uuid: str


class NearbyResponse(BaseModel):
    count: int
    devices: List[DeviceResponse]
