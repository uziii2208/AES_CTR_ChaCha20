from time import time
import os
from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np

class ChaCha20:
    def __init__(self, key: bytes, nonce: bytes):
        if len(key) != 32:
            raise ValueError("Khóa phải có độ dài 32 bytes")
        if len(nonce) != 12:
            raise ValueError("Nonce phải có độ dài 12 bytes")
        
        self.state = list(b"expand 32-byte k") + list(key) + [0, 0, 0, 0] + list(nonce)
    
    def quarter_round(self, a: int, b: int, c: int, d: int) -> None:
        a = (a + b) & 0xFFFFFFFF
        d = d ^ a
        d = ((d << 16) & 0xFFFFFFFF) | (d >> 16)
        
        c = (c + d) & 0xFFFFFFFF
        b = b ^ c
        b = ((b << 12) & 0xFFFFFFFF) | (b >> 20)
        
        a = (a + b) & 0xFFFFFFFF
        d = d ^ a
        d = ((d << 8) & 0xFFFFFFFF) | (d >> 24)
        
        c = (c + d) & 0xFFFFFFFF
        b = b ^ c
        b = ((b << 7) & 0xFFFFFFFF) | (b >> 25)
        
        return a, b, c, d

    def block_function(self, counter: int = 0) -> bytes:
        # Cập nhật bộ đếm trong trạng thái
        self.state[12] = counter
        
        # Sao chép trạng thái làm việc
        state = self.state.copy()
        working_state = state.copy()
        
        # 20 vòng (10 vòng đôi)
        for _ in range(10):
            # Vòng theo cột
            state[0], state[4], state[8], state[12] = self.quarter_round(state[0], state[4], state[8], state[12])
            state[1], state[5], state[9], state[13] = self.quarter_round(state[1], state[5], state[9], state[13])
            state[2], state[6], state[10], state[14] = self.quarter_round(state[2], state[6], state[10], state[14])
            state[3], state[7], state[11], state[15] = self.quarter_round(state[3], state[7], state[11], state[15])
            
            # Vòng theo đường chéo
            state[0], state[5], state[10], state[15] = self.quarter_round(state[0], state[5], state[10], state[15])
            state[1], state[6], state[11], state[12] = self.quarter_round(state[1], state[6], state[11], state[12])
            state[2], state[7], state[8], state[13] = self.quarter_round(state[2], state[7], state[8], state[13])
            state[3], state[4], state[9], state[14] = self.quarter_round(state[3], state[4], state[9], state[14])
        
        # Cộng với trạng thái ban đầu
        for i in range(16):
            state[i] = (state[i] + working_state[i]) & 0xFFFFFFFF
        
        # Chuyển đổi thành bytes và trả về
        return b''.join(x.to_bytes(4, 'little') for x in state)

    def encrypt(self, plaintext: bytes) -> bytes:
        encrypted = bytearray(len(plaintext))
        for i in range(0, len(plaintext), 64):
            keystream = self.block_function(i // 64)
            chunk = plaintext[i:i + 64]
            for j, (a, b) in enumerate(zip(chunk, keystream)):
                encrypted[i + j] = a ^ b
        return bytes(encrypted)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.encrypt(ciphertext)  # ChaCha20 sử dụng cùng một hàm cho mã hóa và giải mã

def generate_test_file(size_mb: int) -> str:
    """Tạo file test với kích thước được chỉ định (MB)"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    filename = os.path.join(data_dir, f"test_{size_mb}MB.txt")
    os.makedirs(data_dir, exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    return filename

def benchmark_chacha20(file_sizes: list) -> Tuple[list, list]:
    """Đo hiệu năng ChaCha20 với các kích thước file khác nhau"""
    key = os.urandom(32)
    nonce = os.urandom(12)
    times = []
    throughputs = []
    cipher = ChaCha20(key, nonce)  # Tạo cipher một lần
    
    for size in file_sizes:
        # Tạo dữ liệu trực tiếp trong bộ nhớ thay vì qua file
        data = os.urandom(size * 1024 * 1024)  # Tạo dữ liệu ngẫu nhiên
        
        # Chạy warm-up để tránh ảnh hưởng của JIT
        cipher.encrypt(os.urandom(1024))
        
        # Đo thời gian mã hóa (lấy trung bình của 3 lần chạy)
        times_run = []
        for _ in range(3):
            start_time = time()
            encrypted = cipher.encrypt(data)
            end_time = time()
            times_run.append(end_time - start_time)
        
        # Lấy thời gian trung bình
        encryption_time = sum(times_run) / len(times_run)
        throughput = (size * 1024 * 1024) / (encryption_time * 1024 * 1024)  # MB/s
        
        times.append(encryption_time)
        throughputs.append(throughput)
        
        # Đảm bảo giải phóng bộ nhớ
        del data
        del encrypted
    
    return times, throughputs

def get_algorithm_info() -> str:
    """Trả về thông tin về thuật toán ChaCha20"""
    return """ChaCha20 - Thuật toán mã hóa dòng hiện đại
    
• Đặc điểm:
  - Được thiết kế bởi Daniel J. Bernstein năm 2008
  - Là phiên bản cải tiến của Salsa20
  - Sử dụng phép XOR và phép quay bit
  - Độ dài khóa: 256 bit (32 bytes)
  - Độ dài nonce: 96 bit (12 bytes)
  
• Ưu điểm:
  - Tốc độ cao trên phần cứng thông thường
  - An toàn về mặt mật mã học
  - Không yêu cầu bảng tra cứu (lookup tables)
  - Chống lại các tấn công timing
  
• Cấu trúc:
  - Ma trận trạng thái 4x4 (16 từ 32-bit)
  - 20 vòng (10 vòng đôi)
  - Mỗi vòng gồm 4 phép quarter-round
  
• Ứng dụng:
  - TLS 1.3
  - Mã hóa đường truyền
  - Bảo mật IoT
  - Mã hóa dữ liệu lưu trữ"""

def plot_results(file_sizes: list, chacha_times: list, chacha_throughputs: list):
    """Vẽ biểu đồ kết quả"""
    # Thiết lập style mặc định đẹp hơn
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['lines.linewidth'] = 2
    
    plt.figure(figsize=(12, 5))
    
    # Biểu đồ thời gian
    plt.subplot(1, 2, 1)
    plt.plot(file_sizes, chacha_times, 'b-o', label='ChaCha20', linewidth=2)
    plt.xlabel('Kích thước file (MB)')
    plt.ylabel('Thời gian mã hóa (giây)')
    plt.title('Thời gian mã hóa theo kích thước file')
    plt.legend()
    plt.grid(True)
    
    # Biểu đồ throughput
    plt.subplot(1, 2, 2)
    plt.plot(file_sizes, chacha_throughputs, 'r-o', label='ChaCha20', linewidth=2)
    plt.xlabel('Kích thước file (MB)')
    plt.ylabel('Throughput (MB/s)')
    plt.title('Throughput theo kích thước file')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    
    # Thêm thông tin về cấu hình
    plt.figtext(0.02, 0.02, f'Benchmark time: {time():.0f}', fontsize=8)
    
    try:
        # Lưu biểu đồ
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Lưu file tạm để test quyền ghi
        test_file = os.path.join(data_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        # Lưu biểu đồ với đường dẫn tuyệt đối
        output_file = os.path.join(data_dir, 'chacha20_performance.png')
        if os.path.exists(output_file):
            os.remove(output_file)  # Xóa file cũ nếu tồn tại
        plt.savefig(output_file, dpi=300, bbox_inches='tight', format='png')
    except Exception as e:
        print(f"Lỗi khi lưu biểu đồ: {str(e)}")
        # Thử lưu vào thư mục hiện tại
        plt.savefig('chacha20_performance.png', dpi=300, bbox_inches='tight', format='png')
    finally:
        plt.close()

def demo_encryption(text: str, key: bytes = None, nonce: bytes = None) -> Tuple[bytes, bytes, bytes]:
    """Demo mã hóa/giải mã với text"""
    if key is None:
        key = os.urandom(32)
    if nonce is None:
        nonce = os.urandom(12)
    
    cipher = ChaCha20(key, nonce)
    plaintext = text.encode('utf-8')
    encrypted = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(encrypted)
    
    return encrypted, key, nonce

def create_gui():
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    from tkinter.font import Font
    
    def run_benchmark():
        try:
            # Lấy giá trị từ các input
            sizes = [int(size.strip()) for size in file_sizes_entry.get().split(',')]
            if not sizes:
                raise ValueError("Vui lòng nhập ít nhất một kích thước file")
            if any(size <= 0 for size in sizes):
                raise ValueError("Kích thước file phải lớn hơn 0")
        except ValueError as e:
            output_text.delete('1.0', tk.END)
            output_text.insert(tk.END, f"Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", str(e))
            return
        
        # Xóa nội dung cũ
        output_text.delete('1.0', tk.END)
        output_text.insert(tk.END, "Bắt đầu đánh giá hiệu năng ChaCha20...\n")
        
        # Cập nhật UI
        progress_var.set(0)
        root.update()
        
        # Chạy benchmark
        times, throughputs = benchmark_chacha20(sizes)
        
        # Hiển thị kết quả
        output_text.insert(tk.END, "\nKết quả đánh giá hiệu năng ChaCha20:\n")
        for i, size in enumerate(sizes):
            output_text.insert(tk.END, f"\nKích thước file: {size}MB\n")
            output_text.insert(tk.END, f"Thời gian mã hóa: {times[i]:.2f} giây\n")
            output_text.insert(tk.END, f"Throughput: {throughputs[i]:.2f} MB/s\n")
            progress_var.set((i + 1) / len(sizes) * 100)
            root.update()
        
        try:
            plot_results(sizes, times, throughputs)
            output_text.insert(tk.END, "\nĐã lưu biểu đồ kết quả vào 'data/chacha20_performance.png'\n")
        except Exception as e:
            output_text.insert(tk.END, f"\nLỗi khi lưu biểu đồ: {str(e)}\n")
        finally:
            progress_var.set(100)

    # Tạo cửa sổ chính
    root = tk.Tk()
    root.title("ChaCha20 Demo & Benchmark")
    root.geometry("800x600")

    # Tạo style
    style = ttk.Style()
    style.configure('TNotebook.Tab', padding=[20, 5])
    
    # Tạo notebook để chứa các tab
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Tab Demo
    demo_frame = ttk.Frame(notebook, padding="10")
    notebook.add(demo_frame, text="Demo Mã hóa/Giải mã")
    
    # Frame cho input trong tab demo
    input_frame = ttk.LabelFrame(demo_frame, text="Nhập text để mã hóa", padding="10")
    input_frame.pack(fill=tk.X, pady=5)
    
    demo_text = scrolledtext.ScrolledText(input_frame, height=5)
    demo_text.pack(fill=tk.X)
    demo_text.insert('1.0', "Nhập văn bản để mã hóa tại đây...")
    
    # Frame cho output trong tab demo
    output_frame = ttk.LabelFrame(demo_frame, text="Kết quả", padding="10")
    output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    demo_output = scrolledtext.ScrolledText(output_frame, height=10)
    demo_output.pack(fill=tk.BOTH, expand=True)
    
    def run_demo():
        try:
            text = demo_text.get('1.0', tk.END).strip()
            if not text:
                raise ValueError("Vui lòng nhập text để mã hóa")
            
            encrypted, key, nonce = demo_encryption(text)
            
            demo_output.delete('1.0', tk.END)
            demo_output.insert(tk.END, "=== Demo ChaCha20 ===\\n\\n")
            demo_output.insert(tk.END, f"Plaintext: {text}\\n\\n")
            demo_output.insert(tk.END, f"Encrypted (hex): {encrypted.hex()}\\n\\n")
            demo_output.insert(tk.END, f"Key (hex): {key.hex()}\\n")
            demo_output.insert(tk.END, f"Nonce (hex): {nonce.hex()}\\n")
            
            # Giải mã để kiểm tra
            cipher = ChaCha20(key, nonce)
            decrypted = cipher.decrypt(encrypted)
            demo_output.insert(tk.END, f"\\nDecrypted: {decrypted.decode('utf-8')}\\n")
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    
    ttk.Button(demo_frame, text="Chạy Demo", command=run_demo).pack(pady=5)
    
    # Tab Info
    info_frame = ttk.Frame(notebook, padding="10")
    notebook.add(info_frame, text="Thông tin ChaCha20")
    
    info_text = scrolledtext.ScrolledText(info_frame, height=20, font=('Consolas', 10))
    info_text.pack(fill=tk.BOTH, expand=True)
    info_text.insert('1.0', get_algorithm_info())
    info_text.configure(state='disabled')
    
    # Tab Benchmark
    benchmark_frame = ttk.Frame(notebook, padding="10")
    notebook.add(benchmark_frame, text="Benchmark Hiệu năng")
    
    # Frame cho controls
    control_frame = ttk.LabelFrame(benchmark_frame, text="Cấu hình Benchmark", padding="10")
    control_frame.pack(fill=tk.X)
    
    # Input cho kích thước file
    ttk.Label(control_frame, text="Kích thước file (MB, phân cách bằng dấu phẩy):").pack(side=tk.LEFT)
    file_sizes_entry = ttk.Entry(control_frame, width=30)
    file_sizes_entry.insert(0, "1, 10, 50")
    file_sizes_entry.pack(side=tk.LEFT, padx=5)
    
    # Nút chạy benchmark
    ttk.Button(control_frame, text="Chạy Benchmark", command=run_benchmark).pack(side=tk.LEFT, padx=5)
    
    # Progress bar
    progress_var = tk.DoubleVar()
    ttk.Progressbar(benchmark_frame, length=780, variable=progress_var, mode='determinate').pack(pady=10)
    
    # Output text area cho benchmark
    output_text = scrolledtext.ScrolledText(benchmark_frame, height=15)
    output_text.pack(pady=10, fill=tk.BOTH, expand=True)
    
    root.mainloop()

def main():
    create_gui()

if __name__ == "__main__":
    main()