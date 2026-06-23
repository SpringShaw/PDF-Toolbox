import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import shutil

try:
    import pypdf
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("依赖缺失", "缺少 pypdf 库。请先安装: pip install pypdf")
    sys.exit(1)

def find_ghostscript():
    gs_path = shutil.which("gswin64c") or shutil.which("gswin32c") or shutil.which("gs")
    if gs_path:
        return gs_path
    default_paths = [
        r"C:\Program Files\gs\gs10.05.1\bin\gswin64.exe",
        r"C:\Program Files\gs\gs10.04.0\bin\gswin64.exe",
        r"C:\Program Files (x86)\gs\gs10.05.1\bin\gswin32.exe",
    ]
    for path in default_paths:
        if os.path.isfile(path):
            return path
    return None

GS_COMMAND = find_ghostscript()

if not GS_COMMAND:
    print("[警告] 未找到Ghostscript，压缩功能不可用")

class PDFezyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFezy - 简洁PDF工具箱")
        self.root.geometry("720x550")
        self.root.minsize(600, 400)

        # UI样式美化
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure('TNotebook.Tab', padding=[10, 5])
        style.configure('TLabelframe.Label', font=('微软雅黑', 10, 'bold'))

        # 创建标签页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)

        # 合并Tab
        self.merge_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.merge_frame, text='  合并PDF  ')
        self.setup_merge_tab()

        # 拆分Tab
        self.split_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.split_frame, text='  拆分PDF  ')
        self.setup_split_tab()

        # 压缩Tab
        self.compress_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.compress_frame, text='  压缩PDF  ')
        self.setup_compress_tab()

    # 合并Tab相关方法
    def setup_merge_tab(self):
        title_label = ttk.Label(self.merge_frame, text="合并多个PDF文件", font=('微软雅黑', 12, 'bold'))
        title_label.pack(pady=(15, 10))

        main_frame = ttk.Frame(self.merge_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        listbox_frame = ttk.LabelFrame(main_frame, text="待合并文件列表")
        listbox_frame.pack(fill='both', expand=True, side='left', padx=(0, 10))

        self.merge_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.merge_listbox.yview)
        self.merge_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        
        self.merge_listbox.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        listbox_scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='y', side='right')

        ttk.Button(button_frame, text="添加文件", command=self.add_files_to_merge, width=15).pack(pady=5)
        ttk.Button(button_frame, text="上移", command=self.move_up, width=15).pack(pady=5)
        ttk.Button(button_frame, text="下移", command=self.move_down, width=15).pack(pady=5)
        ttk.Button(button_frame, text="删除", command=self.remove_file, width=15).pack(pady=5)

        output_frame = ttk.LabelFrame(self.merge_frame, text="输出设置")
        output_frame.pack(fill='x', padx=10, pady=(0, 15))

        ttk.Label(output_frame, text="输出文件路径:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
        self.merge_output_entry = ttk.Entry(output_frame)
        self.merge_output_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=10)
        ttk.Button(output_frame, text="浏览...", command=self.browse_merge_output).grid(row=0, column=2, padx=5, pady=10)

        output_frame.columnconfigure(1, weight=1)

        ttk.Button(self.merge_frame, text="开始合并", command=self.execute_merge).pack(pady=(0, 15))

    def add_files_to_merge(self):
        files = filedialog.askopenfilenames(title="选择PDF文件", filetypes=[("PDF files", "*.pdf")])
        for file in files:
            self.merge_listbox.insert(tk.END, file)

    def move_up(self):
        try:
            pos = self.merge_listbox.curselection()[0]
            if pos > 0:
                text = self.merge_listbox.get(pos)
                self.merge_listbox.delete(pos)
                self.merge_listbox.insert(pos - 1, text)
                self.merge_listbox.selection_set(pos - 1)
        except IndexError:
            pass

    def move_down(self):
        try:
            pos = self.merge_listbox.curselection()[0]
            if pos < self.merge_listbox.size() - 1:
                text = self.merge_listbox.get(pos)
                self.merge_listbox.delete(pos)
                self.merge_listbox.insert(pos + 1, text)
                self.merge_listbox.selection_set(pos + 1)
        except IndexError:
            pass

    def remove_file(self):
        try:
            pos = self.merge_listbox.curselection()[0]
            self.merge_listbox.delete(pos)
        except IndexError:
            pass

    def browse_merge_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="保存合并后的PDF")
        if filename:
            self.merge_output_entry.delete(0, tk.END)
            self.merge_output_entry.insert(0, filename)

    def execute_merge(self):
        files = self.merge_listbox.get(0, tk.END)
        output_path = self.merge_output_entry.get()
        if not files:
            messagebox.showwarning("警告", "请至少添加一个PDF文件。")
            return
        if not output_path:
            messagebox.showwarning("警告", "请选择输出文件路径。")
            return

        try:
            merger_writer = pypdf.PdfWriter()

            for pdf_path in files:
                reader = pypdf.PdfReader(pdf_path)
                for page in reader.pages:
                    merger_writer.add_page(page)
            
            with open(output_path, 'wb') as out_file:
                merger_writer.write(out_file)
            
            messagebox.showinfo("成功", f"PDF合并完成！\n保存至: {output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"合并失败，请检查文件是否有效")

    # 拆分Tab相关方法
    def setup_split_tab(self):
        title_label = ttk.Label(self.split_frame, text="拆分PDF文件", font=('微软雅黑', 12, 'bold'))
        title_label.pack(pady=(15, 10))

        input_frame = ttk.LabelFrame(self.split_frame, text="源文件")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="选择PDF文件:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
        self.split_file_entry = ttk.Entry(input_frame)
        self.split_file_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=10)
        ttk.Button(input_frame, text="浏览...", command=self.browse_split_file).grid(row=0, column=2, padx=5, pady=10)
        
        input_frame.columnconfigure(1, weight=1)

        mode_frame = ttk.LabelFrame(self.split_frame, text="拆分模式")
        mode_frame.pack(fill='x', padx=10, pady=5)

        self.split_mode = tk.StringVar(value="range")
        ttk.Radiobutton(mode_frame, text="按页码范围", variable=self.split_mode, value="range").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="按固定页数", variable=self.split_mode, value="fixed").grid(row=0, column=1, sticky='w', padx=5, pady=5)

        self.split_params_frame = ttk.LabelFrame(self.split_frame, text="参数设置")
        self.split_params_frame.pack(fill='x', padx=10, pady=5)
        self.update_split_params()
        self.split_mode.trace('w', self.update_split_params)

        output_dir_frame = ttk.LabelFrame(self.split_frame, text="输出设置")
        output_dir_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(output_dir_frame, text="输出目录:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
        self.split_output_dir_entry = ttk.Entry(output_dir_frame)
        self.split_output_dir_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=10)
        ttk.Button(output_dir_frame, text="浏览...", command=self.browse_split_output_dir).grid(row=0, column=2, padx=5, pady=10)
        
        output_dir_frame.columnconfigure(1, weight=1)

        ttk.Button(self.split_frame, text="开始拆分", command=self.execute_split).pack(pady=(0, 15))

    def update_split_params(self, *args):
        for item in self.split_params_frame.winfo_children():
            item.destroy()

        mode = self.split_mode.get()
        inner_frame = ttk.Frame(self.split_params_frame)
        inner_frame.pack(fill='x', padx=5, pady=10)
        inner_frame.columnconfigure(1, weight=1)

        if mode == "range":
            ttk.Label(inner_frame, text="起始页码 (从1开始):").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            self.split_start_entry = ttk.Entry(inner_frame, width=10)
            self.split_start_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            
            ttk.Label(inner_frame, text="结束页码:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            self.split_end_entry = ttk.Entry(inner_frame, width=10)
            self.split_end_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        elif mode == "fixed":
            ttk.Label(inner_frame, text="每份页数:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            self.split_fixed_entry = ttk.Entry(inner_frame, width=10)
            self.split_fixed_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)

    def browse_split_file(self):
        file = filedialog.askopenfilename(title="选择PDF文件", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.split_file_entry.delete(0, tk.END)
            self.split_file_entry.insert(0, file)

    def browse_split_output_dir(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.split_output_dir_entry.delete(0, tk.END)
            self.split_output_dir_entry.insert(0, directory)

    def execute_split(self):
        input_path = self.split_file_entry.get()
        output_dir = self.split_output_dir_entry.get()
        mode = self.split_mode.get()

        if not input_path or not os.path.isfile(input_path):
            messagebox.showwarning("警告", "请选择有效的源PDF文件。")
            return
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showwarning("警告", "请选择有效的输出目录。")
            return

        try:
            reader = pypdf.PdfReader(input_path)
            total_pages = len(reader.pages)

            if mode == "range":
                try:
                    start = int(self.split_start_entry.get()) - 1
                    end = int(self.split_end_entry.get()) - 1
                    if start < 0 or end >= total_pages or start > end:
                        raise ValueError("页码范围无效。")
                    writer = pypdf.PdfWriter()
                    for i in range(start, end + 1):
                        writer.add_page(reader.pages[i])
                    
                    output_filename = f"split_{start+1}_to_{end+1}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    with open(output_path, 'wb') as out_file:
                        writer.write(out_file)
                    messagebox.showinfo("成功", f"PDF拆分完成！\n保存至: {output_path}")

                except ValueError as e:
                    messagebox.showerror("输入错误", f"请输入有效的页码范围。\n{e}")
            elif mode == "fixed":
                try:
                    fixed_size = int(self.split_fixed_entry.get())
                    if fixed_size <= 0:
                        raise ValueError("页数必须大于0。")
                    
                    part_num = 1
                    for i in range(0, total_pages, fixed_size):
                        writer = pypdf.PdfWriter()
                        end_index = min(i + fixed_size, total_pages)
                        for j in range(i, end_index):
                            writer.add_page(reader.pages[j])
                        
                        output_filename = f"split_part_{part_num}.pdf"
                        output_path = os.path.join(output_dir, output_filename)
                        with open(output_path, 'wb') as out_file:
                            writer.write(out_file)
                        part_num += 1
                    
                    messagebox.showinfo("成功", f"PDF按{fixed_size}页拆分完成！共生成 {part_num - 1} 个文件。")

                except ValueError as e:
                    messagebox.showerror("输入错误", f"请输入有效的固定页数。\n{e}")

        except Exception as e:
            messagebox.showerror("错误", f"拆分失败，请检查文件和参数")

    # 压缩Tab相关方法 (已修复)
    def setup_compress_tab(self):
        if not GS_COMMAND:
             ttk.Label(self.compress_frame, text="Ghostscript 未安装，此功能不可用。",
                      foreground='red', font=('微软雅黑', 10, 'bold')).pack(pady=50)
             return

        title_label = ttk.Label(self.compress_frame, text="压缩PDF文件 (降低图像质量)", font=('微软雅黑', 12, 'bold'))
        title_label.pack(pady=(15, 10))

        input_frame = ttk.LabelFrame(self.compress_frame, text="源文件")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="选择PDF文件:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
        self.compress_file_entry = ttk.Entry(input_frame)
        self.compress_file_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=10)
        ttk.Button(input_frame, text="浏览...", command=self.browse_compress_file).grid(row=0, column=2, padx=5, pady=10)
        
        input_frame.columnconfigure(1, weight=1)

        params_frame = ttk.LabelFrame(self.compress_frame, text="压缩设置")
        params_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(params_frame, text="目标DPI (e.g., 150, 300):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.compress_dpi_entry = ttk.Entry(params_frame, width=10)
        self.compress_dpi_entry.insert(0, "150")
        self.compress_dpi_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(params_frame, text="质量预设:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.compress_quality_var = tk.StringVar(value="/screen")
        quality_options = ["/screen", "/ebook", "/printer", "/prepress"]
        quality_combo = ttk.Combobox(params_frame, textvariable=self.compress_quality_var, values=quality_options, state="readonly", width=15)
        quality_combo.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        quality_combo.set("/screen")

        output_frame = ttk.LabelFrame(self.compress_frame, text="输出设置")
        output_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(output_frame, text="输出文件路径:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
        self.compress_output_entry = ttk.Entry(output_frame)
        self.compress_output_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=10)
        ttk.Button(output_frame, text="浏览...", command=self.browse_compress_output).grid(row=0, column=2, padx=5, pady=10)
        
        output_frame.columnconfigure(1, weight=1)

        ttk.Button(self.compress_frame, text="开始压缩", command=self.execute_compress).pack(pady=(15, 15))

        info_text = (
            "说明:\n"
            "- 此功能依赖 Ghostscript。\n"
            "- 降低DPI和选择较低质量预设可显著减小文件体积。\n"
            "- '/screen' 最低质量，文件最小。\n"
            "- '/prepress' 最高质量，文件较大。"
        )
        info_label = ttk.Label(self.compress_frame, text=info_text, justify='left', font=('微软雅黑', 9))
        info_label.pack(padx=10, pady=(0, 10), anchor='w')

    def browse_compress_file(self):
        file = filedialog.askopenfilename(title="选择要压缩的PDF文件", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.compress_file_entry.delete(0, tk.END)
            self.compress_file_entry.insert(0, file)
            base, _ = os.path.splitext(file)
            default_output = f"{base}_compressed.pdf"
            self.compress_output_entry.delete(0, tk.END)
            self.compress_output_entry.insert(0, default_output)

    def browse_compress_output(self):
         filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="保存压缩后的PDF")
         if filename:
             self.compress_output_entry.delete(0, tk.END)
             self.compress_output_entry.insert(0, filename)

    def execute_compress(self):
        if not GS_COMMAND:
            messagebox.showerror("错误", "Ghostscript 未找到，无法执行压缩。")
            return

        input_path = os.path.normpath(self.compress_file_entry.get().strip())
        output_path = os.path.normpath(self.compress_output_entry.get().strip())
        dpi_str = self.compress_dpi_entry.get().strip()
        quality_preset = self.compress_quality_var.get()

        if not input_path or not os.path.isfile(input_path):
            messagebox.showwarning("警告", "请选择有效的源PDF文件。")
            return
        if not output_path:
            messagebox.showwarning("警告", "请选择输出文件路径。")
            return
        if not dpi_str.isdigit():
            messagebox.showwarning("警告", "请输入有效的DPI值 (整数)。")
            return

        dpi = int(dpi_str)
        if dpi <= 0:
             messagebox.showwarning("警告", "DPI值必须大于0。")
             return

        # 修复：移除了包含 .setpdfwrite 的参数，该参数在新版本Ghostscript中已不支持
        gs_args = [
            GS_COMMAND,
            '-dNOPAUSE', '-dBATCH', '-dSAFER',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS={quality_preset}',
            '-dDownsampleColorImages=true',
            f'-dColorImageResolution={dpi}',
            '-dColorImageDownsampleType=/Bicubic',
            '-dDownsampleGrayImages=true',
            f'-dGrayImageResolution={dpi}',
            '-dGrayImageDownsampleType=/Bicubic',
            '-dDownsampleMonoImages=true',
            f'-dMonoImageResolution={dpi}',
            '-dMonoImageDownsampleType=/Bicubic',
            '-dAutoRotatePages=/None',
            '-dColorConversionStrategy=/LeaveColorUnchanged',
            '-dEmbedAllFonts=true',
            '-dSubsetFonts=true',
            '-dCompressFonts=true',
            f'-sOutputFile={output_path}',
            '-f', input_path  # 直接指定输入文件，移除了 .setpdfwrite 相关参数
        ]

        try:
            result = subprocess.run(gs_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    original_size = os.path.getsize(input_path)
                    compressed_size = os.path.getsize(output_path)
                    reduction = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                    messagebox.showinfo("成功", f"PDF压缩完成！\n"
                                                f"原文件大小: {original_size / 1024:.2f} KB\n"
                                                f"压缩后大小: {compressed_size / 1024:.2f} KB\n"
                                                f"体积减小: {reduction:.1f}%\n"
                                                f"保存至: {output_path}")
                else:
                    messagebox.showwarning("警告", "压缩过程完成，但输出文件似乎无效。")
            else:
                error_msg = f"Ghostscript 执行失败: {result.stderr}"
                print(error_msg)
                messagebox.showerror("错误", f"压缩失败: {error_msg}")

        except Exception as e:
            messagebox.showerror("错误", f"压缩失败，请检查文件和参数")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFezyApp(root)
    root.mainloop()
