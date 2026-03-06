import streamlit as st
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag import MenuRAG
from llm import LocalLLM
from bot import setup_parser, analyze_intent

st.set_page_config(
    page_title="Online FoodBot",
    page_icon="🍜",
    layout="wide"
)

st.title("🍜 Online FoodBot - Trợ lý đặt món thông minh")
st.markdown("---")

@st.cache_resource(show_spinner=False)
def load_system():
    print("🔄 Đang khởi tạo hệ thống cho GUI...")
    rag = MenuRAG(menu_path='data/menu.json')
    parser = setup_parser()
    
    model_path = 'models/qwen2.5-1.5b-instruct-q5_k_m.gguf' 
    if not os.path.exists(model_path):
        model_path = 'models/qwen2.5-1.5b-instruct-q5_k_m.gguf'
        
    llm = LocalLLM(model_path=model_path)
    return rag, parser, llm

with st.spinner("Đang khởi động hệ thống AI (Parser + RAG + LLM)... Vui lòng chờ..."):
    try:
        rag_engine, parser_engine, llm_engine = load_system()
        st.success("Hệ thống đã sẵn sàng!", icon="✅")
        time.sleep(1)
    except Exception as e:
        st.error(f"Lỗi khởi động: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Mời anh/chị gọi món."}
    ]

with st.sidebar:
    st.header("🔧 Thông số Kỹ thuật")
    st.info("Hệ thống Hybrid: Earley Parser + RAG + Local LLM Qwen2.5 1.5B")
    
    st.subheader("🔍 Phân tích Cú pháp (Parser)")
    parser_placeholder = st.empty()
    parser_placeholder.text("(Chưa có dữ liệu)")
    
    st.subheader("📚 Dữ liệu Menu (RAG)")
    rag_placeholder = st.empty()
    rag_placeholder.text("(Chưa có dữ liệu)")

# --- HIỂN THỊ CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ INPUT NGƯỜI DÙNG ---
if prompt := st.chat_input("Nhập yêu cầu đặt món..."):
    # 1. Hiển thị câu hỏi của khách
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Xử lý Logic (Backend)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("▌ *Đang suy nghĩ...*")
        
        try:
            rag_results = rag_engine.search(prompt)
            rag_text = "\n".join([f"- {m['ten_mon']}" for m in rag_results])
            rag_placeholder.code(rag_text if rag_text else "Không tìm thấy món", language="text")

            parser_info = analyze_intent(parser_engine, prompt, rag_engine.menu_items)
        
            parser_placeholder.code(parser_info, language="text")

            stream = llm_engine.generate_response(prompt, rag_results, parser_info)
            full_response = message_placeholder.write_stream(stream)
            
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            message_placeholder.error(f"Lỗi xử lý: {e}")