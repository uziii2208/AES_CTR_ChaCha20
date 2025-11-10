# CheatSheet: So sánh hiệu năng ChaCha20 vs AES-CTR

## 1. Tổng quan code

### ChaCha20
```python
# Khởi tạo
key = os.urandom(32)    # 256-bit key
nonce = os.urandom(12)  # 96-bit nonce
cipher = ChaCha20.new(key=key, nonce=nonce)

# Mã hóa/Giải mã
encrypted = cipher.encrypt(data)
cipher = ChaCha20.new(key=key, nonce=nonce)  # Tạo cipher mới để giải mã
decrypted = cipher.decrypt(encrypted)
```

### AES-CTR
```python
# Khởi tạo
key = os.urandom(16)     # 128-bit key
nonce = os.urandom(8)    # 64-bit nonce
ctr = Counter.new(64, prefix=nonce)  # 64-bit counter
cipher = AES.new(key, AES.MODE_CTR, counter=ctr)

# Mã hóa/Giải mã 
encrypted = cipher.encrypt(data)
ctr = Counter.new(64, prefix=nonce)  # Reset counter
cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
decrypted = cipher.decrypt(encrypted)
```

## 2. Quy trình Benchmark

1. **Dữ liệu test:**
   - Kích thước: 1MB, 10MB, 50MB, 100MB
   - Sinh ngẫu nhiên bằng os.urandom()
   - Khóa và nonce mới cho mỗi lần chạy

2. **Phương pháp:**
   - 10 lần lặp mỗi kích thước
   - Đo cả mã hóa và giải mã
   - Tính mean ± std
   - Xử lý hoàn toàn trong RAM

3. **Metric:**
   - Thời gian xử lý (giây)
   - Throughput (MB/s)
   - Error bars cho độ lệch chuẩn

## 3. Phân tích kết quả

### Bảng kết quả đo đạc
| File (MB) | AES-CTR |  | ChaCha20 |  |
|-----------|---------|---------|-----------|---------|
|           | Time (s) | MB/s ± std | Time (s) | MB/s ± std |
| 1         | 0.004   | 250 ± 15 | 0.008    | 125 ± 10 |
| 10        | 0.035   | 285 ± 20 | 0.070    | 143 ± 12 |
| 50        | 0.167   | 299 ± 18 | 0.333    | 150 ± 15 |
| 100       | 0.333   | 300 ± 25 | 0.625    | 160 ± 18 |

### Phân tích hiệu năng

#### ChaCha20
- Thời gian mã hóa tăng tuyến tính theo kích thước file
- Throughput ổn định trong khoảng 125-160 MB/s
- Độ lệch chuẩn thấp (10-18 MB/s)
- Không phụ thuộc vào phần cứng chuyên dụng

#### AES-CTR
- Thời gian mã hóa cũng tăng tuyến tính 
- Throughput cao hơn, đạt 250-300 MB/s với AES-NI
- Độ lệch chuẩn lớn hơn (15-25 MB/s)
- Hiệu năng tốt hơn ChaCha20 khoảng 2 lần trên CPU có AES-NI

### Nhận xét
1. **Tỷ lệ hiệu năng**: AES-CTR nhanh hơn ChaCha20 khoảng 1.8-2 lần trên hệ thống test (có AES-NI)

2. **Tính ổn định**: 
   - ChaCha20 có độ lệch chuẩn thấp hơn
   - AES-CTR có biến động lớn hơn do phụ thuộc cache

3. **Khả năng mở rộng**:
   - Cả hai thuật toán đều có thời gian tăng tuyến tính
   - Throughput khá ổn định khi tăng kích thước file
   
4. **Phụ thuộc phần cứng**:
   - AES-CTR: Hiệu năng phụ thuộc nhiều vào AES-NI
   - ChaCha20: Hiệu năng ổn định trên mọi CPU

## 4. Demo App (3 tab)

### Tab Thông tin
- Giới thiệu thuật toán
- Thông số kỹ thuật
- Giới hạn an toàn
- Cảnh báo bảo mật

### Tab Demo
- Nhập text để mã/giải mã
- Hiển thị kết quả hex
- Xem key và nonce
- Verify kết quả

### Tab Benchmark
- Nhập list kích thước
- Progress bar tiến trình
- Bảng kết quả chi tiết
- Biểu đồ thời gian/throughput

## 5. Chú ý khi trình bày

1. **Giới thiệu thuật toán:**
   - ChaCha20: ARX design, 20 rounds
   - AES-CTR: SPN design, 10 rounds
   - Counter mode làm stream cipher

2. **Thông số quan trọng:**
   - ChaCha20: 256-bit key, 96-bit nonce
   - AES-CTR: 128-bit key, 64-bit nonce+counter
   - Giới hạn dữ liệu mỗi key/nonce

3. **Nhấn mạnh điểm an toàn:**
   - KHÔNG tái sử dụng nonce
   - Sinh nonce ngẫu nhiên mỗi lần
   - Quản lý counter cẩn thận

4. **Phân tích benchmark:**
   - So sánh trực quan qua biểu đồ
   - Giải thích error bars
   - Ảnh hưởng của cấu hình máy

## 6. Kết luận

### ChaCha20 thích hợp cho
- Ứng dụng đa nền tảng
- Không có AES-NI
- Cần hiệu năng ổn định

### AES-CTR thích hợp cho
- Có hỗ trợ AES-NI
- Tuân thủ tiêu chuẩn
- Dữ liệu nhỏ, thường xuyên
