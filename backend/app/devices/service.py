from __future__ import annotations

import logging

import mysql.connector

from app.core.errors import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.db.connection import connection_scope
from app.devices import repository
from app.devices.schemas import (
    CreateDeviceRequest,
    DeviceListQuery,
    DeviceResponse,
    UpdateDeviceRequest,
)


logger = logging.getLogger(__name__)

TECHNICIAN_ALLOWED_FIELDS = {"trang_thai", "mo_ta"}
ADMIN_ALLOWED_FIELDS = {
    "ma_thiet_bi",
    "ten_thiet_bi",
    "loai_thiet_bi",
    "vi_tri",
    "trang_thai",
    "mo_ta",
}


def list_devices(query: DeviceListQuery) -> list[dict]:
    with connection_scope() as connection:
        return repository.list_devices(
            connection,
            status=query.status,
            device_type=query.type,
            keyword=query.keyword,
        )


def create_device(payload: CreateDeviceRequest) -> dict:
    with connection_scope() as connection:
        duplicate = repository.find_duplicate_device_code(
            connection,
            ma_thiet_bi=payload.ma_thiet_bi,
        )
        if duplicate is not None:
            raise ConflictError("DUPLICATE_DEVICE_CODE")

        try:
            device_id = repository.create_device(
                connection,
                ma_thiet_bi=payload.ma_thiet_bi,
                ten_thiet_bi=payload.ten_thiet_bi,
                loai_thiet_bi=payload.loai_thiet_bi,
                vi_tri=payload.vi_tri,
                trang_thai=payload.trang_thai,
                mo_ta=payload.mo_ta,
            )
            connection.commit()
        except mysql.connector.IntegrityError as exc:
            connection.rollback()
            raise ConflictError("DUPLICATE_DEVICE_CODE") from exc
        except Exception:
            connection.rollback()
            raise
        created_device = repository.get_device_by_id(connection, device_id)

    logger.info("DEVICE_CREATED device_id=%s code=%s", device_id, payload.ma_thiet_bi)

    if created_device is None:
        raise NotFoundError("DEVICE_NOT_FOUND")
    return created_device


def get_device_detail(device_id: int) -> dict:
    with connection_scope() as connection:
        device = repository.get_device_by_id(connection, device_id)
    if device is None:
        raise NotFoundError("DEVICE_NOT_FOUND")
    return device


def update_device(
    device_id: int,
    payload: UpdateDeviceRequest,
    *,
    current_user: dict,
) -> dict:
    requested_updates = payload.model_dump(exclude_none=True)
    if not requested_updates:
        raise BadRequestError("INVALID_INPUT")

    allowed_fields = ADMIN_ALLOWED_FIELDS
    if current_user["vai_tro"] == "TECHNICIAN":
        allowed_fields = TECHNICIAN_ALLOWED_FIELDS
        disallowed_fields = set(requested_updates) - TECHNICIAN_ALLOWED_FIELDS
        if disallowed_fields:
            raise ForbiddenError("FORBIDDEN")

    updates = {
        key: value for key, value in requested_updates.items() if key in allowed_fields
    }
    if not updates:
        raise BadRequestError("INVALID_INPUT")

    with connection_scope() as connection:
        existing_device = repository.get_device_by_id(connection, device_id)
        if existing_device is None:
            raise NotFoundError("DEVICE_NOT_FOUND")

        new_code = updates.get("ma_thiet_bi")
        if new_code is not None:
            duplicate = repository.find_duplicate_device_code(
                connection,
                ma_thiet_bi=new_code,
                exclude_device_id=device_id,
            )
            if duplicate is not None:
                raise ConflictError("DUPLICATE_DEVICE_CODE")

        try:
            repository.update_device(connection, device_id, updates)
            connection.commit()
        except mysql.connector.IntegrityError as exc:
            connection.rollback()
            raise ConflictError("DUPLICATE_DEVICE_CODE") from exc
        except Exception:
            connection.rollback()
            raise
        updated_device = repository.get_device_by_id(connection, device_id)

    logger.info(
        "DEVICE_UPDATED device_id=%s role=%s fields=%s",
        device_id,
        current_user["vai_tro"],
        ",".join(sorted(updates.keys())),
    )

    if updated_device is None:
        raise NotFoundError("DEVICE_NOT_FOUND")
    return updated_device
