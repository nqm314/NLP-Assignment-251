import sys
import os
import nltk
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag import MenuRAG
from llm import LocalLLM

def setup_parser():
    grammar_path = 'output/grammar.txt'
    if not os.path.exists(grammar_path):
        return None
    try:
        with open(grammar_path, 'r', encoding='utf-8') as f:
            grammar = nltk.CFG.fromstring(f.read())
        return nltk.EarleyChartParser(grammar)
    except:
        return None

def normalize_quantity(sentence):
    # Map các từ chỉ số lượng thông dụng
    word_to_num = {
        'một': '1', 'hai': '2', 'ba': '3', 'bốn': '4', 'năm': '5',
        'sáu': '6', 'bảy': '7', 'tám': '8', 'chín': '9', 'mười': '10',
        'chục': '10'
    }
    
    sentence_lower = sentence.lower()
    for word, num in word_to_num.items():
        sentence_lower = re.sub(rf'\b{word}\b', num, sentence_lower)
    
    return sentence_lower

def calculate_order_logic(sentence, menu_items):
    clean_sentence = normalize_quantity(sentence)
    
    found_items = []
    total_price = 0
    
    sorted_menu = sorted(menu_items, key=lambda x: len(x['ten_mon']), reverse=True)
    
    for item in sorted_menu:
        item_name = item['ten_mon'].lower()
        item_price = item['gia']
        
        pattern = rf"(\d+)?\s*(?:tô|bát|dĩa|suất|hộp|ly|cốc|phần|chai)?\s*{re.escape(item_name)}"
        
        # Tìm tất cả các lần xuất hiện
        matches = re.finditer(pattern, clean_sentence)
        
        for match in matches:
            full_match = match.group(0)
            
            if "[[MASK]]" in full_match:
                continue

            qty_str = match.group(1)
            quantity = int(qty_str) if qty_str else 1
            
            # Tính tiền
            cost = quantity * item_price
            total_price += cost
            
            cost_str = "{:,.0f}".format(cost).replace(",", ".")
            found_items.append(f"{quantity} {item['ten_mon']} ({cost_str}đ)")
            
            clean_sentence = clean_sentence.replace(full_match, "[[MASK]]", 1)

    if found_items:
        total_str = "{:,.0f}".format(total_price).replace(",", ".")
        return f"HỆ THỐNG TÍNH TOÁN: Khách đặt: {', '.join(found_items)}. TỔNG ĐƠN: {total_str} vnđ."
    
    return None


def analyze_intent(parser, sentence, menu_items):
    s_lower = sentence.lower()
    if any(w in s_lower for w in ['giao lúc', 'giao vào', 'ship lúc', 'giờ tối', 'giờ sáng', 'chốt đơn']):
         return "HỆ THỐNG: Khách đang CHỐT ĐƠN hoặc HẸN GIỜ. Hãy xác nhận thời gian và cảm ơn."

    if "đổi" in s_lower and ("thành" in s_lower or "sang" in s_lower):
        return "HỆ THỐNG: Khách muốn ĐỔI MÓN. Hãy xác nhận món cũ đổi sang món mới và tính lại giá (nếu có thông tin)."

    calc_result = calculate_order_logic(sentence, menu_items)
    if calc_result:
        return calc_result

    if parser:
        try:
            tokens = sentence.lower().split()
            trees = list(parser.parse(tokens))
            if trees:
                return f"Cấu trúc câu (Tham khảo): {str(trees[0])}"
        except:
            pass
            
    return "HỆ THỐNG: Khách đang hỏi thông tin hoặc trò chuyện."


def main():
    print("\n" + "="*50)
    print("   🤖 CHATBOT ĐẶT MÓN (Qwen Hybrid Logic)   ")
    print("="*50 + "\n")

    try:
        rag = MenuRAG()
        parser = setup_parser()
        llm = LocalLLM() 
    except Exception as e:
        print(f"\n❌ Lỗi khởi động: {e}")
        return

    print("\n💬 Bot: Xin chào! Mời anh/chị đặt món.")

    while True:
        user_input = input("\n👤 Khách: ").strip()
        if user_input.lower() in ['thoat', 'exit', 'quit']:
            print("💬 Bot: Tạm biệt!")
            break
        if not user_input: continue

        # B1: RAG lấy menu
        rag_results = rag.search(user_input)
        
        # B2: Python tính toán
        system_hint = analyze_intent(parser, user_input, rag.menu_items)
        
        # B3: LLM trả lời
        reply = llm.generate_response(user_input, rag_results, system_hint)
        
        print(f"🤖 Bot: {reply}")

if __name__ == "__main__":
    main()