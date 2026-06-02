import sys
from PyPDF2 import PdfMerger

def merge_pdfs(pdf1_path, pdf2_path, output_path):
    try:
        merger = PdfMerger()
        merger.append(pdf1_path)
        merger.append(pdf2_path)
        merger.write(output_path)
        merger.close()
        print(f"✅ 合并成功！文件保存至：{output_path}")
    except FileNotFoundError as e:
        print(f"❌ 错误：找不到文件 '{e.filename}'")
    except Exception as e:
        print(f"❌ 合并失败：{str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法：将两个PDF拖到窗口，或输入命令：")
        print("merge_pdfs 第一个文件.pdf 第二个文件.pdf 合并后的文件.pdf")
        sys.exit(1)
    
    merge_pdfs(sys.argv[1], sys.argv[2], sys.argv[3])