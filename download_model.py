import os
import requests
from tqdm import tqdm

# --- CẤU HÌNH QWEN 2.5 (1.5B Parameters) ---
# Link tải bản Q5_K_M (Cân bằng nhất) - Nặng chỉ ~1.1 GB
MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q5_k_m.gguf?download=true"
MODEL_DIR = "models"
MODEL_FILENAME = "qwen2.5-1.5b-instruct-q5_k_m.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

def download_file():
    print(f"🚀 Đang tải Siêu Phẩm Qwen2.5-1.5B (~1.1 GB)...")
    
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    if os.path.exists(MODEL_PATH):
        print(f"✅ Model đã có sẵn: {MODEL_PATH}")
        return

    try:
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(MODEL_PATH, 'wb') as f, tqdm(
            desc="Downloading",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024*1024):
                size = f.write(data)
                bar.update(size)
        print("\n✅ TẢI THÀNH CÔNG!")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")

if __name__ == "__main__":
    download_file()