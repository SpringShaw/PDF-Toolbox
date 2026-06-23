import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser
import os
import locale
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import fitz

MAX_FILE_SIZE = 500 * 1024 * 1024
LANG_FILE = os.path.join(os.path.expanduser("~"), ".pdf_toolbox_lang")

TRANSLATIONS = {
    "zh": {
        "app_title": "本地PDF工具箱（含编辑功能）",
        "select_operation": "选择操作：",
        "execute": "执行操作",
        "status_ready": "请选择操作并设置参数",
        "status_success": "操作成功！",
        "status_fail": "操作失败",
        "success_title": "成功",
        "success_msg": "操作已完成！",
        "error_title": "错误",
        "error_prefix": "操作失败：",
        "warn_title": "警告",
        "lang_btn": "English",
        "func_merge": "PDF合并",
        "func_split": "PDF拆分",
        "func_extract": "提取页面",
        "func_rotate": "页面旋转",
        "func_encrypt": "PDF加密",
        "func_decrypt": "PDF解密",
        "func_watermark": "添加文本（水印）",
        "select_pdf_files": "选择要合并的PDF文件（可多选）：",
        "no_file_selected": "未选择文件",
        "files_selected": "已选择 {count} 个文件",
        "select_file": "选择文件",
        "select_save_location": "选择保存位置",
        "output_path": "输出文件路径：",
        "select_split_file": "选择要拆分的PDF文件：",
        "split_pages_hint": "拆分页码（如：1-3,5 或留空拆分成单页）：",
        "output_folder": "输出文件夹：",
        "select_folder": "选择文件夹",
        "select_source_pdf": "选择源PDF文件：",
        "extract_pages_hint": "提取页码（如：1,3-5）：",
        "select_rotate_file": "选择要旋转的PDF文件：",
        "rotate_pages_hint": "旋转页码（如：1-3 或留空旋转所有页）：",
        "rotate_angle": "旋转角度：",
        "select_encrypt_file": "选择要加密的PDF文件：",
        "set_password": "设置密码：",
        "select_decrypt_file": "选择要解密的PDF文件：",
        "input_password": "输入密码：",
        "select_edit_file": "选择要编辑的PDF文件：",
        "watermark_text": "要添加的文本内容：",
        "watermark_default": "机密",
        "apply_pages": "应用页码（如：1-3 或留空全部）：",
        "font_size": "字体大小：",
        "text_color": "文本颜色：",
        "select_color": "选择颜色",
        "rotate_angle_label": "旋转角度：",
        "file_dialog_title": "选择PDF文件",
        "save_dialog_title": "保存文件",
        "folder_dialog_title": "选择输出文件夹",
        "color_dialog_title": "选择文本颜色",
        "err_select_file": "请选择文件",
        "err_file_not_exist": "文件不存在或路径无效",
        "err_file_too_large": "文件过大，超过500MB限制",
        "err_select_output": "请选择输出路径",
        "err_no_merge_files": "请选择要合并的文件",
        "err_input_text": "请输入文本内容",
        "err_invalid_font_size": "字体大小必须是有效数字",
        "err_font_size_range": "字体大小须在0-500之间",
        "err_invalid_rotate": "旋转角度必须是有效数字",
        "err_rotate_range": "旋转角度必须在0-360之间",
        "err_invalid_pdf": "无效的PDF文件",
        "err_add_text": "添加文本失败：",
        "err_extract_pages": "请输入提取页码",
        "err_invalid_pages": "无效的页码格式",
        "err_set_password": "请设置密码",
        "err_password_length": "密码长度至少6位",
        "err_input_password": "请输入密码",
        "err_invalid_color": "无效的颜色格式",
    },
    "en": {
        "app_title": "Local PDF Toolbox (with Edit)",
        "select_operation": "Select Operation:",
        "execute": "Execute",
        "status_ready": "Select operation and set parameters",
        "status_success": "Success!",
        "status_fail": "Failed",
        "success_title": "Success",
        "success_msg": "Operation completed!",
        "error_title": "Error",
        "error_prefix": "Failed: ",
        "warn_title": "Warning",
        "lang_btn": "中文",
        "func_merge": "PDF Merge",
        "func_split": "PDF Split",
        "func_extract": "Extract Pages",
        "func_rotate": "Rotate Pages",
        "func_encrypt": "PDF Encrypt",
        "func_decrypt": "PDF Decrypt",
        "func_watermark": "Add Text (Watermark)",
        "select_pdf_files": "Select PDF files to merge (multiple):",
        "no_file_selected": "No file selected",
        "files_selected": "{count} file(s) selected",
        "select_file": "Select File",
        "select_save_location": "Save As",
        "output_path": "Output file path:",
        "select_split_file": "Select PDF file to split:",
        "split_pages_hint": "Pages to split (e.g. 1-3,5 or empty for single pages):",
        "output_folder": "Output folder:",
        "select_folder": "Select Folder",
        "select_source_pdf": "Select source PDF file:",
        "extract_pages_hint": "Pages to extract (e.g. 1,3-5):",
        "select_rotate_file": "Select PDF file to rotate:",
        "rotate_pages_hint": "Pages to rotate (e.g. 1-3 or empty for all):",
        "rotate_angle": "Rotation angle:",
        "select_encrypt_file": "Select PDF file to encrypt:",
        "set_password": "Set password:",
        "select_decrypt_file": "Select PDF file to decrypt:",
        "input_password": "Enter password:",
        "select_edit_file": "Select PDF file to edit:",
        "watermark_text": "Text to add:",
        "watermark_default": "CONFIDENTIAL",
        "apply_pages": "Apply to pages (e.g. 1-3 or empty for all):",
        "font_size": "Font size:",
        "text_color": "Text color:",
        "select_color": "Select Color",
        "rotate_angle_label": "Rotation angle:",
        "file_dialog_title": "Select PDF File",
        "save_dialog_title": "Save File",
        "folder_dialog_title": "Select Output Folder",
        "color_dialog_title": "Select Text Color",
        "err_select_file": "Please select a file",
        "err_file_not_exist": "File does not exist or invalid path",
        "err_file_too_large": "File too large, exceeds 500MB limit",
        "err_select_output": "Please select output path",
        "err_no_merge_files": "Please select files to merge",
        "err_input_text": "Please enter text content",
        "err_invalid_font_size": "Font size must be a valid number",
        "err_font_size_range": "Font size must be between 0-500",
        "err_invalid_rotate": "Rotation angle must be a valid number",
        "err_rotate_range": "Rotation angle must be between 0-360",
        "err_invalid_pdf": "Invalid PDF file",
        "err_add_text": "Failed to add text: ",
        "err_extract_pages": "Please enter pages to extract",
        "err_invalid_pages": "Invalid page format",
        "err_set_password": "Please set a password",
        "err_password_length": "Password must be at least 6 characters",
        "err_input_password": "Please enter password",
        "err_invalid_color": "Invalid color format",
    }
}

