"""Application entry point for Iron Việt Fitness API."""
from fastapi import FastAPI
from .core import init_db
from .routers import catalog, members, orders, subscriptions, consultations, requests, staff, payments

app = FastAPI(
    title="Iron Việt Fitness — API nghiệp vụ giả lập",
    version="1.1.0",
    description="API mô phỏng nghiệp vụ phòng gym, dùng knowledge_base của Iron Việt Fitness. Dữ liệu hội viên và giao dịch là dữ liệu giả lập.",
)

for module in (catalog, members, orders, subscriptions, consultations, requests, staff, payments):
    app.include_router(module.router)

@app.on_event("startup")
def startup() -> None:
    init_db()
