# Đánh giá hiệu năng mã hóa dòng (ChaCha20) và mã hóa khối (AES-CTR)

## Cấu trúc dự án

```
project/
│
├── src/
│   ├── chacha20_benchmark.py    # Mã nguồn đánh giá ChaCha20
│   └── aes_ctr_benchmark.py     # Mã nguồn đánh giá AES-CTR
│
├── data/                        # Thư mục chứa kết quả và biểu đồ
│
├── theory_summary.md            # Tổng hợp lý thuyết
├── report.md                    # Báo cáo chi tiết
├── slides.tex                   # Slide trình bày
└── README.md                    # File hướng dẫn này
```

## Yêu cầu hệ thống

1. Python 3.8 trở lên
2. Các thư viện Python:
   - pycryptodome
   - matplotlib
3. TeXLive hoặc MiKTeX (để biên dịch slides)

## Cài đặt

1. Cài đặt các thư viện Python cần thiết:
```bash
pip install pycryptodome matplotlib
```

2. Cài đặt TeXLive hoặc MiKTeX từ trang chủ:
   - TeXLive: https://www.tug.org/texlive/
   - MiKTeX: https://miktex.org/

## Chạy chương trình

### 1. Đánh giá hiệu năng ChaCha20
```bash
python src/chacha20_benchmark.py
```
Kết quả sẽ được lưu trong file `chacha20_performance.png`

### 2. Đánh giá hiệu năng AES-CTR
```bash
python src/aes_ctr_benchmark.py
```
Kết quả sẽ được lưu trong file `aes_ctr_performance.png`

### 3. Biên dịch slide trình bày
```bash
pdflatex slides.tex
```
File PDF sẽ được tạo ra với tên `slides.pdf`

## Cấu trúc mã nguồn

### ChaCha20 (`chacha20_benchmark.py`)
- Cài đặt thuật toán ChaCha20 từ đầu
- Hàm tạo file test với kích thước tùy chọn
- Hàm benchmark và vẽ biểu đồ kết quả

### AES-CTR (`aes_ctr_benchmark.py`)
- Sử dụng thư viện pycryptodome cho AES
- Cấu hình mode CTR
- Hàm benchmark và vẽ biểu đồ kết quả

## Kết quả đầu ra

1. **Biểu đồ hiệu năng**
   - `chacha20_performance.png`: Biểu đồ thời gian và throughput của ChaCha20
   - `aes_ctr_performance.png`: Biểu đồ thời gian và throughput của AES-CTR

2. **Báo cáo**
   - `report.md`: Báo cáo chi tiết kết quả nghiên cứu
   - `theory_summary.md`: Tổng hợp lý thuyết về hai thuật toán

3. **Slide trình bày**
   - `slides.pdf`: File PDF được tạo ra sau khi biên dịch `slides.tex`

## Xử lý lỗi thường gặp

1. **Lỗi import thư viện**
   ```
   ModuleNotFoundError: No module named 'Crypto'
   ```
   Giải pháp: Cài đặt thư viện pycryptodome
   ```bash
   pip install pycryptodome
   ```

2. **Lỗi matplotlib**
   ```
   ModuleNotFoundError: No module named 'matplotlib'
   ```
   Giải pháp: Cài đặt thư viện matplotlib
   ```bash
   pip install matplotlib
   ```

3. **Lỗi biên dịch LaTeX**
   - Đảm bảo đã cài đặt gói `beamer`
   - Đảm bảo đã cài đặt gói `vietnam` cho hỗ trợ tiếng Việt

## Liên hệ hỗ trợ

Nếu gặp bất kỳ vấn đề nào, vui lòng tạo issue trên repository hoặc liên hệ trực tiếp với nhóm phát triển.

## Tài liệu tham khảo

1. Tài liệu về ChaCha20:
   - RFC 7539: ChaCha20 và Poly1305
   - Trang web của Daniel J. Bernstein

2. Tài liệu về AES:
   - FIPS 197: Advanced Encryption Standard
   - NIST Special Publication 800-38A