current_lang = "zh"

def t(key, **params):
    text = TRANSLATIONS[current_lang].get(key, TRANSLATIONS["zh"].get(key, key))
    for name, value in params.items():
        text = text.replace(f"{{{name}}}", str(value))
    return text

def get_system_lang():
    try:
        sys_lang = locale.getdefaultlocale()[0]
        if sys_lang and sys_lang.lower().startswith("zh"):
            return "zh"
    except:
        pass
    return "en"

def load_lang():
    global current_lang
    if os.path.exists(LANG_FILE):
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if saved in ("zh", "en"):
                    current_lang = saved
                    return
        except:
            pass
    current_lang = get_system_lang()

def save_lang():
    try:
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            f.write(current_lang)
    except:
        pass


class PDFToolbox:
    def __init__(self, root):
        self.root = root
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TCombobox", font=("SimHei", 10))
        
        self.header_frame = ttk.Frame(root)
        self.header_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        self.title_label = ttk.Label(self.header_frame, text=t("select_operation"), font=("SimHei", 12, "bold"))
        self.title_label.pack(side="left")
        
        self.lang_btn = ttk.Button(self.header_frame, text=t("lang_btn"), command=self.switch_language, width=8)
        self.lang_btn.pack(side="right")
        
        self.functions_keys = [
            "func_merge", "func_split", "func_extract", 
            "func_rotate", "func_encrypt", "func_decrypt", "func_watermark"
        ]
        self.function_var = tk.StringVar(value=t(self.functions_keys[0]))
        self.function_combo = ttk.Combobox(
            root, 
            textvariable=self.function_var, 
            values=[t(k) for k in self.functions_keys], 
            state="readonly",
            width=30
        )
        self.function_combo.pack(pady=5)
        self.function_combo.bind("<<ComboboxSelected>>", self.update_ui)
        
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.update_ui(None)
        
        self.execute_btn = ttk.Button(root, text=t("execute"), command=self.execute_function, width=20)
        self.execute_btn.pack(pady=20)
        
        self.status_var = tk.StringVar(value=t("status_ready"))
        ttk.Label(root, textvariable=self.status_var, foreground="blue").pack(pady=10)
        
        self.root.title(t("app_title"))
        self.apply_language()
    
    def switch_language(self):
        global current_lang
        current_lang = "en" if current_lang == "zh" else "zh"
        save_lang()
        self.apply_language()
    
    def apply_language(self):
        self.root.title(t("app_title"))
        self.title_label.config(text=t("select_operation"))
        self.lang_btn.config(text=t("lang_btn"))
        
        current_key = self.get_current_func_key()
        
        self.function_combo.config(values=[t(k) for k in self.functions_keys])
        self.function_var.set(t(current_key))
        
        self.execute_btn.config(text=t("execute"))
        self.status_var.set(t("status_ready"))
        self.update_ui(None)
    
    def get_current_func_key(self):
        current_func = self.function_var.get()
        for key in self.functions_keys:
            if t(key) == current_func:
                return key
        return self.functions_keys[0]
    
    def update_ui(self, event):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        func_key = self.get_current_func_key()
        
        if func_key == "func_merge":
            self.create_merge_ui()
        elif func_key == "func_split":
            self.create_split_ui()
        elif func_key == "func_extract":
            self.create_extract_ui()
        elif func_key == "func_rotate":
            self.create_rotate_ui()
        elif func_key == "func_encrypt":
            self.create_encrypt_ui()
        elif func_key == "func_decrypt":
            self.create_decrypt_ui()
        elif func_key == "func_watermark":
            self.create_add_text_ui()
    
    def create_add_text_ui(self):
        ttk.Label(self.frame, text=t("select_edit_file")).pack(anchor="w", pady=5)
        self.text_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.text_file_var, width=55).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_file"), command=lambda: self.select_single_file("text")).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text=t("watermark_text")).pack(anchor="w", pady=5)
        self.text_content_var = tk.StringVar(value=t("watermark_default"))
        ttk.Entry(self.frame, textvariable=self.text_content_var, width=55).pack(anchor="w", pady=2)
        
        frame_layout = ttk.Frame(self.frame)
        frame_layout.pack(anchor="w", fill="x", pady=5)
        
        ttk.Label(frame_layout, text=t("apply_pages")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.text_pages_var = tk.StringVar(value="")
        ttk.Entry(frame_layout, textvariable=self.text_pages_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(frame_layout, text=t("font_size")).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.text_size_var = tk.StringVar(value="48")
        ttk.Entry(frame_layout, textvariable=self.text_size_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        self.text_color = "#FF0000"
        ttk.Label(frame_layout, text=t("text_color")).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.color_label = ttk.Label(frame_layout, text="", background=self.text_color, width=5)
        self.color_label.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        ttk.Button(frame_layout, text=t("select_color"), command=self.choose_text_color).grid(row=2, column=2, padx=5, pady=2, sticky="w")
        
        ttk.Label(frame_layout, text=t("rotate_angle_label")).grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.text_rotate_var = tk.StringVar(value="0")
        ttk.Combobox(frame_layout, textvariable=self.text_rotate_var, values=["0", "90", "180", "270"], state="readonly", width=10).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(self.frame, text=t("output_path")).pack(anchor="w", pady=5)
        self.text_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.text_output_var, width=55).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_save_location"), command=lambda: self.select_output_path("text")).pack(anchor="w", pady=5)
    
    def choose_text_color(self):
        color = colorchooser.askcolor(title=t("color_dialog_title"))[1]
        if color:
            self.text_color = color
            self.color_label.config(background=color)
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(t("err_invalid_color"))
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
    
    def create_merge_ui(self):
        ttk.Label(self.frame, text=t("select_pdf_files")).pack(anchor="w", pady=5)
        self.merge_files = []
        self.merge_files_var = tk.StringVar(value=t("no_file_selected"))
        ttk.Label(self.frame, textvariable=self.merge_files_var).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_file"), command=lambda: self.select_files("merge")).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text=t("output_path")).pack(anchor="w", pady=5)
        self.merge_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.merge_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_save_location"), command=lambda: self.select_output_path("merge")).pack(anchor="w", pady=5)
    
    def create_split_ui(self):
        ttk.Label(self.frame, text=t("select_split_file")).pack(anchor="w", pady=5)
        self.split_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.split_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_file"), command=lambda: self.select_single_file("split")).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text=t("split_pages_hint")).pack(anchor="w", pady=5)
        self.split_pages_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.split_pages_var, width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text=t("output_folder")).pack(anchor="w", pady=5)
        self.split_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.split_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_folder"), command=lambda: self.select_output_folder("split")).pack(anchor="w", pady=5)
    
    def create_extract_ui(self):
        ttk.Label(self.frame, text=t("select_source_pdf")).pack(anchor="w", pady=5)
        self.extract_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.extract_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_file"), command=lambda: self.select_single_file("extract")).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text=t("extract_pages_hint")).pack(anchor="w", pady=5)
        self.extract_pages_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.extract_pages_var, width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text=t("output_path")).pack(anchor="w", pady=5)
        self.extract_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.extract_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_save_location"), command=lambda: self.select_output_path("extract")).pack(anchor="w", pady=5)
    
    def create_rotate_ui(self):
        ttk.Label(self.frame, text=t("select_rotate_file")).pack(anchor="w", pady=5)
        self.rotate_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.rotate_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_file"), command=lambda: self.select_single_file("rotate")).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text=t("rotate_pages_hint")).pack(anchor="w", pady=5)
        self.rotate_pages_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.rotate_pages_var, width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text=t("rotate_angle")).pack(anchor="w", pady=5)
        self.rotate_angle_var = tk.StringVar(value="90")
        ttk.Combobox(self.frame, textvariable=self.rotate_angle_var, values=["90", "180", "270"], state="readonly", width=10).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text=t("output_path")).pack(anchor="w", pady=5)
        self.rotate_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.rotate_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_save_location"), command=lambda: self.select_output_path("rotate")).pack(anchor="w", pady=5)
    
    def create_encrypt_ui(self):
        ttk.Label(self.frame, text=t("select_encrypt_file")).pack(anchor="w", pady=5)
        self.encrypt_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.encrypt_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_file"), command=lambda: self.select_single_file("encrypt")).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text=t("set_password")).pack(anchor="w", pady=5)
        self.encrypt_password_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.encrypt_password_var, show="*", width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text=t("output_path")).pack(anchor="w", pady=5)
        self.encrypt_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.encrypt_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_save_location"), command=lambda: self.select_output_path("encrypt")).pack(anchor="w", pady=5)
    
    def create_decrypt_ui(self):
        ttk.Label(self.frame, text=t("select_decrypt_file")).pack(anchor="w", pady=5)
        self.decrypt_file_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.decrypt_file_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_file"), command=lambda: self.select_single_file("decrypt")).pack(anchor="w", pady=5)
        
        ttk.Label(self.frame, text=t("input_password")).pack(anchor="w", pady=5)
        self.decrypt_password_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.decrypt_password_var, show="*", width=50).pack(anchor="w", pady=2)
        
        ttk.Label(self.frame, text=t("output_path")).pack(anchor="w", pady=5)
        self.decrypt_output_var = tk.StringVar(value="")
        ttk.Entry(self.frame, textvariable=self.decrypt_output_var, width=50).pack(anchor="w", pady=2)
        ttk.Button(self.frame, text=t("select_save_location"), command=lambda: self.select_output_path("decrypt")).pack(anchor="w", pady=5)
    
    def select_files(self, func_type):
        files = filedialog.askopenfilenames(title=t("file_dialog_title"), filetypes=[("PDF files", "*.pdf")])
        if files:
            if func_type == "merge":
                self.merge_files = list(files)
                self.merge_files_var.set(t("files_selected", count=len(files)))
    
    def select_single_file(self, func_type):
        file = filedialog.askopenfilename(title=t("file_dialog_title"), filetypes=[("PDF files", "*.pdf")])
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
        defaults = {"merge": "merged.pdf", "extract": "extracted.pdf", "rotate": "rotated.pdf", 
                    "encrypt": "encrypted.pdf", "decrypt": "decrypted.pdf", "text": "with_text.pdf"}
        default_filename = defaults.get(func_type, "output.pdf")
        
        file = filedialog.asksaveasfilename(title=t("save_dialog_title"), defaultextension=".pdf", 
                                            filetypes=[("PDF files", "*.pdf")], initialfile=default_filename)
        if file:
            var_name = f"{func_type}_output_var"
            var = getattr(self, var_name, None)
            if var:
                var.set(file)
    
    def select_output_folder(self, func_type):
        folder = filedialog.askdirectory(title=t("folder_dialog_title"))
        if folder:
            var_name = f"{func_type}_output_var"
            var = getattr(self, var_name, None)
            if var:
                var.set(folder)
    
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
                except (ValueError, TypeError):
                    continue
            else:
                try:
                    page = int(part)
                    if 1 <= page <= total_pages:
                        pages.append(page)
                except (ValueError, TypeError):
                    continue
        return list(sorted(set(pages)))
    
    def _validate_file(self, path, must_exist=True):
        if not path:
            raise Exception(t("err_select_file"))
        path = os.path.normpath(path)
        if must_exist and not os.path.isfile(path):
            raise Exception(t("err_file_not_exist"))
        if must_exist and os.path.getsize(path) > MAX_FILE_SIZE:
            raise Exception(t("err_file_too_large"))
        return path

    def _validate_output(self, path):
        if not path:
            raise Exception(t("err_select_output"))
        return os.path.normpath(path)

    def execute_function(self):
        func_key = self.get_current_func_key()
        try:
            if func_key == "func_merge":
                self.merge_pdfs()
            elif func_key == "func_split":
                self.split_pdf()
            elif func_key == "func_extract":
                self.extract_pages()
            elif func_key == "func_rotate":
                self.rotate_pages()
            elif func_key == "func_encrypt":
                self.encrypt_pdf()
            elif func_key == "func_decrypt":
                self.decrypt_pdf()
            elif func_key == "func_watermark":
                self.add_text_to_pdf()
            self.status_var.set(t("status_success"))
            messagebox.showinfo(t("success_title"), t("success_msg"))
        except Exception as e:
            self.status_var.set(t("status_fail"))
            messagebox.showerror(t("error_title"), f"{t('error_prefix')}{e}")
    
    def add_text_to_pdf(self):
        input_path = self._validate_file(self.text_file_var.get())
        output_path = self._validate_output(self.text_output_var.get())
        text = self.text_content_var.get()
        
        if not text:
            raise Exception(t("err_input_text"))
        
        try:
            font_size = float(self.text_size_var.get())
        except (ValueError, TypeError):
            raise Exception(t("err_invalid_font_size"))
        
        if font_size <= 0 or font_size > 500:
            raise Exception(t("err_font_size_range"))
        
        try:
            rotate = int(self.text_rotate_var.get())
        except (ValueError, TypeError):
            raise Exception(t("err_invalid_rotate"))
        
        if not (0 <= rotate <= 360):
            raise Exception(t("err_rotate_range"))
        
        try:
            doc = fitz.open(input_path)
            total_pages = len(doc)
            target_pages = self.parse_pages(self.text_pages_var.get(), total_pages)
            
            for page_num in target_pages:
                page = doc[page_num - 1]
                page_rect = page.rect
                x = page_rect.width / 2
                y = page_rect.height / 2
                page.insert_text((x, y), text, fontsize=font_size, color=self.hex_to_rgb(self.text_color), rotate=rotate)
            
            doc.save(output_path)
            doc.close()
        except fitz.FileDataError:
            raise Exception(t("err_invalid_pdf"))
        except Exception as e:
            raise Exception(f"{t('err_add_text')}{e}")
    
    def merge_pdfs(self):
        if not self.merge_files:
            raise Exception(t("err_no_merge_files"))
        output_path = self._validate_output(self.merge_output_var.get())
        
        for pdf in self.merge_files:
            self._validate_file(pdf)
        
        merger = PdfMerger()
        try:
            for pdf in self.merge_files:
                merger.append(pdf)
            merger.write(output_path)
        finally:
            merger.close()
    
    def split_pdf(self):
        input_path = self._validate_file(self.split_file_var.get())
        output_folder = self._validate_output(self.split_output_var.get())
        pages_str = self.split_pages_var.get()
        
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
    
    def extract_pages(self):
        input_path = self._validate_file(self.extract_file_var.get())
        output_path = self._validate_output(self.extract_output_var.get())
        pages_str = self.extract_pages_var.get()
        
        if not pages_str:
            raise Exception(t("err_extract_pages"))
        
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        pages = self.parse_pages(pages_str, total_pages)
        
        if not pages:
            raise Exception(t("err_invalid_pages"))
            
        writer = PdfWriter()
        for page in pages:
            writer.add_page(reader.pages[page - 1])
        with open(output_path, "wb") as f:
            writer.write(f)
    
    def rotate_pages(self):
        input_path = self._validate_file(self.rotate_file_var.get())
        output_path = self._validate_output(self.rotate_output_var.get())
        pages_str = self.rotate_pages_var.get()
        angle = int(self.rotate_angle_var.get())
            
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
    
    def encrypt_pdf(self):
        input_path = self._validate_file(self.encrypt_file_var.get())
        output_path = self._validate_output(self.encrypt_output_var.get())
        password = self.encrypt_password_var.get()
        
        if not password:
            raise Exception(t("err_set_password"))
        if len(password) < 6:
            raise Exception(t("err_password_length"))
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(password)
        with open(output_path, "wb") as f:
            writer.write(f)
    
    def decrypt_pdf(self):
        input_path = self._validate_file(self.decrypt_file_var.get())
        output_path = self._validate_output(self.decrypt_output_var.get())
        password = self.decrypt_password_var.get()
        
        if not password:
            raise Exception(t("err_input_password"))
        
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            reader.decrypt(password)
            
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)

if __name__ == "__main__":
    load_lang()
    root = tk.Tk()
    app = PDFToolbox(root)
    root.mainloop()
