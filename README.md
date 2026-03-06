# Bài tập lớn Xử lý Ngôn ngữ Tự nhiên (CO3085) - Hệ thống Đặt món ăn Thông minh

**Sinh viên thực hiện:** Nguyễn Quang Minh

**MSSV:** 2212063

---

## 1. Tổng quan Dự án
Dự án xây dựng một giải pháp toàn diện cho bài toán đặt món ăn trực tuyến qua ngôn ngữ tự nhiên tiếng Việt, kết hợp giữa hai 2 cách tiếp cận:
1.  **Phần 1 (Classical NLP):** Xây dựng Văn phạm phi ngữ cảnh (CFG) và Parser để phân tích cấu trúc câu chính xác.
2.  **Phần 2 (Modern NLP):** Xây dựng Chatbot thông minh sử dụng **LLM/RAG** (Kết hợp Logic Python và Mô hình ngôn ngữ lớn chạy cục bộ).

**Điểm nổi bật:**
* **Hoạt động Offline:** Hệ thống chạy hoàn toàn trên Docker, không phụ thuộc API trả phí.
* **Mô hình AI:** Sử dụng **Qwen2.5-1.5B-Instruct** (Quantized) cho tốc độ phản hồi cực nhanh trên CPU.
* **Kiến trúc Lai (Hybrid):** Khắc phục lỗi tính toán của LLM bằng logic lập trình (Python Regex & Parser), đảm bảo hóa đơn luôn chính xác.
* **Giao diện:** Web App trực quan với **Streamlit**, tích hợp Debug Panel để theo dõi luồng xử lý.

👉 **[QUAN TRỌNG] Xem chi tiết thiết kế giải thuật và dữ liệu tại: [DATA_DESIGN.md](./DATA_DESIGN.md)**

---

## 2. Cấu trúc Thư mục
Dự án được tổ chức theo cấu trúc module hóa:

* **`/app`**: Mã nguồn chính của chương trình.
    * `main.py`: Entrypoint cho các tác vụ Phần 1 (Sinh câu, Parse câu).
    * `bot.py`, `llm.py`, `rag.py`: Các module lõi cho Chatbot Phần 2.
    * `gui.py`: Giao diện Web (Streamlit).
* **`/data`**: Dữ liệu đầu vào (Menu, Luật văn phạm).
* **`/models`**: Nơi chứa file model AI (`.gguf`).
* **`/input`**: Dữ liệu kiểm thử cho Phần 1.
* **`/output`**: Nơi chứa kết quả đầu ra của Phần 1.
* **`Dockerfile`**: Cấu hình môi trường.

---

## 3. Hướng dẫn Cài đặt & Chạy (Sử dụng Docker)
Yêu cầu: Máy tính đã cài đặt **Docker Desktop**.

### Bước 1: Xây dựng Docker Image (Build)
Mở terminal (PowerShell hoặc CMD) tại thư mục gốc của dự án và chạy lệnh sau để đóng gói toàn bộ mã nguồn và thư viện:
```
docker build -t nlp-assignment-2 .
```
(Quá trình này có thể mất 20-30 phút để cài đặt các thư viện cần thiết).

### Bước 2: Chạy Phần 1 (Parser Cổ điển - CLI)
Phần này thực hiện các yêu cầu: Tạo văn phạm, Sinh câu mẫu, và Phân tích cú pháp câu. Do Dockerfile mặc định chạy Chatbot (Phần 2), nên để chạy Phần 1, chúng ta cần sử dụng cờ `--entrypoint python` để gọi riêng script xử lý.

Lưu ý: Các lệnh dưới đây sử dụng cú pháp của Windows PowerShell (${pwd}).

#### 2.1. Yêu cầu 1: Xây dựng Văn phạm (Grammar)
Hệ thống đọc dữ liệu từ thư mục `data/` và tạo ra file văn phạm chuẩn.

- Output: `output/grammar.txt`
```
docker run --rm --entrypoint python -v "${pwd}/output:/app/output" nlp-assignment-2 app/main.py 1
```
#### 2.2. Yêu cầu 2: Sinh câu ngẫu nhiên (Generation)
Sinh ra 10.000 câu mẫu hợp lệ từ văn phạm vừa tạo.

- Output: `output/samples.txt`
```
docker run --rm --entrypoint python -v "${pwd}/output:/app/output" nlp-assignment-2 app/main.py 2 10000
```
#### 2.3. Yêu cầu 3: Phân tích cú pháp (Parsing)
Đọc các câu từ file `input/sentences.txt` và dựng cây cú pháp.

- Input: File `sentences.txt` từ máy thật (được mount vào).

- Output: `output/parse-results.txt`
```
docker run --rm --entrypoint python -v "${pwd}/output:/app/output" -v "${pwd}/input:/app/input" nlp-assignment-2 app/main.py 3
```
### Bước 3: Chạy Phần 2 (AI Chatbot - Web Interface)
Đây là ứng dụng chính của bài tập lớn với giao diện đồ họa.

**Lệnh khởi động:**

Chạy lệnh sau để bật Web App. Lưu ý chúng ta cần ánh xạ cổng `8501`. Do giới hạn dung lượng nộp bài (<10MB), file model AI (~1.2GB) không được đính kèm. Hệ thống đã được lập trình để TỰ ĐỘNG TẢI MODEL trong lần chạy đầu tiên.
```
docker run --rm -p 8501:8501 -v "${pwd}:/app" nlp-assignment-2
```
**Quá trình khởi động:**
1. Tải Model (Lần đầu tiên): Nếu máy chưa có file model Qwen2.5-1.5B (~1.2 GB) trong thư mục `models/`, hệ thống sẽ tự động tải về. Vui lòng giữ kết nối Internet.

2. Các lần sau: Hệ thống sẽ dùng lại model đã tải (do đã mount volume), khởi động rất nhanh.

**Truy cập ứng dụng:**
Sau khi terminal hiện thông báo `You can now view your Streamlit app in your browser`, hãy mở trình duyệt và truy cập:

👉 `http://localhost:8501`

## 4. Ghi chú về Dữ liệu
- Kết quả Phần 1: Sau khi chạy xong các lệnh ở Bước 2, vui lòng kiểm tra thư mục `output/` trên máy tính để xem các file kết quả (`grammar.txt`, `samples.txt`, `parse-results.txt`).

- Dữ liệu Menu (Phần 2): Được định nghĩa trong `data/menu.json`. Bạn có thể chỉnh sửa file này để thêm món ăn mới, Chatbot sẽ tự động cập nhật kiến thức (RAG) ở lần chạy sau.