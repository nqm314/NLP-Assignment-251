# 1. Dùng Python 3.9 (Ổn định hơn cho llama-cpp so với 3.8)
FROM python:3.9-slim

WORKDIR /app

# 2. CÀI CÔNG CỤ BUILD (Thuốc giải cho lỗi thiếu C++)
# Cập nhật và cài gcc, g++, cmake để biên dịch llama-cpp-python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 3. Cài thư viện Python
COPY requirements.txt .
# Upgrade pip để tránh lỗi vặt
RUN pip install --upgrade pip
# Cài các gói (Lúc này nó sẽ tự biên dịch llama-cpp, mất tầm 2-3 phút)
RUN pip install -r requirements.txt

# 4. Tải dữ liệu NLTK
RUN python -m nltk.downloader all

# 5. Copy toàn bộ code vào
COPY . .

# 6. Mở cổng 8501 (Cổng Web của Streamlit)
EXPOSE 8501

# 7. Lệnh chạy: Tải model trước -> Chạy Web sau
# --server.address=0.0.0.0 là BẮT BUỘC để truy cập từ bên ngoài Docker
ENTRYPOINT ["/bin/bash", "-c", "python download_model.py && streamlit run app/gui.py --server.address=0.0.0.0 --browser.serverAddress=localhost"]