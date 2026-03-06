# Tài liệu Thiết kế Dữ liệu và Giải thuật

**Bài tập lớn Xử lý ngôn ngữ tự nhiên - Phần 1: Viết văn phạm và Parser**

---

## 1. Tiếp cận Bài toán

Bài toán đặt ra là xây dựng một hệ thống hiểu ngôn ngữ tự nhiên (NLU) trong miền hẹp: **Đặt món ăn trực tuyến tiếng Việt**.

Đặc thù của miền ngôn ngữ này:
1.  **Cấu trúc linh hoạt:** Người Việt có thể nói "cho 2 phở bò" hoặc "phở bò 2 tô" đều đúng.
2.  **Từ ghép:** Đơn vị từ vựng (token) thường là từ ghép (ví dụ: "cơm sườn", "trà sữa", "không hành").
3.  **Thông tin phân tán:** Một câu lệnh có thể chứa nhiều món, mỗi món có số lượng và ghi chú riêng, kèm theo thông tin thời gian giao hàng.

**Chiến lược tiếp cận:**
Thay vì sử dụng các luật cứng nhắc (Hard-coded rules), hệ thống sử dụng **Văn phạm Phi ngữ cảnh (Context-Free Grammar - CFG)** để mô hình hóa ngôn ngữ. Dữ liệu được tách biệt hoàn toàn giữa "Từ vựng" (Lexical) và "Cấu trúc" (Syntax) để đảm bảo tính mở rộng.

---

## 2. Tổ chức và Ý nghĩa Dữ liệu

Dữ liệu văn phạm được chia thành hai tệp tin cấu hình riêng biệt (`.cfg`), đóng vai trò là "Bộ não" cho Parser.

### 2.1. Lexical Rules (`data/lexical_rules.cfg`)
File này định nghĩa các **Ký hiệu Kết thúc (Terminals)**. Nó đóng vai trò là từ điển, ánh xạ các khái niệm trừu tượng sang từ ngữ cụ thể.

* **Thực thể Món ăn (`TenMon`):** Danh sách các món có trong menu (VD: 'cơm sườn', 'phở bò'...).
* **Đơn vị tính (`DonVi`):** Các từ chỉ đơn vị (VD: 'tô', 'phần', 'ly'...).
* **Đặc điểm/Tùy chọn (`DacDiem`):** Các yêu cầu chế biến (VD: 'ít đường', 'không hành').
* **Hành động/Ý định (Intents):**
    * `CumDongTu_Dat`: Ý định muốn mua (đặt, lấy, cho...).
    * `CumDongTu_Huy`: Ý định muốn bỏ món (hủy, không lấy...).
    * `CumDongTu_CapNhat`: Ý định sửa đổi (thêm, đổi, giảm...).
* **Thời gian (`Time`):** Các từ vựng để cấu thành mốc thời gian (giờ, phút, rưỡi, ship lúc...).

### 2.2. Syntax Rules (`data/syntax_rules.cfg`)
File này định nghĩa các **Luật sinh (Production Rules)**. Nó mô tả cấu trúc ngữ pháp của câu mà không phụ thuộc vào từ vựng cụ thể.

**Cấu trúc cốt lõi:** `CumDanhTu_MonAn` (Cụm danh từ món ăn).
Đây là cấu trúc phức tạp nhất, được thiết kế để xử lý sự linh hoạt của tiếng Việt:
* *Dạng Tiền tố:* `(Số lượng) (Đơn vị) [Tên Món] (Đặc điểm)` -> VD: "2 tô phở bò ít hành".
* *Dạng Hậu tố:* `[Tên Món] (Số lượng) (Đơn vị) (Đặc điểm)` -> VD: "Phở bò 2 tô ít hành".

---

## 3. Giải thuật và Kỹ thuật 

Hệ thống sử dụng kết hợp các giải thuật kinh điển trong NLP cổ điển để đảm bảo hiệu năng và độ chính xác.

