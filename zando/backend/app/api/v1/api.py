from fastapi import APIRouter

from .endpoints import dna, analysis, reports, cache, admin

api_router = APIRouter()

# Include all API routers
api_router.include_router(dna.router, prefix="/dna", tags=["dna"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Additional routers can be added here as they are implemented
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(genetics.router, prefix="/genetics", tags=["genetics"])