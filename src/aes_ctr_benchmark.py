from Crypto.Cipher import AES
from Crypto.Util import Counter
import os
from time import time
from typing import Tuple
import matplotlib.pyplot as plt

def get_algorithm_info() -> str:
    """Trả về thông tin về thuật toán AES-CTR"""
    return """AES-CTR (Advanced Encryption Standard - Counter Mode)
    
• Đặc điểm:
  - AES: Tiêu chuẩn mã hóa tiên tiến, được NIST chọn năm 2001
  - CTR Mode: Chế độ hoạt động biến khối cipher thành stream cipher
  - Độ dài khóa: 128 bit (AES-128)
  - Độ dài nonce: 64 bit + 64 bit counter
  
• Ưu điểm:
  - Tốc độ cao nhờ khả năng song song hóa
  - Không cần padding
  - Dễ dàng xử lý từng byte
  - Hỗ trợ random access
  - Có phần cứng chuyên dụng (AES-NI)
  
• Cấu trúc:
  - AES: SPN (Substitution-Permutation Network)
  - 10 vòng cho AES-128
  - CTR: Tạo keystream bằng mã hóa counter
  
• Ứng dụng:
  - TLS/SSL
  - Disk encryption
  - VPN
  - Bảo mật IoT"""

def demo_encryption(text: str) -> Tuple[bytes, bytes, bytes]:
    """Demo mã hóa/giải mã với text"""
    key = os.urandom(16)
    nonce = os.urandom(8)
    ctr = Counter.new(64, prefix=nonce, initial_value=0)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    
    plaintext = text.encode('utf-8')
    encrypted = cipher.encrypt(plaintext)
    
    # Tạo cipher mới cho giải mã vì CTR không thể reuse
    ctr = Counter.new(64, prefix=nonce, initial_value=0)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    decrypted = cipher.decrypt(encrypted)
    
    return encrypted, key, nonce

def generate_test_file(size_mb: int) -> str:
    """Tạo file test với kích thước được chỉ định (MB)"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    filename = os.path.join(data_dir, f"test_{size_mb}MB.txt")
    os.makedirs(data_dir, exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    return filename

def benchmark_aes_ctr(file_sizes: list) -> Tuple[list, list]:
    """Đo hiệu năng AES-CTR với các kích thước file khác nhau"""
    key = os.urandom(16)  # AES-128 sử dụng khóa 16 bytes
    times = []
    throughputs = []
    
    # Warm-up để JIT compilation
    nonce = os.urandom(8)
    ctr = Counter.new(64, prefix=nonce, initial_value=0)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    cipher.encrypt(os.urandom(1024))
    
    for size in file_sizes:
        # Tạo dữ liệu trực tiếp trong bộ nhớ
        data = os.urandom(size * 1024 * 1024)
        
        # Đo thời gian mã hóa (lấy trung bình của 3 lần chạy)
        times_run = []
        for _ in range(3):
            # Tạo cipher mới cho mỗi lần chạy
            nonce = os.urandom(8)
            ctr = Counter.new(64, prefix=nonce, initial_value=0)
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            
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

def plot_results(file_sizes: list, aes_times: list, aes_throughputs: list):
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
    plt.plot(file_sizes, aes_times, 'g-o', label='AES-CTR', linewidth=2, markersize=8)
    plt.xlabel('Kích thước file (MB)', fontsize=10)
    plt.ylabel('Thời gian mã hóa (giây)', fontsize=10)
    plt.title('Thời gian mã hóa theo kích thước file', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Biểu đồ throughput
    plt.subplot(1, 2, 2)
    plt.plot(file_sizes, aes_throughputs, 'r-o', label='AES-CTR', linewidth=2, markersize=8)
    plt.xlabel('Kích thước file (MB)', fontsize=10)
    plt.ylabel('Throughput (MB/s)', fontsize=10)
    plt.title('Throughput theo kích thước file', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
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
        output_file = os.path.join(data_dir, 'aes_ctr_performance.png')
        if os.path.exists(output_file):
            os.remove(output_file)  # Xóa file cũ nếu tồn tại
        plt.savefig(output_file, dpi=300, bbox_inches='tight', format='png')
    except Exception as e:
        print(f"Lỗi khi lưu biểu đồ: {str(e)}")
        # Thử lưu vào thư mục hiện tại
        plt.savefig('aes_ctr_performance.png', dpi=300, bbox_inches='tight', format='png')
    finally:
        plt.close()

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
        output_text.insert(tk.END, "Bắt đầu đánh giá hiệu năng AES-CTR...\n")
        
        # Cập nhật UI
        progress_var.set(0)
        root.update()
        
        # Chạy benchmark
        times, throughputs = benchmark_aes_ctr(sizes)
        
        # Hiển thị kết quả
        output_text.insert(tk.END, "\nKết quả đánh giá hiệu năng AES-CTR:\n")
        for i, size in enumerate(sizes):
            output_text.insert(tk.END, f"\nKích thước file: {size}MB\n")
            output_text.insert(tk.END, f"Thời gian mã hóa: {times[i]:.2f} giây\n")
            output_text.insert(tk.END, f"Throughput: {throughputs[i]:.2f} MB/s\n")
            progress_var.set((i + 1) / len(sizes) * 100)
            root.update()
        
        try:
            plot_results(sizes, times, throughputs)
            output_text.insert(tk.END, "\nĐã lưu biểu đồ kết quả vào 'data/aes_ctr_performance.png'\n")
        except Exception as e:
            output_text.insert(tk.END, f"\nLỗi khi lưu biểu đồ: {str(e)}\n")
        finally:
            progress_var.set(100)

    # Tạo cửa sổ chính
    root = tk.Tk()
    root.title("AES-CTR Demo & Benchmark")
    root.geometry("800x600")

    # Tạo style
    style = ttk.Style()
    style.configure('TNotebook.Tab', padding=[20, 5])
    
    # Tạo notebook để chứa các tab
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Tab Info
    info_frame = ttk.Frame(notebook, padding="10")
    notebook.add(info_frame, text="Thông tin AES-CTR")
    
    info_text = scrolledtext.ScrolledText(info_frame, height=20, font=('Consolas', 10))
    info_text.pack(fill=tk.BOTH, expand=True)
    info_text.insert('1.0', get_algorithm_info())
    info_text.configure(state='disabled')
    
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
            demo_output.insert(tk.END, "=== Demo AES-CTR ===\n\n")
            demo_output.insert(tk.END, f"Plaintext: {text}\n\n")
            demo_output.insert(tk.END, f"Encrypted (hex): {encrypted.hex()}\n\n")
            demo_output.insert(tk.END, f"Key (hex): {key.hex()}\n")
            demo_output.insert(tk.END, f"Nonce (hex): {nonce.hex()}\n")
            
            # Giải mã để kiểm tra
            ctr = Counter.new(64, prefix=nonce, initial_value=0)
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            decrypted = cipher.decrypt(encrypted)
            demo_output.insert(tk.END, f"\nDecrypted: {decrypted.decode('utf-8')}\n")
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    
    ttk.Button(demo_frame, text="Chạy Demo", command=run_demo).pack(pady=5)
    
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