from time import time
import os
from typing import Tuple, List
import matplotlib.pyplot as plt
import numpy as np
from Crypto.Cipher import ChaCha20
import platform
import cpuinfo

def get_system_info() -> dict:
    """Lấy thông tin hệ thống"""
    cpu_info = cpuinfo.get_cpu_info()
    return {
        'cpu_brand': cpu_info['brand_raw'],
        'python_version': platform.python_version(),
        'os': f"{platform.system()} {platform.release()}",
        'architecture': platform.machine(),
        'pycryptodome_version': '3.19.0'  # Hoặc lấy động từ pkg_resources
    }

def benchmark_chacha20(file_sizes: List[int], num_runs: int = 10) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Đo hiệu năng ChaCha20 với các kích thước file khác nhau
    Returns:
        encrypt_times: Thời gian mã hóa trung bình
        encrypt_stds: Độ lệch chuẩn thời gian mã hóa
        decrypt_times: Thời gian giải mã trung bình
        decrypt_stds: Độ lệch chuẩn thời gian giải mã
    """
    key = os.urandom(32)  # ChaCha20 sử dụng khóa 256-bit
    encrypt_times = []
    encrypt_stds = []
    decrypt_times = []
    decrypt_stds = []
    
    for size in file_sizes:
        data = os.urandom(size * 1024 * 1024)  # Tạo dữ liệu ngẫu nhiên
        encrypt_runs = []
        decrypt_runs = []
        
        for _ in range(num_runs):
            # Mỗi lần chạy dùng nonce mới
            nonce = os.urandom(12)  # ChaCha20 IETF dùng nonce 96-bit
            
            # Đo thời gian mã hóa
            cipher = ChaCha20.new(key=key, nonce=nonce)
            start_time = time()
            encrypted = cipher.encrypt(data)
            encrypt_runs.append(time() - start_time)
            
            # Đo thời gian giải mã
            cipher = ChaCha20.new(key=key, nonce=nonce)
            start_time = time()
            decrypted = cipher.decrypt(encrypted)
            decrypt_runs.append(time() - start_time)
            
            # Verify kết quả
            assert data == decrypted, "Lỗi: Giải mã không khớp dữ liệu gốc!"
        
        # Tính trung bình và độ lệch chuẩn
        encrypt_times.append(np.mean(encrypt_runs))
        encrypt_stds.append(np.std(encrypt_runs))
        decrypt_times.append(np.mean(decrypt_runs))
        decrypt_stds.append(np.std(decrypt_runs))
        
        # Giải phóng bộ nhớ
        del data, encrypted, decrypted
    
    return encrypt_times, encrypt_stds, decrypt_times, decrypt_stds

def plot_results(file_sizes: List[int], 
                encrypt_times: List[float], encrypt_stds: List[float],
                decrypt_times: List[float], decrypt_stds: List[float]):
    """Vẽ biểu đồ kết quả với error bars"""
    system_info = get_system_info()
    
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['lines.linewidth'] = 2
    
    plt.figure(figsize=(15, 6))
    
    # Biểu đồ thời gian
    plt.subplot(1, 2, 1)
    plt.errorbar(file_sizes, encrypt_times, yerr=encrypt_stds, fmt='b-o', 
                label='Encryption', capsize=5, capthick=1, elinewidth=1)
    plt.errorbar(file_sizes, decrypt_times, yerr=decrypt_stds, fmt='r-o',
                label='Decryption', capsize=5, capthick=1, elinewidth=1)
    plt.xlabel('Kích thước file (MB)')
    plt.ylabel('Thời gian xử lý (giây)')
    plt.title('Thời gian mã hóa/giải mã theo kích thước file')
    plt.legend()
    plt.grid(True)
    
    # Biểu đồ throughput
    plt.subplot(1, 2, 2)
    encrypt_throughput = [(size * 1024 * 1024) / (time * 1024 * 1024) for size, time in zip(file_sizes, encrypt_times)]
    decrypt_throughput = [(size * 1024 * 1024) / (time * 1024 * 1024) for size, time in zip(file_sizes, decrypt_times)]
    encrypt_throughput_std = [throughput * (std/time) for throughput, std, time in zip(encrypt_throughput, encrypt_stds, encrypt_times)]
    decrypt_throughput_std = [throughput * (std/time) for throughput, std, time in zip(decrypt_throughput, decrypt_stds, decrypt_times)]
    
    plt.errorbar(file_sizes, encrypt_throughput, yerr=encrypt_throughput_std,
                fmt='b-o', label='Encryption', capsize=5, capthick=1, elinewidth=1)
    plt.errorbar(file_sizes, decrypt_throughput, yerr=decrypt_throughput_std,
                fmt='r-o', label='Decryption', capsize=5, capthick=1, elinewidth=1)
    plt.xlabel('Kích thước file (MB)')
    plt.ylabel('Throughput (MB/s)')
    plt.title('Throughput theo kích thước file')
    plt.legend()
    plt.grid(True)
    
    # Thêm thông tin cấu hình
    info_text = f'CPU: {system_info["cpu_brand"]}\n'
    info_text += f'OS: {system_info["os"]}\n'
    info_text += f'Python {system_info["python_version"]}, PyCryptodome {system_info["pycryptodome_version"]}'
    plt.figtext(0.02, 0.02, info_text, fontsize=8)
    
    plt.tight_layout()
    
    # Lưu biểu đồ
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'chacha20_performance.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Đã lưu biểu đồ tại: {output_file}")
    except Exception as e:
        print(f"Lỗi khi lưu biểu đồ: {str(e)}")
    finally:
        plt.close()

def get_algorithm_info() -> str:
    """Trả về thông tin về thuật toán ChaCha20"""
    return """ChaCha20 - Thuật toán mã hóa dòng hiện đại
    
