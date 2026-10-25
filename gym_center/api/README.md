# Iron Việt Fitness — FastAPI

API nghiệp vụ giả lập cho phòng gym, được tổ chức theo cấu trúc module tương tự `moc-mien-florist/api`, nhưng tùy biến toàn bộ nghiệp vụ cho gym. Các endpoint tương thích tên đường dẫn theo mẫu khi phù hợp; không sử dụng logic tiệm hoa.

## Cấu trúc

```text
api/
├── app/
│   ├── main.py                 # tạo app, đăng ký routers
│   ├── core.py                 # SQLite, seed data, schemas và helper dùng chung
│   └── routers/
│       ├── catalog.py          # branches, products, inventory, promotions, policy
│       ├── members.py          # hồ sơ hội viên
│       ├── orders.py           # báo giá, đăng ký, đổi/hủy đăng ký
│       ├── subscriptions.py    # vòng đời thẻ hội viên
│       ├── consultations.py   # lịch lớp nhóm/PT
│       ├── requests.py         # hoàn tiền, đổi gói/lịch, ưu đãi, escalations
│       ├── staff.py            # nhân viên xử lý yêu cầu, ghi nhận thanh toán
│       └── payments.py        # tra cứu thanh toán
├── sql/
│   ├── schema.sql             # bảng, ràng buộc và index
│   └── seed.sql               # dữ liệu tham chiếu idempotent
├── scripts/init_db.py        # khởi tạo/reset SQLite
├── tests/test_api.py
├── requirements.txt
└── .env.example
```

## Cài đặt và chạy

Python 3.10+ khuyến nghị. Từ thư mục `gym_center/api`:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Mở Swagger tại http://127.0.0.1:8001/docs, ReDoc tại http://127.0.0.1:8001/redoc và health check tại http://127.0.0.1:8001/health.

## Dữ liệu demo

Khi khởi động lần đầu, SQLite được tạo tự động ở `gym_center/api/gym_center.db` (có thể đặt `GYM_DB_PATH`). Dữ liệu giả lập gồm 120 hồ sơ hội viên, 120 đăng ký/thẻ tập, 180 lịch đặt và 120 giao dịch thanh toán. Cấu trúc bảng được quản lý tại `sql/schema.sql`; dữ liệu tham chiếu chi nhánh, phương thức thanh toán và loại hoạt động được nạp từ `sql/seed.sql`. Dữ liệu demo hội viên/lịch/giao dịch được tạo từ CSV knowledge base về gói hội viên, lịch lớp và huấn luyện viên. Không dùng dữ liệu thật.

## Endpoint

| Method | Endpoint | Nghiệp vụ |
|---|---|---|
| GET | `/health` | Kiểm tra trạng thái và số bản ghi demo |
| GET | `/branches` | Chi nhánh, địa chỉ, giờ hoạt động |
| GET | `/products`, `/products/{sku}` | Tìm gói tập/lớp học và xem chi tiết |
| GET | `/inventory` | Tra hội viên hoặc lịch đặt |
| GET | `/delivery/zones`, `/delivery/slots` | Tương thích tên endpoint mẫu; trả phạm vi tập tại cơ sở và khung lịch |
| GET | `/promotions`, `/discounts/{code}` | Ưu đãi và mã gói/ưu đãi |
| GET | `/policy` | Đọc `policy.yaml` |
| GET/POST | `/members`, `/members/{member_id}` | Tra cứu/tạo hội viên |
| POST/GET | `/orders`, `/orders/quote`, `/orders/{code}` | Báo giá và đăng ký gói |
| POST | `/orders/{code}/reschedule`, `/orders/{code}/cancel` | Đổi ngày bắt đầu/hủy đăng ký |
| GET | `/subscriptions/plans`, `/subscriptions/{code}` | Danh sách gói và tra thẻ |
| POST | `/subscriptions/{code}/pause`, `/resume`, `/reschedule`, `/cancel` | Bảo lưu, tiếp tục, đổi ngày, hủy thẻ |
| GET/POST | `/consultations`, `/consultations/availability`, `/consultations/{code}` | Kiểm tra và đặt lịch lớp/PT |
| POST | `/consultations/{code}/reschedule`, `/cancel` | Đổi/hủy lịch |
| POST | `/requests/refund`, `/exchange`, `/discount`, `/escalate` | Ghi nhận yêu cầu hội viên |
| GET | `/requests/{code}` | Tra trạng thái yêu cầu |
| GET/POST | `/staff/requests`, `/staff/requests/{code}/decision` | Nhân viên duyệt yêu cầu |
| POST | `/staff/orders/{code}/payment` | Ghi nhận thanh toán |
| GET | `/payments` | Tra cứu giao dịch |

## Ví dụ gọi API

```bash
curl http://127.0.0.1:8001/health
curl 'http://127.0.0.1:8001/products?product_type=plan'
curl 'http://127.0.0.1:8001/members?limit=10'
curl 'http://127.0.0.1:8001/consultations/availability?date=2026-10-25&branch=quan-7&activity_type=class'
```

## Khởi tạo database bằng script

Từ thư mục `gym_center/api`:

```bash
python scripts/init_db.py
# Tạo lại database demo từ đầu (xóa dữ liệu hiện có trong DB đích):
python scripts/init_db.py --reset
```

## Chạy kiểm thử

```bash
pytest -q
```

## Lưu ý

Đây là prototype phục vụ tích hợp agent và kiểm thử nghiệp vụ. Dữ liệu là giả lập; chưa có xác thực/phân quyền, cổng thanh toán thật hoặc kiểm soát giao dịch production. Các quyết định về hoàn tiền/bảo lưu cần được đối chiếu knowledge base và nhân viên có thẩm quyền.
