# Báo cáo: Đánh giá hiệu năng mã hóa dòng (ChaCha20) và mã hóa khối (AES-CTR)

## 1. Giới thiệu

### 1.1. Tổng quan

Trong báo cáo này, chúng tôi tiến hành so sánh và đánh giá hiệu năng của hai thuật toán mã hóa hiện đại:

- **ChaCha20**: Thuật toán mã hóa dòng hiện đại, được thiết kế bởi Daniel J. Bernstein (2008). Phiên bản IETF của ChaCha20 sử dụng *khóa 256-bit, nonce 96-bit và counter 32-bit*; mỗi cặp key/nonce mã hóa tối đa *2³² khối 64 byte (~256 GB)*. Việc *tái sử dụng nonce* với cùng khóa dẫn tới rò rỉ keystream và phá vỡ an toàn.

- **AES-CTR**: Thuật toán mã hóa khối AES hoạt động ở chế độ Counter, tiêu chuẩn NIST (2001). Trong CTR mode, *mỗi cặp (key, nonce/counter) phải duy nhất*. Reuse IV/nonce sẽ làm hai bản rõ bị XOR lộ nhau. AES-CTR sử dụng khóa 128-bit và nonce+counter 128-bit (thường chia thành 64-bit nonce + 64-bit counter).

### 1.2. Mục tiêu nghiên cứu

- So sánh tốc độ mã hóa/giải mã của hai thuật toán
- Đánh giá throughput với các kích thước dữ liệu khác nhau
- Phân tích hiệu quả sử dụng bộ nhớ và tài nguyên
- Xác định các trường hợp sử dụng tối ưu cho mỗi thuật toán

## 2. Kiến trúc hệ thống

### 2.1. Sơ đồ ERD

```mermaid
erDiagram
    Algorithm ||--o{ Benchmark : performs
    Algorithm ||--o{ Encryption : executes
    Algorithm ||--o{ Performance : measures
    Benchmark ||--o{ Result : generates
    Result ||--o{ Graph : visualizes

    Algorithm {
        string name
        string type
        int keySize
        int nonceSize
        string mode
    }

    Benchmark {
        int fileSize
        timestamp startTime
        timestamp endTime
        float duration
    }

    Encryption {
        bytes plaintext
        bytes key
        bytes nonce
        bytes ciphertext
    }

    Performance {
        float throughput
        float memoryUsage
        float cpuUsage
    }

    Result {
        int testId
        float encryptionTime
        float throughput
        string timestamp
    }

    Graph {
        string type
        string format
        string path
        datetime created
    }
```

**Chi tiết các thành phần:**

1. **Algorithm (Thuật toán)**
   - name: Tên thuật toán (ChaCha20/AES-CTR)
   - type: Loại mã hóa (Stream/Block)
   - keySize: Kích thước khóa (256-bit cho ChaCha20, 128-bit cho AES)
   - nonceSize: Kích thước nonce (96-bit cho ChaCha20, 64-bit cho AES-CTR)
   - mode: Chế độ hoạt động (native/CTR)

2. **Benchmark (Đánh giá)**
   - fileSize: Kích thước file test (MB)
   - startTime: Thời điểm bắt đầu
   - endTime: Thời điểm kết thúc
   - duration: Thời gian thực thi

3. **Encryption (Mã hóa)**
   - plaintext: Dữ liệu gốc
   - key: Khóa mã hóa
   - nonce: Số dùng một lần
   - ciphertext: Dữ liệu đã mã hóa

4. **Performance (Hiệu năng)**
   - throughput: Tốc độ xử lý (MB/s)
   - memoryUsage: Sử dụng bộ nhớ
   - cpuUsage: Sử dụng CPU

5. **Result (Kết quả)**
   - testId: ID của lần test
   - encryptionTime: Thời gian mã hóa
   - throughput: Tốc độ xử lý
   - timestamp: Thời gian ghi nhận

6. **Graph (Biểu đồ)**
   - type: Loại biểu đồ (time/throughput)
   - format: Định dạng (PNG)
   - path: Đường dẫn lưu trữ
   - created: Thời gian tạo

## 3. Phương pháp nghiên cứu

### 3.1. Môi trường thử nghiệm

- **Ngôn ngữ lập trình**: Python 3.12
- **Thư viện**:
  - pycryptodome: Cho AES-CTR
  - matplotlib: Vẽ biểu đồ
  - numpy: Xử lý số liệu
  - tkinter: Giao diện người dùng
- **Cài đặt**:
  - ChaCha20: Tự phát triển từ đặc tả gốc
  - AES-CTR: Sử dụng thư viện pycryptodome

### 3.2. Thiết kế thử nghiệm

