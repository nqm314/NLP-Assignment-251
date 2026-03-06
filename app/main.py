import nltk
import sys
import traceback
import random 
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)

INPUT_DIR = os.path.join(BASE_DIR, "..", "input")
INPUT_DIR = os.path.abspath(INPUT_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)

def part_1(syntax_file='syntax_rules.cfg', lexical_file='lexical_rules.cfg', output_file='grammar.txt'):
    """
    Yêu cầu 2.1: Xây dựng văn phạm từ dữ liệu nội bộ
    Dữ liệu nội bộ được định nghĩa từ 2 file lexical_rules.cfg và syntax_rules.cfg
    Xây dựng file grammar.txt bằng việc nối file syntax và lexical lại.
    """
    syntax_file = os.path.join(DATA_DIR, syntax_file)
    lexical_file = os.path.join(DATA_DIR, lexical_file)
    output_file = os.path.join(OUTPUT_DIR, output_file)

    print("Đang xây dựng văn phạm...")
    try:
        with open(syntax_file, 'r', encoding='utf-8') as f_syntax:
            syntax_content = f_syntax.read()
            
        with open(lexical_file, 'r', encoding='utf-8') as f_lexical:
            lexical_content = f_lexical.read()
        
        full_grammar = syntax_content + "\n\n# --- Tự động nối từ file lexical ---\n\n" + lexical_content
        
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(full_grammar)
            
        print(f"Hoàn thành yêu cầu 2.1! Đã xây dựng văn phạm CFG tại {output_file}")
        return full_grammar
        
    except FileNotFoundError as e:
        print(f"Lỗi yêu cầu 2.1: Không tìm thấy file '{syntax_file}' và '{lexical_file}'")
        print(f"Chi tiết: {e}")
        return None
    except Exception as e:
        print(f"Lỗi yêu cầu 2.1: {e}")
        return None

def generate_random_recursive(grammar, symbol):
    """
    Hàm đệ quy để sinh ngẫu nhiên, bắt đầu từ một 'symbol'.
    Hỗ trợ cho yêu cầu 2.2
    """

    # Lấy tất cả các quy tắc có thể có cho 'symbol' này (vế trái)
    # Ex: symbol = Cau, productions = [Cau -> CauDatMon, Cau -> CauHoi, ...]
    productions = grammar.productions(lhs=symbol)

    if not productions:
        print(f"!!! LỖI NGỮ PHÁP: Ký hiệu {symbol} được dùng nhưng không được định nghĩa!!!")
        return [f"UNDEFINED_SYMBOL({symbol.symbol()})"]

    # Chọn ngẫu nhiên 1 quy tắc trong số đó
    # Ex: prod = (Cau -> CauDatMon)
    prod = random.choice(productions)

    sentence_parts = []

    # Lặp qua vế phải của quy tắc (vd: [CauDatMon])
    for sym_on_rhs in prod.rhs():

        # Kiểm tra xem nó là terminal (từ) hay non-terminal (một quy tắc khác)
        if isinstance(sym_on_rhs, str):
            # Nếu là 'str' (vd: 'cho', 'tôi', 'cơm sườn') -> nó là terminal
            # -> Thêm nó vào câu
            sentence_parts.append(sym_on_rhs)
        else:
            # Nếu là Nonterminal (vd: CauDatMon, OPT_ChuNgu)
            # -> Gọi đệ quy để giải quyết nó
            # -> Nối kết quả của hàm con vào
            sentence_parts.extend(generate_random_recursive(grammar, sym_on_rhs))

    return sentence_parts


def part_2(grammar, number_of_sentences):
    """
    Yêu cầu 2.2: Sinh câu.
    Sử dụng giải thuật đệ quy ngẫu nhiên.
    """
    print(f"Đang sinh {number_of_sentences} câu (dùng đệ quy ngẫu nhiên)...")
    try:
        start_symbol = nltk.Nonterminal('Cau') # Bắt đầu từ 'Cau'
        samples_file = os.path.join(OUTPUT_DIR, 'samples.txt')
        with open(samples_file, "w", encoding="utf-8") as f_out:
            for i in range(number_of_sentences):
                # Gọi hàm sinh ngẫu nhiên
                tokens = generate_random_recursive(grammar, start_symbol)
                sentence = ' '.join(tokens)
                f_out.write(sentence + "\n")

                # In ra tiến độ cho 100 câu đầu
                if i < 100 or i % 1000 == 0:
                    print(f"  Sinh câu {i+1}: {sentence}")

        print(f"Hoàn thành yêu cầu 2.2! Đã sinh {number_of_sentences} câu trong output/samples.txt")

    except Exception as e:
        print(f"Lỗi yêu cầu 2.2: {e}")
        traceback.print_exc()

