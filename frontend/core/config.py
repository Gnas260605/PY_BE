import os

class FrontendConfig:
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")
    APP_TITLE: str = "CS466 Helpdesk Portal"
    PORT: int = int(os.getenv("FRONTEND_PORT", "8500"))
    HOST: str = os.getenv("FRONTEND_HOST", "127.0.0.1")
    REQUEST_TIMEOUT: float = 15.0
    CACHE_TTL_SECONDS: int = int(os.getenv("FRONTEND_CACHE_TTL_SECONDS", "60"))
    STORAGE_SECRET: str = os.getenv("FRONTEND_STORAGE_SECRET", "cs466-helpdesk-dev-secret")

config = FrontendConfig()