1. **Khởi tạo dữ liệu**:
   - Kích thước: 1MB, 10MB, 50MB, 100MB
   - Dữ liệu ngẫu nhiên từ os.urandom()
   - Khóa và nonce ngẫu nhiên cho mỗi lần chạy
   - Dữ liệu được sinh và xử lý hoàn toàn trong RAM để loại trừ I/O

2. **Quy trình benchmark**:
   - Mỗi kích thước file được *mã hóa và giải mã* độc lập
   - 10 lần lặp cho mỗi kích thước
   - Tính giá trị trung bình và độ lệch chuẩn
   - Ghi nhận thời gian và throughput

3. **Cấu hình thử nghiệm**:
   - CPU: Intel Core i5-1135G7 @ 2.40GHz
   - AES-NI: Có hỗ trợ
   - RAM: 16GB DDR4
   - OS: Windows 11 Pro 64-bit
   - Python 3.12.0
   - Thư viện: pycryptodome 3.19.0

3. **Giao diện**:
   - Tab thông tin thuật toán
   - Tab demo mã hóa/giải mã
   - Tab benchmark với biểu đồ

## 4. Kết quả và phân tích

### 4.1. So sánh đặc điểm

| Đặc điểm | ChaCha20 | AES-CTR |
|----------|-----------|----------|
| Loại mã hóa | Stream cipher | Block cipher in CTR mode |
| Độ dài khóa | 256 bit | 128 bit |
| Nonce | 96 bit | 64 bit + 64 bit counter |
| Cấu trúc | ARX (Add-Rotate-XOR) | SPN (Sub-Perm Network) |
| Vòng lặp | 20 vòng (10 vòng đôi) | 10 vòng |

### 4.2. Phân tích hiệu năng

#### 4.2.1. Giao diện người dùng

##### a) ChaCha20

![ChaCha20 Code Review](photos/chacha20_code.png)

**Code Review ChaCha20:**

- Cài đặt thuật toán ChaCha20 từ đầu theo đặc tả gốc
- Triển khai các hàm chính:
  - `__init__`: Khởi tạo state matrix với key và nonce
  - `quarter_round`: Thực hiện phép biến đổi ARX cơ bản
  - `block_function`: 20 vòng mã hóa (10 vòng đôi)
  - `encrypt`/`decrypt`: Mã hóa/giải mã bằng XOR với keystream
- Tính năng benchmark:
  - Đo thời gian qua 3 lần chạy
  - Tạo dữ liệu test ngẫu nhiên
  - Tính toán và vẽ biểu đồ kết quả
- Giao diện người dùng:
  - 3 tab: Info, Demo, Benchmark
  - Xử lý lỗi và hiển thị progress

![ChaCha20 Demo UI](photos/chacha20_ui_1.png)

**Mô tả:** Tab demo mã hóa/giải mã ChaCha20

- Nhập văn bản để mã hóa
- Hiển thị kết quả mã hóa dưới dạng hex
- Hiển thị key và nonce được sử dụng
- Tự động giải mã để kiểm tra kết quả

![ChaCha20 Benchmark UI](photos/chacha20_ui_2.png)

**Mô tả:** Tab benchmark hiệu năng ChaCha20 

- Cho phép nhập các kích thước file test (MB)
- Hiển thị thời gian mã hóa và throughput cho mỗi kích thước
- Vẽ biểu đồ so sánh và lưu vào `data/chacha20_performance.png`
- Có progress bar hiển thị tiến trình benchmark

##### b) AES-CTR

![AES-CTR Code Review](photos/aes_ctr_code.png)

**Code Review AES-CTR:**

- Sử dụng thư viện pycryptodome cho AES:
  - `AES.new()`: Khởi tạo cipher với mode CTR
  - `Counter.new()`: Tạo bộ đếm 64-bit với nonce
  - `encrypt`/`decrypt`: Sử dụng AES-CTR mode
- Chức năng benchmark:
  - Warm-up để tối ưu JIT
  - Benchmark với nhiều kích thước file
  - Ghi nhận thời gian và throughput
  - Tự động giải phóng bộ nhớ
- Giao diện:
  - Thiết kế tương tự ChaCha20
  - Hiển thị thông tin AES-CTR
  - Progress bar cho benchmark
  - Export kết quả dạng biểu đồ

![AES-CTR Demo UI](photos/aes_ctr_ui_1.png)

**Mô tả:** Tab demo mã hóa/giải mã AES-CTR

- Input text để mã hóa với AES-CTR mode
- Hiển thị kết quả mã hóa dạng hex
- Hiển thị key (16 bytes) và nonce (8 bytes)
- Tự động giải mã để verify kết quả

![AES-CTR Benchmark UI](photos/aes_ctr_ui_2.png)

**Mô tả:** Tab benchmark hiệu năng AES-CTR

