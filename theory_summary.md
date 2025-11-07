# Lý thuyết về mã hóa dòng và mã hóa khối

## 1. ChaCha20 (Mã hóa dòng)

### 1.1. Giới thiệu
ChaCha20 là một thuật toán mã hóa dòng được thiết kế bởi Daniel J. Bernstein vào năm 2008. Đây là phiên bản cải tiến của thuật toán Salsa20, với cải tiến về hiệu năng và bảo mật. ChaCha20 được sử dụng rộng rãi trong các giao thức bảo mật hiện đại như TLS 1.3.

### 1.2. Cấu trúc
ChaCha20 hoạt động dựa trên một ma trận trạng thái 4x4 với các số 32-bit:
```
cccccccc  cccccccc  cccccccc  cccccccc
kkkkkkkk  kkkkkkkk  kkkkkkkk  kkkkkkkk
kkkkkkkk  kkkkkkkk  kkkkkkkk  kkkkkkkk
bbbbbbbb  nnnnnnnn  nnnnnnnn  nnnnnnnn
```
Trong đó:
- c: Hằng số "expand 32-byte k"
- k: Khóa 256-bit (32 byte)
- b: Bộ đếm 32-bit
- n: Nonce 96-bit (12 byte)

### 1.3. Nguyên lý hoạt động
1. **Khởi tạo trạng thái**: Tạo ma trận 4x4 với khóa, nonce và bộ đếm
2. **Vòng lặp chính**: Thực hiện 20 vòng (10 vòng đôi)
   - Mỗi vòng đôi gồm:
     - 4 phép biến đổi quarter-round theo cột
     - 4 phép biến đổi quarter-round theo đường chéo
3. **Tạo keystream**: Cộng trạng thái cuối với trạng thái ban đầu
4. **Mã hóa**: XOR keystream với plaintext

## 2. AES-CTR (Mã hóa khối ở chế độ CTR)

### 2.1. Giới thiệu
AES (Advanced Encryption Standard) là thuật toán mã hóa khối tiêu chuẩn được NIST chọn vào năm 2001. CTR (Counter) là một chế độ hoạt động biến AES thành mã hóa dòng.

### 2.2. Cấu trúc AES-128
1. **Khóa**: 128 bit (16 byte)
2. **Kích thước khối**: 128 bit
3. **Ma trận trạng thái**: 4x4 byte
4. **Số vòng**: 10 vòng

### 2.3. Chế độ CTR
CTR mode biến đổi mã hóa khối thành mã hóa dòng bằng cách:
1. Tạo một chuỗi các giá trị bộ đếm
2. Mã hóa các giá trị bộ đếm để tạo keystream
3. XOR keystream với plaintext

### 2.4. Ưu điểm của CTR mode
1. Cho phép xử lý song song
2. Không cần padding
3. Mã hóa và giải mã sử dụng cùng một thuật toán
4. Truy cập ngẫu nhiên vào dữ liệu đã mã hóa

## 3. So sánh ChaCha20 và AES-CTR

### 3.1. Hiệu năng
- **ChaCha20**: 
  - Hiệu quả trên phần cứng không chuyên dụng
  - Tốc độ cao với dữ liệu lớn
  - Không yêu cầu bảng tra cứu

- **AES-CTR**:
  - Hiệu quả trên phần cứng có hỗ trợ AES-NI
  - Ổn định với mọi kích thước dữ liệu
  - Yêu cầu bảng tra cứu S-box

### 3.2. Bảo mật
- **ChaCha20**:
  - Thiết kế đơn giản, dễ phân tích
  - Không có tấn công hiệu quả đã biết
  - Margin bảo mật tốt với 20 vòng

- **AES-CTR**:
  - Đã được phân tích kỹ lưỡng
  - Tiêu chuẩn toàn cầu
  - Được hỗ trợ rộng rãi trong phần cứng