• Đặc điểm:
  - Được thiết kế bởi Daniel J. Bernstein năm 2008
  - Phiên bản IETF (RFC 8439):
    + Khóa: 256-bit (32 bytes)
    + Nonce: 96-bit (12 bytes)
    + Counter: 32-bit
    + Giới hạn: 2^32 blocks (~256GB) mỗi cặp key/nonce
  
• Ưu điểm:
  - Tốc độ cao trên phần cứng thông thường
  - An toàn về mặt mật mã học
  - Không yêu cầu bảng tra cứu (lookup tables)
  - Chống lại các tấn công timing
  
• Cảnh báo:
  - KHÔNG được tái sử dụng nonce với cùng khóa
  - Nonce nên được sinh ngẫu nhiên hoặc counter
  - Cần giới hạn dữ liệu ở mức 256GB mỗi key/nonce
  
• Ứng dụng:
  - TLS 1.3
  - Mã hóa đường truyền
  - Bảo mật IoT
  - Mã hóa dữ liệu lưu trữ"""

def create_gui():
    """Tạo giao diện đồ họa cho demo và benchmark"""
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    
    def demo_encryption() -> Tuple[bytes, bytes, bytes]:
        """Demo mã hóa/giải mã với văn bản"""
        text = demo_text.get('1.0', tk.END).strip()
        if not text:
            raise ValueError("Vui lòng nhập text để mã hóa")
        
        key = os.urandom(32)
        nonce = os.urandom(12)
        plaintext = text.encode('utf-8')
        
        cipher = ChaCha20.new(key=key, nonce=nonce)
        encrypted = cipher.encrypt(plaintext)
        
        cipher = ChaCha20.new(key=key, nonce=nonce)
        decrypted = cipher.decrypt(encrypted)
        
        return encrypted, key, nonce, decrypted
    
    def run_demo():
        try:
            encrypted, key, nonce, decrypted = demo_encryption()
            
            demo_output.delete('1.0', tk.END)
            demo_output.insert(tk.END, "=== Demo ChaCha20 ===\n\n")
            demo_output.insert(tk.END, f"Plaintext: {demo_text.get('1.0', tk.END).strip()}\n\n")
            demo_output.insert(tk.END, f"Encrypted (hex): {encrypted.hex()}\n\n")
            demo_output.insert(tk.END, f"Key (hex): {key.hex()}\n")
            demo_output.insert(tk.END, f"Nonce (hex): {nonce.hex()}\n")
            demo_output.insert(tk.END, f"\nDecrypted: {decrypted.decode('utf-8')}\n")
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    
    def run_benchmark():
        try:
            sizes = [int(size.strip()) for size in file_sizes_entry.get().split(',')]
            if not sizes:
                raise ValueError("Vui lòng nhập ít nhất một kích thước file")
            if any(size <= 0 for size in sizes):
                raise ValueError("Kích thước file phải lớn hơn 0")
            
            output_text.delete('1.0', tk.END)
            output_text.insert(tk.END, "Bắt đầu benchmark ChaCha20...\n\n")
            progress_var.set(0)
            root.update()
            
            # Chạy benchmark
            encrypt_times, encrypt_stds, decrypt_times, decrypt_stds = benchmark_chacha20(sizes)
            
            # Hiển thị kết quả
            output_text.insert(tk.END, "Kết quả benchmark:\n\n")
            output_text.insert(tk.END, f"{'Size (MB)':>10} | {'Encrypt (MB/s)':>15} | {'Decrypt (MB/s)':>15}\n")
            output_text.insert(tk.END, "-" * 50 + "\n")
            
            for i, size in enumerate(sizes):
                encrypt_throughput = (size * 1024 * 1024) / (encrypt_times[i] * 1024 * 1024)
                decrypt_throughput = (size * 1024 * 1024) / (decrypt_times[i] * 1024 * 1024)
                output_text.insert(tk.END, 
                    f"{size:>10} | {encrypt_throughput:>6.2f} ± {encrypt_throughput*(encrypt_stds[i]/encrypt_times[i]):>5.2f} | "
                    f"{decrypt_throughput:>6.2f} ± {decrypt_throughput*(decrypt_stds[i]/decrypt_times[i]):>5.2f}\n")
                progress_var.set((i + 1) / len(sizes) * 100)
                root.update()
            
            # Vẽ và lưu biểu đồ
            plot_results(sizes, encrypt_times, encrypt_stds, decrypt_times, decrypt_stds)
            output_text.insert(tk.END, "\nĐã lưu biểu đồ kết quả vào data/chacha20_performance.png\n")
            progress_var.set(100)
            
        except Exception as e:
            output_text.insert(tk.END, f"\nLỗi: {str(e)}\n")
            messagebox.showerror("Lỗi", str(e))
    
    # Tạo cửa sổ chính
    root = tk.Tk()
    root.title("ChaCha20 Demo & Benchmark")
    root.geometry("800x600")
    
    # Tạo notebook tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Tab Info
    info_frame = ttk.Frame(notebook, padding="10")
    notebook.add(info_frame, text="Thông tin ChaCha20")
    
    info_text = scrolledtext.ScrolledText(info_frame, height=20, font=('Consolas', 10))
    info_text.pack(fill=tk.BOTH, expand=True)
    info_text.insert('1.0', get_algorithm_info())
    info_text.configure(state='disabled')
    
    # Tab Demo
    demo_frame = ttk.Frame(notebook, padding="10")
    notebook.add(demo_frame, text="Demo Mã hóa/Giải mã")
    
    input_frame = ttk.LabelFrame(demo_frame, text="Nhập text để mã hóa", padding="10")
    input_frame.pack(fill=tk.X, pady=5)
    
    demo_text = scrolledtext.ScrolledText(input_frame, height=5)
    demo_text.pack(fill=tk.X)
    demo_text.insert('1.0', "Nhập văn bản để mã hóa tại đây...")
    
    output_frame = ttk.LabelFrame(demo_frame, text="Kết quả", padding="10")
    output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    demo_output = scrolledtext.ScrolledText(output_frame, height=10)
    demo_output.pack(fill=tk.BOTH, expand=True)
    
    ttk.Button(demo_frame, text="Chạy Demo", command=run_demo).pack(pady=5)
    
    # Tab Benchmark
    benchmark_frame = ttk.Frame(notebook, padding="10")
    notebook.add(benchmark_frame, text="Benchmark")
    
    control_frame = ttk.LabelFrame(benchmark_frame, text="Cấu hình Benchmark", padding="10")
    control_frame.pack(fill=tk.X)
    
    ttk.Label(control_frame, text="Kích thước file (MB, phân cách bằng dấu phẩy):").pack(side=tk.LEFT)
    file_sizes_entry = ttk.Entry(control_frame, width=30)
    file_sizes_entry.insert(0, "1, 10, 50, 100")
    file_sizes_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Button(control_frame, text="Chạy Benchmark", command=run_benchmark).pack(side=tk.LEFT, padx=5)
    
    progress_var = tk.DoubleVar()
    ttk.Progressbar(benchmark_frame, length=780, variable=progress_var, mode='determinate').pack(pady=10)
    
    output_text = scrolledtext.ScrolledText(benchmark_frame, height=15, font=('Consolas', 10))
    output_text.pack(pady=10, fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
