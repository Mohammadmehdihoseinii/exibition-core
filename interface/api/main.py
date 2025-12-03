from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
# ----------------- Import Your Routers -----------------
from interface.api.users.users import router as auth_router
from interface.api.exhibition.exhibition import router as exhibition_router
from interface.api.company.company import router as company_router
from interface.api.organizer.organizer import router as organizer_router
from interface.api.favorite.favorite import router as favorite_router
from interface.api.product.product import router as product_router

# ----------------- FastAPI App -----------------
app = FastAPI(
    title="exibition API",
    version="0.5.0",
    description="Exchange API with WebSocket, EventBus, server status, and full docs",
    docs_url="/docs",
    redoc_url=None
)

# ----------------- Middleware -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{os.getenv("apiPort")}",f"http://localhost:{os.getenv("sitePort")}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ----------------- Mock Background Task -----------------
async def generate_price_updates():
    """
    اگر در پروژه اصلی WebSocket یا EventBus دارید،
    اینجا باید به سیستم اصلی وصل شود.

    فعلاً یک وظیفه خالی برای جلوگیری از خطا
    """
    while True:
        await asyncio.sleep(5)
        # اینجا می‌تونی لاگ بزاری یا داده تست بفرستی
        # print("Generating mock price data...")


# ----------------- Startup Tasks -----------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generate_price_updates())


# ----------------- Pydantic Models -----------------
class HealthResponse(BaseModel):
    status: str
    message: str


class RouteInfo(BaseModel):
    path: str
    methods: list[str]
    name: str


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    echo: str


# ----------------- Include Routers -----------------
app.include_router(auth_router)
app.include_router(exhibition_router)
app.include_router(company_router)
app.include_router(organizer_router)
app.include_router(favorite_router)
app.include_router(product_router)

# ----------------- Endpoints -----------------
@app.get("/", summary="صفحه اصلی")
def root():
    """
    صفحه اصلی API با وضعیت سرور و لینک docs
    """
    return {
        "message": "Exibition API is running",
        "version": app.version,
        "status": "healthy",
        "docs": "/docs",
        # "features": [
        #     "WebSocket updates",
        #     "EventBus",
        #     "Mock price data",
        #     "Order simulation"
        # ]
    }


@app.get("/health", response_model=HealthResponse, summary="وضعیت سلامت سرور")
def health_check():
    """
    بررسی وضعیت سلامت سرور
    """
    return {"status": "healthy", "message": "Server is running"}


@app.get("/routes", response_model=list[RouteInfo], summary="لیست مسیرهای REST و WebSocket")
def list_routes():
    """
    نمایش تمام مسیرهای REST و WebSocket
    """
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return routes


@app.post("/echo", response_model=EchoResponse, summary="نمونه endpoint برای تست مدل‌ها")
def echo(req: EchoRequest):
    """
    یک مسیر تستی برای بررسی Swagger UI
    """
    return {"echo": req.message}


# ----------------- Run Server -----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("apiPort"), reload=True)
