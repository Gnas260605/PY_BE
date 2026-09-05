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
            return str(detail)
        if isinstance(detail, str):
            if detail in ERROR_MESSAGES:
                return ERROR_MESSAGES[detail]
            return detail
        elif isinstance(detail, list) and len(detail) > 0:
            first_err = detail[0]
            if isinstance(first_err, dict) and "msg" in first_err:
                return f"Lỗi dữ liệu: {first_err.get('loc', [''])[ -1 ]} - {first_err.get('msg')}"
            return str(first_err)
        
        if status_code == 401:
            return ERROR_MESSAGES["TOKEN_EXPIRED"]
        elif status_code == 403:
            return ERROR_MESSAGES["FORBIDDEN"]
        elif status_code == 404:
            return "Không tìm thấy dữ liệu yêu cầu."
        elif status_code >= 500:
            return ERROR_MESSAGES["SERVER_ERROR"]
        
        return "Có lỗi xảy ra trong quá trình xử lý."

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

                # Parse JSON
                try:
                    res_json = response.json()
                except Exception:
                    res_json = {}

                if not response.is_success:
                    detail = res_json.get("detail", "")
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

http_client = HttpClient()