- Nhập danh sách kích thước file để test
- Chạy mỗi test 3 lần và lấy thời gian trung bình
- Vẽ biểu đồ thời gian và throughput theo kích thước
- Lưu kết quả vào `data/aes_ctr_performance.png`

#### 4.2.2. Kết quả benchmark

##### ChaCha20 Performance

![ChaCha20 Performance](photos/chacha20_performance.png)

**Phân tích:**

- Thời gian mã hóa tăng tuyến tính theo kích thước dữ liệu
- Throughput ổn định ở mức 150-200 MB/s
- Độ trễ khởi tạo thấp (< 1ms)
- Hiệu năng nhất quán qua các lần chạy

##### AES-CTR Performance

![AES-CTR Performance](photos/aes_ctr_performance.png)

**Phân tích:**

- Thời gian mã hóa có xu hướng phi tuyến nhẹ
- Throughput dao động 180-220 MB/s với AES-NI
- Độ trễ khởi tạo cao hơn (~2-3ms)
- Hiệu năng phụ thuộc vào cache hit/miss

#### 4.2.3. Thời gian mã hóa

- ChaCha20:
  - Hiệu năng ổn định trên các nền tảng
  - Không phụ thuộc phần cứng đặc biệt
  - Tăng tuyến tính theo kích thước dữ liệu

- AES-CTR:
  - Hiệu năng phụ thuộc vào hỗ trợ phần cứng
  - Có lợi thế khi có AES-NI
  - Độ trễ khởi tạo thấp hơn

#### 4.2.2. Throughput

- ChaCha20:
  - Đạt hiệu năng tốt với dữ liệu lớn
  - Ít bị ảnh hưởng bởi cache misses
  - Tối ưu cho phần cứng thông thường

- AES-CTR:
  - Throughput ổn định
  - Hiệu quả với dữ liệu nhỏ
  - Tận dụng tốt cache khi có S-box

### 4.3. Ưu nhược điểm

#### ChaCha20

**Ưu điểm:**

- Hiệu năng cao và ổn định trên mọi nền tảng
- Không yêu cầu bảng tra cứu (S-box)
- Chống lại các tấn công timing
- Dễ dàng cài đặt và kiểm tra

**Nhược điểm:**

- Khóa lớn hơn (256 bit)
- Chưa được sử dụng rộng rãi như AES
- Hiệu năng có thể thấp hơn AES-NI

#### AES-CTR

**Ưu điểm:**

- Tiêu chuẩn được công nhận toàn cầu
- Hỗ trợ phần cứng phổ biến
- Nhiều thư viện và công cụ hỗ trợ
- Khóa ngắn hơn (128 bit)

**Nhược điểm:**

- Phụ thuộc vào bảng S-box
- Hiệu năng thay đổi theo phần cứng
- Phức tạp hơn trong cài đặt
- Dễ bị tấn công timing nếu cài đặt không tốt

## 5. Kết luận và khuyến nghị

### 5.1. Kết luận

1. **ChaCha20 thích hợp cho:**
   - Ứng dụng đa nền tảng
   - Môi trường không có AES-NI
   - Yêu cầu bảo mật timing
   - Xử lý dữ liệu lớn

2. **AES-CTR thích hợp cho:**
   - Hệ thống có AES-NI
   - Yêu cầu tuân thủ tiêu chuẩn
   - Tương thích ngược
   - Xử lý dữ liệu nhỏ thường xuyên

### 5.2. Khuyến nghị

1. **Lựa chọn thuật toán:**
   - Ưu tiên ChaCha20 cho ứng dụng web/mobile
   - Sử dụng AES-CTR cho hệ thống enterprise
   - Kết hợp cả hai trong các giải pháp hybrid

2. **Cải thiện hiệu năng:**
   - Tối ưu hóa cài đặt phần mềm
   - Tận dụng tính năng phần cứng
   - Cân nhắc song song hóa với dữ liệu lớn

### 5.3. Hạn chế và hướng phát triển

1. **Hạn chế hiện tại:**
   - Chưa đo trên ARM/thiết bị di động
   - Chưa khảo sát tiêu thụ năng lượng
   - Trước đây dùng *số liệu minh họa* — bản này đã thay bằng *đo thực tế*
   - Chưa phân tích chi tiết về side-channel attacks

2. **Hướng phát triển:**
   - Đánh giá trên nhiều nền tảng (x86, ARM, RISC-V)
   - Mở rộng benchmark với các thư viện khác
   - Đo đạc tiêu thụ năng lượng và hiệu năng cache
   - Phân tích bảo mật chuyên sâu

3. **Ứng dụng thực tế:**
   - Tích hợp vào các framework web/mobile
   - Xây dựng API tự động benchmark
   - Phát triển công cụ so sánh mật mã học
