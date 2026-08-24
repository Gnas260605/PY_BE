from __future__ import annotations

from pydantic import ValidationError

from fastapi import APIRouter, Depends, Query, status

from app.core.auth import get_current_user, require_roles
from app.core.errors import BadRequestError
from app.devices.schemas import (
    CreateDeviceRequest,
    DeviceListQuery,
    DeviceResponse,
    UpdateDeviceRequest,
)
from app.devices.service import (
    create_device,
    get_device_detail,
    list_devices,
    update_device,
)


router = APIRouter()


@router.get(
    "/devices",
    response_model=list[DeviceResponse],
    dependencies=[Depends(require_roles("ADMIN", "TECHNICIAN"))],
)
def list_devices_route(
    status_value: str | None = Query(default=None, alias="status"),
    type_value: str | None = Query(default=None, alias="type"),
    keyword: str | None = Query(default=None),
) -> list[dict]:
    try:
        query = DeviceListQuery(status=status_value, type=type_value, keyword=keyword)
    except ValidationError as exc:
        raise BadRequestError("INVALID_INPUT") from exc
    return list_devices(query)


@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def create_device_route(payload: CreateDeviceRequest) -> dict:
    return create_device(payload)


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    dependencies=[Depends(require_roles("ADMIN", "TECHNICIAN"))],
)
def get_device_route(device_id: int) -> dict:
    return get_device_detail(device_id)


@router.patch(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    dependencies=[Depends(require_roles("ADMIN", "TECHNICIAN"))],
)
def update_device_route(
    device_id: int,
    payload: UpdateDeviceRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return update_device(device_id, payload, current_user=current_user)
