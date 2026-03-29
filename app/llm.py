from llama_cpp import Llama
import os

class LocalLLM:
    def __init__(self, model_path='models/qwen2.5-1.5b-instruct-q5_k_m.gguf'):
        print(f"🧠 Downloading Qwen2.5 ({model_path})...")
        if not os.path.exists(model_path):
            raise FileNotFoundError("❌ Model not found. Please download again!")

        # Llama-cpp-python nạp model
        self.model = Llama(
            model_path=model_path,
            n_ctx=32768,       # Context window
            n_threads=8,       # Số luồng CPU
            n_gpu_layers=0,    # Chạy GPU nếu có
            verbose=False      # Tắt log rác của thư viện
        )
        print("✅ Model is ready.")

    def generate_response(self, user_query, rag_info, parser_info):
        # 1. Format Menu
        formatted_menu = []
        for m in rag_info:
            price_str = "{:,.0f}".format(m['gia']).replace(",", ".")
            formatted_menu.append(f"- {m['ten_mon']} (Giá: {price_str} vnđ)")
        menu_context = "\n".join(formatted_menu)
        
        system_content = f"""Bạn là nhân viên phục vụ quán ăn chuyên nghiệp.
Nhiệm vụ:
1. Trả lời khách hàng dựa trên MENU bên dưới.
2. Nếu khách ĐẶT MÓN: Xác nhận tên món và TỔNG TIỀN (Sử dụng con số từ HỆ THỐNG TÍNH TOÁN).
3. KHÔNG tự bịa giá. KHÔNG hỏi ngược lại khách nếu không cần thiết.

MENU QUÁN:
{menu_context}

HỆ THỐNG TÍNH TOÁN (Độ tin cậy 100%):
{parser_info}"""

        prompt = f"""<|im_start|>system
{system_content}<|im_end|>
<|im_start|>user
{user_query}<|im_end|>
<|im_start|>assistant
"""
        
        print(f"\n[DEBUG] Prompt:\n{prompt}\n")
        print("[DEBUG] Qwen đang suy nghĩ...")
        
        full_response = ""
        
        # 3. Gọi model (Cú pháp của llama-cpp)
        stream = self.model(
            prompt,
            max_tokens=256,
            temperature=0.1, 
            top_p=0.9,
            stop=["<|im_end|>", "User:", "Khách:"], # Stop tokens
            stream=True
        )

        for output in stream:
            # Lấy text từ chunk
            text = output['choices'][0]['text']
            print(text, end="", flush=True)
            full_response += text
            yield text # Dùng yield để Streamlit hiển thị mượt mà
            
        print("\n")