import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import sys
import os
import pyinstxtractorcn
from datetime import datetime

class PyInstxtractorCN_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("pyinstxtractorcnGUI 1.0.9")
        self.root.geometry("800x650")
        self.root.configure(bg="#f0f0f0")

        self.file_path = ""
        self.base_output_dir = ""
        self.status_var = tk.StringVar(value="就绪")

        self._create_widgets()

        sys.stdout = self
        
    def _create_widgets(self):
        tk.Label(self.root, text="PyInstallerGUI 1.0.9", font=("黑体", 18, "bold"),
                 bg="#f0f0f0", fg="#2c3e50").pack(pady=15)
        
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        left_frame = tk.Frame(main_frame, bg="#e0e0e0", bd=2, relief=tk.GROOVE, width=220)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        left_frame.pack_propagate(False)

        btn_container = tk.Frame(left_frame, bg="#e0e0e0", padx=20, pady=20)
        btn_container.pack(anchor=tk.CENTER)
        
        tk.Button(btn_container, text="选择文件", command=self._select_file,
                  width=15, height=2, bg="#3498db", fg="white", font=("Arial", 10))\
            .pack(pady=8)
        
        tk.Button(btn_container, text="选择输出目录", command=self._select_output_dir,
                  width=15, height=2, bg="#2ecc71", fg="white", font=("Arial", 10))\
            .pack(pady=8)
        
        self.start_btn = tk.Button(btn_container, text="开始解包", command=self._start_extraction,
                                   width=15, height=2, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"))
        self.start_btn.pack(pady=20)
        
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.GROOVE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=10)
        
        self.info_text = tk.Text(right_frame, height=6, width=50, wrap=tk.WORD,
                                 font=("Consolas", 10), bg="white", fg="#333")
        self.info_text.pack(padx=15, pady=10, fill=tk.X)
        self._update_info()
        
        tk.Label(right_frame, text="操作日志", font=("Arial", 10, "bold"),
                 bg="white", fg="#2c3e50", anchor=tk.W)\
            .pack(padx=15, pady=(0, 5))
        
        self.log_area = scrolledtext.ScrolledText(right_frame, height=12, wrap=tk.WORD,
                                                  font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        self.log_area.pack(padx=15, pady=(0, 10), fill=tk.BOTH, expand=True)
        
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                 bg="#2c3e50", fg="white", anchor=tk.W)\
            .pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=5)
    
    def _update_info(self):
        """更新文件信息显示"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        file_info = f"文件：{'未选择' if not self.file_path else os.path.basename(self.file_path)}\n"
        output_dir = self._get_final_output_dir() or "未设置（将使用默认路径）"
        file_info += f"输出目录：{output_dir}"
        
        self.info_text.insert(tk.END, file_info)
        self.info_text.config(state=tk.DISABLED)
    
    def _get_final_output_dir(self):
        """获取最终解包目录（保留文件后缀名）"""
        if not self.file_path:
            return None

        full_filename = os.path.basename(self.file_path)
        extracted_dir = f"{full_filename}_extracted"
        
        if self.base_output_dir:
            return os.path.join(self.base_output_dir, extracted_dir)
        else:
            return os.path.join(os.path.dirname(self.file_path), extracted_dir)
    
    def _select_file(self):
        """选择待解包文件"""
        path = filedialog.askopenfilename(filetypes=[("EXE文件", "*.exe")])
        if path:
            self.file_path = path
            self._update_info()
            self.status_var.set(f"已选择文件：{os.path.basename(path)}")
            self._log(f"选择文件：{path}")
    
    def _select_output_dir(self):
        """选择输出目录"""
        path = filedialog.askdirectory(title="选择解包输出目录")
        if path:
            self.base_output_dir = path
            self._update_info()
            self.status_var.set(f"基础目录：{path}")
            self._log(f"设置基础目录：{path}")
    
    def _start_extraction(self):
        """启动解包流程（线程安全）"""
        if not self.file_path:
            self._show_error("请先选择待解包的EXE文件")
            return
        
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set("解包中...请稍候")
        self._log("开始解包操作")
        
        threading.Thread(target=self._perform_extraction, daemon=True).start()
    
    def _perform_extraction(self):
        """实际解包操作（在新线程执行）"""
        try:
            final_dir = self._get_final_output_dir()
            if not final_dir:
                raise ValueError("输出目录未正确生成")
            
            os.makedirs(final_dir, exist_ok=True)
            
            pyinstxtractorcn.dcp(self.file_path, final_dir)
            
            self._log(f"解包完成！文件保存至：{final_dir}")
            self.status_var.set(f"成功！结果保存至：{final_dir}")
            
        except pyinstxtractorcn.InvalidFileError:
            self._show_error("无效的PyInstaller打包文件")
        except Exception as e:
            self._show_error(f"解包失败：{str(e)}")
        finally:
            self.start_btn.config(state=tk.NORMAL)
    
    def _show_error(self, msg):
        """显示错误信息"""
        self.status_var.set(f"错误：{msg}")
        self._log(f"错误：{msg}")
    
    def _log(self, msg):
        """记录日志信息（线程安全）"""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        
        self.root.after(0, lambda: self.log_area.insert(tk.END, f"{timestamp} {msg}\n"))
        self.root.after(0, lambda: self.log_area.see(tk.END))
    
    def write(self, text):
        if text.strip() != '':
            self._log(text.rstrip())
    
    def flush(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PyInstxtractorCN_GUI(root)
    root.mainloop()