### 3.1. Chiến lược Tokenizer: Tham lam (Greedy Tokenization)
Tiếng Việt không dùng dấu cách để tách từ hoàn toàn (ví dụ: "cơm sườn" là 1 từ, nhưng có khoảng trắng).
* **Vấn đề:** Nếu dùng `split()` thông thường, "cơm sườn" sẽ bị tách thành "cơm" và "sườn". Parser sẽ không hiểu.
* **Giải thuật:** Hệ thống sử dụng chiến lược **Greedy Matching (Khớp dài nhất trước)**.
    1.  Nạp toàn bộ từ vựng từ `lexical_rules.cfg` vào một Tập hợp (Set) để tra cứu O(1).
    2.  Quét câu đầu vào, ưu tiên khớp các cụm từ dài nhất có thể (Max-match) có trong từ điển.
    3.  Ví dụ: Với câu "cơm sườn trứng", hệ thống sẽ ưu tiên khớp token `cơm sườn trứng` (3 từ) thay vì `cơm` + `sườn` + `trứng`.

### 3.2. Giải thuật Phân tích cú pháp: Earley Chart Parser
Thay vì sử dụng giải thuật CYK (yêu cầu văn phạm phải ở dạng chuẩn Chomsky - CNF gây khó đọc) hay Recursive Descent (dễ bị lặp vô hạn với đệ quy trái), hệ thống sử dụng **Earley Parser**.

* **Độ phức tạp:** $O(n^3)$ trong trường hợp tệ nhất, nhưng nhanh hơn nhiều với các văn phạm thực tế.
* **Ưu điểm:**
    * Hỗ trợ mọi loại văn phạm CFG (bao gồm cả đệ quy trái, luật rỗng, luật đơn vị).
    * Xử lý tốt các cấu trúc nhập nhằng (Ambiguous grammar).
    * Cho phép giữ nguyên cấu trúc văn phạm tự nhiên, dễ đọc hiểu cho con người.

### 3.3. Giải thuật Sinh câu: Đệ quy Ngẫu nhiên (Recursive Random Generation)
Để tạo ra tập dữ liệu mẫu (`samples.txt`) đa dạng, hệ thống sử dụng giải thuật sinh đệ quy top-down tự xây dựng (thay vì dùng `nltk.generate` vốn chỉ sinh theo thứ tự cố định).

* **Cơ chế:**
    1.  Bắt đầu từ nút gốc `Cau`.
    2.  Tại mỗi nút phi-kết-thúc, chọn ngẫu nhiên (`random.choice`) một luật sinh khả dụng.
    3.  Đệ quy xuống các nút con cho đến khi gặp ký hiệu kết thúc (Terminal).
    4.  Cơ chế "Bảo vệ": Nếu gặp một ký hiệu chưa được định nghĩa, hệ thống sẽ báo lỗi thay vì crash, giúp quá trình debug văn phạm dễ dàng hơn.

---

## 4. Xử lý Mơ hồ (Ambiguity Handling)

Một trong những thách thức lớn nhất là sự mơ hồ trong cấu trúc `CumDanhTu_MonAn`.
* *Tình huống:* Câu input "cơm sườn".
* *Lỗi tiềm ẩn:* Parser có thể hiểu theo 2 cách:
    1.  Dạng Tiền tố (với số lượng rỗng): `(Null) cơm sườn`.
    2.  Dạng Hậu tố (với số lượng rỗng): `cơm sườn (Null)`.

**Giải pháp:** Thiết kế văn phạm **Loại trừ lẫn nhau (Mutually Exclusive)**.
Hệ thống chia `CumDanhTu_MonAn` thành 2 nhóm luật không giao nhau:
* `Cum_MonAn_1`: BẮT BUỘC bắt đầu bằng Số lượng hoặc Đơn vị.
* `Cum_MonAn_2`: BẮT BUỘC bắt đầu bằng Tên món.

Kết quả là mỗi câu input chỉ có duy nhất một cây cú pháp hợp lệ (Unambiguous Parse Tree), đảm bảo tính chính xác cho các bước xử lý ngữ nghĩa sau này.