def part_3(grammar):
    """
    Yêu cầu 2.3: Phân tích và xây dựng cây cú pháp.
    Dùng tokenizer tham lam (greedy) và EarleyChartParser.
    """
    print("Đang phân tích câu từ input/sentences.txt...")
    try:
        # Tạo một set chứa tất cả các từ vựng (terminals)
        print("Đang nạp từ vựng...")
        terminal_set = set()
        max_phrase_len = 1 # Tìm độ dài cụm từ dài nhất (vd: 'cơm sườn trứng' là 3)
        
        for prod in grammar.productions():
            if prod.is_lexical():
                # prod.rhs() là một tuple, vd: ('cơm sườn',)
                terminal = prod.rhs()[0]
                terminal_set.add(terminal)
                
                words_in_terminal = len(terminal.split())
                if words_in_terminal > max_phrase_len:
                    max_phrase_len = words_in_terminal
                    
        print(f"Đã nạp {len(terminal_set)} từ vựng. Cụm từ dài nhất có {max_phrase_len} từ.")

        # Tạo Parser (Earley)
        parser = nltk.EarleyChartParser(grammar)
        
        input_file = os.path.join(INPUT_DIR, 'sentences.txt')
        output_file = os.path.join(OUTPUT_DIR, 'parse-results.txt')
        count_success = 0
        count_failure = 0
        total = 0

        with open(input_file, 'r', encoding='utf-8') as f_in, \
             open(output_file, 'w', encoding='utf-8') as f_out:
            
            for line in f_in:
                sentence = line.strip()
                if not sentence:
                    continue
                
                total += 1
                f_out.write(f"--------------------------------------------------\n")
                f_out.write(f"The sentence: {sentence}\n")
                
                # Tokenizer tham lam (Greedy Tokenizer)
                tokens = []
                words = sentence.split()
                i = 0
                while i < len(words):
                    found = False
                    # Thử khớp cụm dài nhất trước
                    for length in range(max_phrase_len, 0, -1): 
                        if i + length <= len(words):
                            phrase = ' '.join(words[i:i+length])
                            
                            if phrase in terminal_set:
                                tokens.append(phrase)
                                i += length
                                found = True
                                break
                    if not found:
                        f_out.write(f"!!! Lỗi Tokenizer: Từ '{words[i]}' không có trong văn phạm.\n")
                        i += 1 
                
                if not tokens:
                    f_out.write("Parsed rule: () (Không thể tokenize)\n")
                    continue

                # Phân tích
                try:
                    parse_trees = list(parser.parse(tokens))
                    
                    if parse_trees:
                        tree_str = str(parse_trees[0])
                        f_out.write("Parsed rule (Tree):\n")
                        f_out.write(f"{tree_str}\n")
                        count_success += 1
                        
                        if len(parse_trees) > 1:
                            f_out.write(f"\n!!! CẢNH BÁO: VĂN PHẠM BỊ MƠ HỒ (AMBIGUOUS)!!!\n")
                            f_out.write(f"Tìm thấy {len(parse_trees)} cây cú pháp khác nhau.\n")
                            # f_out.write(f"Cây thứ 2:\n{str(parse_trees[1])}\n")
                    
                    else:
                        f_out.write("Parsed rule: ()\n") # Không hợp lệ
                        count_failure += 1
                except ValueError as e:
                    f_out.write(f"Parsed rule: () (Lỗi: {e})\n")

        print(f"Hoàn thành yêu cầu 2.3! Phân tích thành công {count_success}/{total} câu.")
        print(f"Có {count_failure}/{total} câu bị lỗi.")
        print(f"Kết quả trong {output_file}")

    except Exception as e:
        print(f"Lỗi yêu cầu 2.3: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách chạy:")
        print("python main.py 1                (Nối văn phạm)")
        print("python main.py 2 [số_câu]       (Sinh câu, vd: 2 1000)")
        print("python main.py 3                (Phân tích câu)")
        sys.exit(1)

    part = sys.argv[1]
    
    # Part 1 phải chạy trước để tạo 'output/grammar.txt'
    full_grammar_str = part_1()
    if not full_grammar_str:
        sys.exit(1)
        
    try:
        # Nạp văn phạm từ chuỗi đã nối
        grammar = nltk.CFG.fromstring(full_grammar_str)
    except Exception as e:
        print(f"Lỗi nghiêm trọng khi nạp văn phạm: {e}")
        sys.exit(1)

    # Chạy các phần còn lại
    if part == "1":
        pass # Đã chạy
    elif part == "2":
        num = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        part_2(grammar, num)
    elif part == "3":
        part_3(grammar)
    else:
        print(f"Part '{part}' không hợp lệ. Chỉ chấp nhận 1, 2, hoặc 3.")