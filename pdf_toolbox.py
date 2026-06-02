import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import fitz  # 用于PDF文本编辑（pymupdf库）

class PDFToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("本地PDF工具箱（含编辑功能）")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TCombobox", font=("SimHei", 10))
        
        # 选择功能的标签
        ttk.Label(root, text="选择操作：", font=("SimHei", 12, "bold")).pack(pady=10)
        
        # 功能选择下拉框
        self.functions = [
            "PDF合并", 
            "PDF拆分", 
            "提取页面", 
            "页面旋转",
            "PDF加密",
            "PDF解密",
            "添加文本（水印）"
        ]
        self.function_var = tk.StringVar(value=self.functions[0])
        self.function_combo = ttk.Combobox(
            root, 
            textvariable=self.function_var, 
            values=self.functions, 
            state="readonly",
            width=30
        )
        self.function_combo.pack(pady=5)
        self.function_combo.bind("<<ComboboxSelected>>", self.update_ui)
        
        # 创建操作区域框架
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 初始化UI
        self.update_ui(None)
        
        # 执行按钮
        self.execute_btn = ttk.Button(
            root, 
            text="执行操作", 
            command=self.execute_function,
            width=20
        )
        self.execute_btn.pack(pady=20)
        
        # 状态标签
        self.status_var = tk.StringVar(value="请选择操作并设置参数")
        ttk.Label(root, textvariable=self.status_var, foreground="blue").pack(pady=10)
    
    def update_ui(self, event):
        # 清空当前框架
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        func = self.function_var.get()
        
        if func == "PDF合并":
            self.create_merge_ui()
        elif func == "PDF拆分":
            self.create_split_ui()
        elif func == "提取页面":
            self.create_extract_ui()
        elif func == "页面旋转":
            self.create_rotate_ui()
        elif func == "PDF加密":
            self.create_encrypt_ui()
        elif func == "PDF解密":
            self.create_decrypt_ui()
        elif func == "添加文本（水印）":
            self.create_add_text_ui()
    
    # 添加文本（水印）的UI
    def create_add_text_ui(self):
        ttk.Label(self.frame, text="选择要编辑的PDF文件：").pack(anchor="w", pady=5)
        self.text_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.text_file_var, width=55).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择文件", 
            command=lambda: self.select_single_file("text")
        ).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text="要添加的文本内容：").pack(anchor="w", pady=5)
        self.text_content_var = tk.StringVar(value="机密")
        ttk.Entry(self.frame, textvariable=self.text_content_var, width=55).pack(anchor="w", pady=2)
        
        # 文本位置和样式设置
        frame_layout = ttk.Frame(self.frame)
        frame_layout.pack(anchor="w", fill="x", pady=5)
        
        # 页码设置
        ttk.Label(frame_layout, text="应用页码（如：1-3 或留空全部）：").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.text_pages_var = tk.StringVar(value="")
        ttk.Entry(frame_layout, textvariable=self.text_pages_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        # 字体大小
        ttk.Label(frame_layout, text="字体大小：").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.text_size_var = tk.StringVar(value="48")
        ttk.Entry(frame_layout, textvariable=self.text_size_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # 颜色选择
        self.text_color = "#FF0000"  # 默认红色
        ttk.Label(frame_layout, text="文本颜色：").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.color_label = ttk.Label(frame_layout, text="", background=self.text_color, width=5)
        self.color_label.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        ttk.Button(
            frame_layout, 
            text="选择颜色", 
            command=self.choose_text_color
        ).grid(row=2, column=2, padx=5, pady=2, sticky="w")
        
        # 旋转角度（使用下拉框限制可选值）
        ttk.Label(frame_layout, text="旋转角度：").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.text_rotate_var = tk.StringVar(value="45")
        # 限制旋转角度为常用值，避免无效输入
        ttk.Combobox(
            frame_layout, 
            textvariable=self.text_rotate_var, 
            values=["0", "45", "90", "135", "180", "225", "270", "315"], 
            state="readonly",
            width=10
        ).grid(row=3, column=1, padx=5, pady=2)
        
        # 输出路径
        ttk.Label(self.frame, text="输出文件路径：").pack(anchor="w", pady=5)
        self.text_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.text_output_var, width=55).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择保存位置", 
            command=lambda: self.select_output_path("text")
        ).pack(anchor="w", pady=5)
    
    # 颜色选择器
    def choose_text_color(self):
        color = colorchooser.askcolor(title="选择文本颜色")[1]
        if color:
            self.text_color = color
            self.color_label.config(background=color)
    
    # 颜色转换函数
    def hex_to_rgb(self, hex_color):
        """将十六进制颜色（如#FF0000）转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
    
    # 合并功能UI
    def create_merge_ui(self):
        ttk.Label(self.frame, text="选择要合并的PDF文件（可多选）：").pack(anchor="w", pady=5)
        self.merge_files = []
        self.merge_files_var = tk.StringVar(value="未选择文件")
        ttk.Label(self.frame, textvariable=self.merge_files_var).pack(anchor="w", pady=2)
        
        ttk.Button(
            self.frame, 
            text="选择文件", 
            command=lambda: self.select_files("merge")
        ).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text="输出文件路径：").pack(anchor="w", pady=5)
        self.merge_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.merge_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择保存位置", 
            command=lambda: self.select_output_path("merge")
        ).pack(anchor="w", pady=5)
    
    # 拆分功能UI
    def create_split_ui(self):
        ttk.Label(self.frame, text="选择要拆分的PDF文件：").pack(anchor="w", pady=5)
        self.split_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.split_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择文件", 
            command=lambda: self.select_single_file("split")
        ).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text="拆分页码（如：1-3,5 或留空拆分成单页）：").pack(anchor="w", pady=5)
        self.split_pages_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.split_pages_var, width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text="输出文件夹：").pack(anchor="w", pady=5)
        self.split_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.split_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择文件夹", 
            command=lambda: self.select_output_folder("split")
        ).pack(anchor="w", pady=5)
    
    # 提取页面UI
    def create_extract_ui(self):
        ttk.Label(self.frame, text="选择源PDF文件：").pack(anchor="w", pady=5)
        self.extract_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.extract_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择文件", 
            command=lambda: self.select_single_file("extract")
        ).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text="提取页码（如：1,3-5）：").pack(anchor="w", pady=5)
        self.extract_pages_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.extract_pages_var, width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text="输出文件路径：").pack(anchor="w", pady=5)
        self.extract_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.extract_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择保存位置", 
            command=lambda: self.select_output_path("extract")
        ).pack(anchor="w", pady=5)
    
    # 页面旋转UI
    def create_rotate_ui(self):
        ttk.Label(self.frame, text="选择要旋转的PDF文件：").pack(anchor="w", pady=5)
        self.rotate_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.rotate_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择文件", 
            command=lambda: self.select_single_file("rotate")
        ).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text="旋转页码（如：1-3 或留空旋转所有页）：").pack(anchor="w", pady=5)
        self.rotate_pages_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.rotate_pages_var, width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text="旋转角度：").pack(anchor="w", pady=5)
        self.rotate_angle_var = tk.StringVar(value="90")
        ttk.Combobox(
            self.frame, 
            textvariable=self.rotate_angle_var, 
            values=["90", "180", "270"], 
            state="readonly",
            width=10
        ).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text="输出文件路径：").pack(anchor="w", pady=5)
        self.rotate_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.rotate_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择保存位置", 
            command=lambda: self.select_output_path("rotate")
        ).pack(anchor="w", pady=5)
    
    # 加密功能UI
    def create_encrypt_ui(self):
        ttk.Label(self.frame, text="选择要加密的PDF文件：").pack(anchor="w", pady=5)
        self.encrypt_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.encrypt_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择文件", 
            command=lambda: self.select_single_file("encrypt")
        ).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text="设置密码：").pack(anchor="w", pady=5)
        self.encrypt_password_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.encrypt_password_var, show="*", width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text="输出文件路径：").pack(anchor="w", pady=5)
        self.encrypt_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.encrypt_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择保存位置", 
            command=lambda: self.select_output_path("encrypt")
        ).pack(anchor="w", pady=5)
    
    # 解密功能UI
    def create_decrypt_ui(self):
        ttk.Label(self.frame, text="选择要解密的PDF文件：").pack(anchor="w", pady=5)
        self.decrypt_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.decrypt_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择文件", 
            command=lambda: self.select_single_file("decrypt")
        ).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text="输入密码：").pack(anchor="w", pady=5)
        self.decrypt_password_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.decrypt_password_var, show="*", width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text="输出文件路径：").pack(anchor="w", pady=5)
        self.decrypt_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.decrypt_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(
            self.frame, 
            text="选择保存位置", 
            command=lambda: self.select_output_path("decrypt")
        ).pack(anchor="w", pady=5)
    
    # 文件选择功能
    def select_files(self, func_type):
        files = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if files:
            if func_type == "merge":
                self.merge_files = list(files)
                self.merge_files_var.set(f"已选择 {len(files)} 个文件")
    
    def select_single_file(self, func_type):
        file = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if file:
            if func_type == "split":
                self.split_file_var.set(file)
            elif func_type == "extract":
                self.extract_file_var.set(file)
            elif func_type == "rotate":
                self.rotate_file_var.set(file)
            elif func_type == "encrypt":
                self.encrypt_file_var.set(file)
            elif func_type == "decrypt":
                self.decrypt_file_var.set(file)
            elif func_type == "text":
                self.text_file_var.set(file)
    
    def select_output_path(self, func_type):
        default_filename = "output.pdf"
        if func_type == "merge":
            default_filename = "merged.pdf"
        elif func_type == "extract":
            default_filename = "extracted.pdf"
        elif func_type == "rotate":
            default_filename = "rotated.pdf"
        elif func_type == "encrypt":
            default_filename = "encrypted.pdf"
        elif func_type == "decrypt":
            default_filename = "decrypted.pdf"
        elif func_type == "text":
            default_filename = "with_text.pdf"
            
        file = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")],
            initialfile=default_filename
        )
        if file:
            if func_type == "merge":
                self.merge_output_var.set(file)
            elif func_type == "extract":
                self.extract_output_var.set(file)
            elif func_type == "rotate":
                self.rotate_output_var.set(file)
            elif func_type == "encrypt":
                self.encrypt_output_var.set(file)
            elif func_type == "decrypt":
                self.decrypt_output_var.set(file)
            elif func_type == "text":
                self.text_output_var.set(file)
    
    def select_output_folder(self, func_type):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            if func_type == "split":
                self.split_output_var.set(folder)
    
    def parse_pages(self, page_str, total_pages):
        if not page_str.strip():
            return list(range(1, total_pages + 1))
            
        pages = []
        parts = page_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                try:
                    start = int(start.strip())
                    end = int(end.strip())
                    start = max(1, min(start, total_pages))
                    end = max(1, min(end, total_pages))
                    pages.extend(range(start, end + 1))
                except:
                    continue
            else:
                try:
                    page = int(part)
                    if 1 <= page <= total_pages:
                        pages.append(page)
                except:
                    continue
        return list(sorted(set(pages)))
    
    # 执行函数
    def execute_function(self):
        func = self.function_var.get()
        try:
            if func == "PDF合并":
                self.merge_pdfs()
            elif func == "PDF拆分":
                self.split_pdf()
            elif func == "提取页面":
                self.extract_pages()
            elif func == "页面旋转":
                self.rotate_pages()
            elif func == "PDF加密":
                self.encrypt_pdf()
            elif func == "PDF解密":
                self.decrypt_pdf()
            elif func == "添加文本（水印）":
                self.add_text_to_pdf()
            self.status_var.set("操作成功！")
            messagebox.showinfo("成功", "操作已完成！")
        except Exception as e:
            self.status_var.set(f"操作失败：{str(e)}")
            messagebox.showerror("错误", f"操作失败：{str(e)}")
    
    # 添加文本到PDF的实现
    def add_text_to_pdf(self):
        input_path = self.text_file_var.get()
        output_path = self.text_output_var.get()
        text = self.text_content_var.get()
        
        if not input_path or not output_path or not text:
            raise Exception("请选择文件、输出路径并输入文本内容")
        
        try:
            # 解析参数并验证
            font_size = float(self.text_size_var.get())
            rotate = float(self.text_rotate_var.get())
            if not (0 <= rotate <= 360):
                raise Exception("旋转角度必须在0-360之间")
            
            # 打开PDF
            doc = fitz.open(input_path)
            total_pages = len(doc)
            target_pages = self.parse_pages(self.text_pages_var.get(), total_pages)
            
            # 遍历目标页面添加文本
            for page_num in target_pages:
                page = doc[page_num - 1]  # fitz页码从0开始
                page_rect = page.rect  # 页面尺寸
                
                # 计算文本坐标（居中显示）
                x = page_rect.width / 2
                y = page_rect.height / 2
                
                # 添加文本（仅使用基础参数）
                page.insert_text(
                    (x, y),
                    text,
                    fontsize=font_size,
                    color=self.hex_to_rgb(self.text_color),
                    rotate=rotate
                )
            
            # 保存修改
            doc.save(output_path)
            doc.close()
            
        except Exception as e:
            raise Exception(f"添加文本失败：{str(e)}")
    
    # 合并PDF实现
    def merge_pdfs(self):
        if not self.merge_files or not self.merge_output_var.get():
            raise Exception("请选择文件和输出路径")
            
        merger = PdfMerger()
        for pdf in self.merge_files:
            merger.append(pdf)
        merger.write(self.merge_output_var.get())
        merger.close()
    
    # 拆分PDF实现
    def split_pdf(self):
        input_path = self.split_file_var.get()
        output_folder = self.split_output_var.get()
        pages_str = self.split_pages_var.get()
        
        if not input_path or not output_folder:
            raise Exception("请选择文件和输出文件夹")
            
        os.makedirs(output_folder, exist_ok=True)
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        pages = self.parse_pages(pages_str, total_pages)
        
        if not pages:
            for i in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                output_path = os.path.join(output_folder, f"page_{i+1}.pdf")
                with open(output_path, "wb") as f:
                    writer.write(f)
        else:
            current_group = []
            for page in pages:
                if not current_group:
                    current_group.append(page)
                else:
                    if page == current_group[-1] + 1:
                        current_group.append(page)
                    else:
                        self._save_page_range(reader, current_group, output_folder)
                        current_group = [page]
            if current_group:
                self._save_page_range(reader, current_group, output_folder)
    
    def _save_page_range(self, reader, pages, output_folder):
        if len(pages) == 1:
            output_name = f"page_{pages[0]}.pdf"
        else:
            output_name = f"pages_{pages[0]}-{pages[-1]}.pdf"
            
        output_path = os.path.join(output_folder, output_name)
        writer = PdfWriter()
        for page in pages:
            writer.add_page(reader.pages[page - 1])
        with open(output_path, "wb") as f:
            writer.write(f)
    
    # 提取页面实现
    def extract_pages(self):
        input_path = self.extract_file_var.get()
        output_path = self.extract_output_var.get()
        pages_str = self.extract_pages_var.get()
        
        if not input_path or not output_path or not pages_str:
            raise Exception("请选择文件、输出路径和提取页码")
            
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        pages = self.parse_pages(pages_str, total_pages)
        
        if not pages:
            raise Exception("无效的页码格式")
            
        writer = PdfWriter()
        for page in pages:
            writer.add_page(reader.pages[page - 1])
        with open(output_path, "wb") as f:
            writer.write(f)
    
    # 页面旋转实现
    def rotate_pages(self):
        input_path = self.rotate_file_var.get()
        output_path = self.rotate_output_var.get()
        pages_str = self.rotate_pages_var.get()
        angle = int(self.rotate_angle_var.get())
        
        if not input_path or not output_path:
            raise Exception("请选择文件和输出路径")
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        pages = self.parse_pages(pages_str, total_pages)
        
        for i in range(total_pages):
            page = reader.pages[i]
            if (i + 1) in pages:
                page.rotate(angle)
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
    
    # 加密PDF实现
    def encrypt_pdf(self):
        input_path = self.encrypt_file_var.get()
        output_path = self.encrypt_output_var.get()
        password = self.encrypt_password_var.get()
        
        if not input_path or not output_path or not password:
            raise Exception("请选择文件、输出路径并设置密码")
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(password)
        with open(output_path, "wb") as f:
            writer.write(f)
    
    # 解密PDF实现
    def decrypt_pdf(self):
        input_path = self.decrypt_file_var.get()
        output_path = self.decrypt_output_var.get()
        password = self.decrypt_password_var.get()
        
        if not input_path or not output_path or not password:
            raise Exception("请选择文件、输出路径并输入密码")
            
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            reader.decrypt(password)
            
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolbox(root)
    root.mainloop()
    