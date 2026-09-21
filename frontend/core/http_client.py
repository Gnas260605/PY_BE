from typing import Optional, Dict, Any, Union
import httpx
from core.config import config
from core.auth_context import auth_context
from core.constants import ERROR_MESSAGES

class ApiException(Exception):
    def __init__(self, message: str, status_code: int = 400, detail_code: str = ""):
        self.message = message
        self.status_code = status_code
        self.detail_code = detail_code
        super().__init__(self.message)

class HttpClient:
    @staticmethod
    def _translate_error(detail: Any, status_code: int) -> str:
        if isinstance(detail, dict):
            nested_detail = detail.get("detail")
            if nested_detail:
                return HttpClient._translate_error(nested_detail, status_code)
            errors = detail.get("errors")
            if isinstance(errors, list) and len(errors) > 0:
                first_err = errors[0]
                if isinstance(first_err, dict) and "msg" in first_err:
                    field = first_err.get("loc", [""])[-1]
                    return f"Dữ liệu không hợp lệ tại trường '{field}': {first_err.get('msg')}"
            return str(detail)
        
        if isinstance(detail, list) and len(detail) > 0:
            first_err = detail[0]
            if isinstance(first_err, dict) and "msg" in first_err:
                field = first_err.get("loc", [""])[-1]
                return f"Dữ liệu không hợp lệ tại trường '{field}': {first_err.get('msg')}"
            return HttpClient._translate_error(str(first_err), status_code)

        if isinstance(detail, str):
            clean = detail.strip().upper()
            if clean in ERROR_MESSAGES:
                return ERROR_MESSAGES[clean]
            # Match if key is part of string
            for key, val in ERROR_MESSAGES.items():
                if key in clean:
                    return val
            if detail.strip():
                return detail.strip()
        
        if status_code == 401:
            return ERROR_MESSAGES.get("TOKEN_EXPIRED", "Phiên đăng nhập đã hết hạn hoặc thông tin không chính xác.")
        elif status_code == 403:
            return ERROR_MESSAGES.get("FORBIDDEN", "Bạn không có quyền thực hiện thao tác này.")
        elif status_code == 404:
            return "Không tìm thấy dữ liệu yêu cầu trên hệ thống."
        elif status_code == 409:
            return "Dữ liệu bị trùng lặp hoặc xung đột với bản ghi hiện có."
        elif status_code == 429:
            return ERROR_MESSAGES.get("RATE_LIMIT_EXCEEDED", "Bạn đã gửi yêu cầu quá nhanh. Vui lòng đợi 1 phút!")
        elif status_code >= 500:
            return ERROR_MESSAGES.get("SERVER_ERROR", "Lỗi máy chủ nội bộ. Vui lòng thử lại sau!")
        
        return "Có lỗi xảy ra trong quá trình xử lý yêu cầu."

    @classmethod
    async def request(
        cls,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth_required: bool = True
    ) -> Any:
        url = f"{config.API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json"}

        token = auth_context.get_token()
        if auth_required and token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    json=data if data is not None else None,
                    params=params,
                    headers=headers
                )

                # Handle 204 No Content
                if response.status_code == 204:
                    return None

                # Parse JSON or Raw Text
                is_json = "application/json" in response.headers.get("content-type", "")
                if is_json:
                    try:
                        res_json = response.json()
                    except Exception:
                        res_json = {}
                else:
                    res_json = response.text

                if not response.is_success:
                    detail = res_json.get("detail", "") if isinstance(res_json, dict) else str(res_json)
                    friendly_msg = cls._translate_error(detail, response.status_code)
                    if response.status_code == 401:
                        auth_context.clear_session()
                    raise ApiException(
                        message=friendly_msg,
                        status_code=response.status_code,
                        detail_code=str(detail)
                    )

                return res_json

        except httpx.ConnectError:
            raise ApiException(
                message=ERROR_MESSAGES["CONNECTION_ERROR"],
                status_code=503,
                detail_code="CONNECTION_REFUSED"
            )
        except httpx.TimeoutException:
            raise ApiException(
                message="Hết thời gian chờ phản hồi từ máy chủ (Timeout). Vui lòng thử lại!",
                status_code=504,
                detail_code="TIMEOUT"
            )
        except ApiException:
            raise
        except Exception as e:
            raise ApiException(
                message=f"Lỗi không xác định: {str(e)}",
                status_code=500,
                detail_code="UNKNOWN"
            )

    @classmethod
    async def get(cls, endpoint: str, params: Optional[Dict[str, Any]] = None, auth_required: bool = True):
        return await cls.request("GET", endpoint, params=params, auth_required=auth_required)

    @classmethod
    async def post(cls, endpoint: str, data: Optional[Dict[str, Any]] = None, auth_required: bool = True):
        return await cls.request("POST", endpoint, data=data, auth_required=auth_required)

    @classmethod
    async def patch(cls, endpoint: str, data: Optional[Dict[str, Any]] = None, auth_required: bool = True):
        return await cls.request("PATCH", endpoint, data=data, auth_required=auth_required)

    @classmethod
    async def delete(cls, endpoint: str, auth_required: bool = True):
        return await cls.request("DELETE", endpoint, auth_required=auth_required)

    @classmethod
    async def download_file(cls, endpoint: str, params: Optional[Dict[str, Any]] = None, auth_required: bool = True) -> bytes:
        url = f"{config.API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {}
        token = auth_context.get_token()
        if auth_required and token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params, headers=headers)
                if not response.is_success:
                    if response.status_code == 401:
                        auth_context.clear_session()
                    raise ApiException(f"Lỗi tải file (HTTP {response.status_code})", response.status_code)
                return response.content
        except httpx.ConnectError:
            raise ApiException(ERROR_MESSAGES["CONNECTION_ERROR"], 503)
        except Exception as e:
            if isinstance(e, ApiException):
                raise
            raise ApiException(f"Lỗi tải file: {str(e)}", 500)

    @classmethod
    async def upload(cls, endpoint: str, file_name: str, file_data: bytes, content_type: str, auth_required: bool = True):
        url = f"{config.API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {}
        token = auth_context.get_token()
        if auth_required and token:
            headers["Authorization"] = f"Bearer {token}"

        files = {"file": (file_name, file_data, content_type)}
        try:
            async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
                response = await client.post(url, headers=headers, files=files)
                
                is_json = "application/json" in response.headers.get("content-type", "")
                if is_json:
                    try:
                        res_json = response.json()
                    except Exception:
                        res_json = {}
                else:
                    res_json = response.text

                if not response.is_success:
                    detail = res_json.get("detail", "") if isinstance(res_json, dict) else str(res_json)
                    friendly_msg = cls._translate_error(detail, response.status_code)
                    if response.status_code == 401:
                        auth_context.clear_session()
                    raise ApiException(
                        message=friendly_msg,
                        status_code=response.status_code,
                        detail_code=str(detail)
                    )
                return res_json
        except httpx.ConnectError:
            raise ApiException(
                message=ERROR_MESSAGES["CONNECTION_ERROR"],
                status_code=503,
                detail_code="CONNECTION_REFUSED"
            )
        except httpx.TimeoutException:
            raise ApiException(
                message="Hết thời gian chờ phản hồi từ máy chủ (Timeout). Vui lòng thử lại!",
                status_code=504,
                detail_code="TIMEOUT"
            )
        except ApiException:
            raise
        except Exception as e:
            raise ApiException(
                message=f"Lỗi không xác định: {str(e)}",
                status_code=500,
                detail_code="UNKNOWN"
            )

http_client = HttpClient()
