import pytest
from datetime import datetime, timezone, timedelta
from app.services.device_service import create_or_update_device, get_nearby_devices
from app.schemas import DeviceCreate, GeoPoint, NearbyRequest
import app.services.device_service as device_service

# test creqte device

@pytest.mark.asyncio
async def test_create_device_insertion(devices_collection, monkeypatch):
    """Test de creation d'un nouveau device (cas d'insertion)"""
    monkeypatch.setattr(device_service, "devices_collection", devices_collection)

    device = DeviceCreate(
        uuid="123",
        device_name="iPhone",
        os="iOS",
        last_seen=datetime.now(timezone.utc),
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )

    result = await create_or_update_device(device)

    # Verifications pour une insertion
    assert result["action"] == "inserted"
    assert result["id"] is not None, "L'ID du device insere ne doit pas être None"
    assert result["uuid"] == "123"
    assert result["device_name"] == "iPhone"
    assert result["os"] == "iOS"
    assert result["last_seen"] == device.last_seen
    assert result["geolocalisation"]["type"] == "Point"
    assert result["geolocalisation"]["coordinates"] == [2.35, 48.85]


@pytest.mark.asyncio
async def test_update_device(devices_collection, monkeypatch):
    """Test de mise à jour d'un device existant (cas d'update)"""
    monkeypatch.setattr(device_service, "devices_collection", devices_collection)

    # Creer un device en premier
    device1 = DeviceCreate(
        uuid="456",
        device_name="iPhone",
        os="iOS 15",
        last_seen=datetime.now(timezone.utc),
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(device1)

    # Mettre à jour le même device
    device2 = DeviceCreate(
        uuid="456",
        device_name="iPhone 14",  # Change
        os="iOS 16",  # Change
        last_seen=datetime.now(timezone.utc),
        geolocalisation=GeoPoint(coordinates=[2.40, 48.90])  # Change
    )
    result = await create_or_update_device(device2)

    # Verifications pour une mise à jour
    assert result["action"] == "updated"
    assert result["id"] is None, "L'ID doit être None pour une update"
    assert result["uuid"] == "456"
    assert result["device_name"] == "iPhone 14"
    assert result["os"] == "iOS 16"
    assert result["geolocalisation"]["coordinates"] == [2.40, 48.90]

    # Verifier que le device en base a bien ete mis à jour
    updated_device = await devices_collection.find_one({"uuid": "456"})
    assert updated_device["device_name"] == "iPhone 14"
    assert updated_device["os"] == "iOS 16"


# test get nearby devices


@pytest.mark.asyncio
async def test_get_nearby_devices_response_structure(devices_collection, monkeypatch):
    """Test que la structure de reponse est correcte"""
    monkeypatch.setattr(device_service, "devices_collection", devices_collection)

    current_time = datetime.now().replace(microsecond=0)

    # Creer un device de reference
    reference_device = DeviceCreate(
        uuid="ref_device",
        device_name="Reference Device",
        os="iOS",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(reference_device)

    # Creer un device à proximite
    nearby_device = DeviceCreate(
        uuid="nearby_device",
        device_name="Nearby Device",
        os="iOS",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.3501, 48.8501])
    )
    await create_or_update_device(nearby_device)

    # Chercher les devices à proximite
    request = NearbyRequest(longitude=2.35, latitude=48.85, uuid="ref_device")
    results = await get_nearby_devices(request)

    # Verifier la structure de la reponse
    assert len(results) == 1
    device = results[0]

    assert hasattr(device, "id")
    assert hasattr(device, "uuid")
    assert hasattr(device, "device_name")
    assert hasattr(device, "os")
    assert hasattr(device, "geolocalisation")
    assert hasattr(device, "last_seen")
    assert hasattr(device, "longitude")
    assert hasattr(device, "latitude")

    assert device.uuid == "nearby_device"
    assert device.device_name == "Nearby Device"
    assert device.os == "iOS"
    assert device.longitude == 2.3501
    assert device.latitude == 48.8501
    assert device.last_seen == current_time

@pytest.mark.asyncio
async def test_get_nearby_devices_basic(devices_collection, monkeypatch):
    """Test de recherche de devices à proximite"""
    monkeypatch.setattr(device_service, "devices_collection", devices_collection)

    current_time = datetime.now(timezone.utc)

    # Creer un device de reference
    reference_device = DeviceCreate(
        uuid="ref_device",
        device_name="Reference Device",
        os="iOS",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(reference_device)

    # Creer un device à proximite
    nearby_device = DeviceCreate(
        uuid="nearby_device",
        device_name="Nearby Device",
        os="Android",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(nearby_device)

    # Chercher les devices à proximite
    request = NearbyRequest(longitude=2.35, latitude=48.85, uuid="ref_device")
    results = await get_nearby_devices(request)

    # Le device à proximite doit être trouve
    assert len(results) == 1
    assert results[0].uuid == "nearby_device"
    assert results[0].device_name == "Nearby Device"


@pytest.mark.asyncio
async def test_get_nearby_devices_time_filter(devices_collection, monkeypatch):
    """Test du filtre de temps (10 dernières minutes)"""
    monkeypatch.setattr(device_service, "devices_collection", devices_collection)

    current_time = datetime.now(timezone.utc)
    old_time = current_time - timedelta(minutes=15)  # Plus de 10 minutes

    # Creer un device de reference
    reference_device = DeviceCreate(
        uuid="ref_device",
        device_name="Reference Device",
        os="iOS",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(reference_device)

    # Device à proximite mqis trop ancien
    old_device = DeviceCreate(
        uuid="old_device",
        device_name="Old Device",
        os="iOS",
        last_seen=old_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(old_device)

    # Device a proximite et recent
    recent_device = DeviceCreate(
        uuid="recent_device",
        device_name="Recent Device",
        os="Android",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(recent_device)

    # Chercher les devices à proximite
    request = NearbyRequest(longitude=2.35, latitude=48.85, uuid="ref_device")
    results = await get_nearby_devices(request)

    # Seul le device recent doit être trouve
    assert len(results) == 1
    assert results[0].uuid == "recent_device"


@pytest.mark.asyncio
async def test_get_nearby_devices_distance_filter(devices_collection, monkeypatch):
    """Test du filtre de distance (20 mètres maximum)"""
    monkeypatch.setattr(device_service, "devices_collection", devices_collection)

    current_time = datetime.now(timezone.utc)

    # Creer un device de reference
    reference_device = DeviceCreate(
        uuid="ref_device",
        device_name="Reference Device",
        os="iOS",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])
    )
    await create_or_update_device(reference_device)

    # Device loin (> 20m)
    far_device = DeviceCreate(
        uuid="far_device",
        device_name="Far Device",
        os="iOS",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.36, 48.86])  # loin
    )
    await create_or_update_device(far_device)

    # Device proche (< 20m)
    close_device = DeviceCreate(
        uuid="close_device",
        device_name="Close Device",
        os="Android",
        last_seen=current_time,
        geolocalisation=GeoPoint(coordinates=[2.35, 48.85])  # proche
    )
    await create_or_update_device(close_device)

    # Chercher les devices à proximite
    request = NearbyRequest(longitude=2.35, latitude=48.85, uuid="ref_device")
    results = await get_nearby_devices(request)

    # Seul le device proche doit être trouve
    assert len(results) == 1
    assert results[0].uuid == "close_device"

