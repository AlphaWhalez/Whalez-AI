from fastapi import APIRouter
from .monitor import tls_status


def attach_tls_routes(router: APIRouter):
    @router.get("/health/tls")
    def health_tls():
        return tls_status()
