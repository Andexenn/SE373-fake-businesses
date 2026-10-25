# Gym Center — Iron Việt Fitness

Thư mục mô phỏng kiến thức và nghiệp vụ cho agent hỗ trợ khách hàng phòng gym. `moc-mien-florist` chỉ là tài liệu tham khảo về cách tổ chức API và quy ước tên endpoint; các chính sách và nghiệp vụ trong thư mục này được thiết kế riêng cho gym.

## Thành phần

- `knowledge_base/`: tài liệu và dữ liệu tham chiếu về chi nhánh, gói hội viên, giá lớp/PT, lịch lớp, sức chứa, khuyến mãi, quy định an toàn, đặt/hủy lịch và hoàn tiền.
- `brand_voice.md`: giọng điệu và cách phản hồi của thương hiệu.
- `policy.yaml`: chính sách nghiệp vụ có cấu trúc.
- `tools/pdf_src/`: nguồn Markdown để dựng lại tài liệu PDF.
- `tools/build_pdfs.py`: tiện ích tạo PDF từ nguồn.
- `api/`: FastAPI, SQLite demo, router theo nghiệp vụ và kiểm thử. `api/sql/schema.sql` định nghĩa bảng/ràng buộc/index; `api/sql/seed.sql` nạp dữ liệu tham chiếu ban đầu. Xem `api/README.md`.

## Chạy API nhanh

```bash
cd gym_center/api
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Swagger UI: http://127.0.0.1:8001/docs

## Dữ liệu giả lập

API seed tối thiểu 120 hội viên, 180 lịch đặt và 120 giao dịch vào SQLite khi khởi động lần đầu. Các bản ghi không đại diện cho khách hàng thật.

## Kiểm thử

```bash
cd gym_center/api
python -m pytest -q
```
