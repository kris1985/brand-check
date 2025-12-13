#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片品牌检查工具
根据图片文件名中的品牌名，检查品牌是否存在
将未找到对应品牌的文件复制到新文件夹
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import unicodedata
import re
from pathlib import Path
import threading
import shutil
import subprocess
import platform


class BrandCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片品牌检查工具")
        self.root.geometry("700x500")
        
        self.brand_dir = ""
        self.image_dir = ""
        self.brands = set()
        self.is_processing = False  # 标记是否正在处理，防止重复点击
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 品牌目录选择
        ttk.Label(main_frame, text="品牌根目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.brand_dir_label = ttk.Label(main_frame, text="未选择", foreground="gray")
        self.brand_dir_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="选择目录", command=self.select_brand_dir).grid(row=0, column=2, pady=5)
        
        # 图片目录选择
        ttk.Label(main_frame, text="图片根目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.image_dir_label = ttk.Label(main_frame, text="未选择", foreground="gray")
        self.image_dir_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="选择目录", command=self.select_image_dir).grid(row=1, column=2, pady=5)
        
        # 分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=tk.W)
        
        # 创建按钮，设置最小宽度，确保整个按钮区域可点击
        self.process_button = ttk.Button(
            button_frame, 
            text="开始检查", 
            command=self.start_processing, 
            state=tk.DISABLED,
            width=15  # 设置按钮宽度，确保有足够的可点击区域
        )
        self.process_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 状态标签（显示loading状态）
        self.status_label = ttk.Label(button_frame, text="", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 日志输出区域
        ttk.Label(main_frame, text="处理日志:").grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # 文本区域和滚动条
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def log(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def select_brand_dir(self):
        """选择品牌根目录"""
        directory = filedialog.askdirectory(title="选择品牌根目录")
        if directory:
            self.brand_dir = directory
            self.brand_dir_label.config(text=directory, foreground="black")
            self.log(f"已选择品牌目录: {directory}")
            # 清空之前的品牌列表
            self.brands = set()
            
    def select_image_dir(self):
        """选择图片根目录"""
        directory = filedialog.askdirectory(title="选择图片根目录")
        if directory:
            self.image_dir = directory
            self.image_dir_label.config(text=directory, foreground="black")
            self.log(f"已选择图片目录: {directory}")
            # 如果品牌目录和图片目录都已选择，启用开始检查按钮
            if self.brand_dir and self.image_dir:
                self.process_button.config(state=tk.NORMAL)
            
    def normalize_text(self, text):
        """
        标准化文本：移除重音符号，转换为小写
        例如：Été -> ete, Café -> cafe
        """
        # 使用NFD分解，然后过滤掉组合标记（重音符号）
        nfd = unicodedata.normalize('NFD', text)
        # 只保留非组合字符（即去掉重音符号）
        no_accent = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        return no_accent.lower()
        
    def scan_brands(self):
        """扫描品牌目录，获取所有品牌名称（不输出日志）"""
        if not self.brand_dir:
            return False
            
        self.brands = set()
        try:
            brand_path = Path(self.brand_dir)
            if not brand_path.exists():
                return False
                
            # 仅识别第三级目录为品牌名
            for second_level in brand_path.iterdir():
                if second_level.is_dir():
                    for third_level in second_level.iterdir():
                        if third_level.is_dir():
                            brand_name = third_level.name
                            self.brands.add(brand_name)
                    
            # 创建标准化品牌名映射（用于快速查找）
            self.normalized_brands = {}
            for brand in self.brands:
                normalized = self.normalize_text(brand)
                if normalized not in self.normalized_brands:
                    self.normalized_brands[normalized] = []
                self.normalized_brands[normalized].append(brand)
                
            return True
            
        except Exception as e:
            return False
            
    def extract_brand_from_filename(self, filename):
        """
        从文件名中提取品牌名
        格式：品牌_Brador_2025年03月16日_03_1.jpg
        品牌名在第一个下划线和第二个下划线之间
        """
        # 移除文件扩展名
        name_without_ext = os.path.splitext(filename)[0]
        
        # 按下划线分割
        parts = name_without_ext.split('_')
        
        # 如果至少有2个部分，第二个部分（索引1）应该是品牌名
        if len(parts) >= 2:
            return parts[1]  # 返回品牌名部分
        return None
        
    def find_brand_match(self, brand_name):
        """
        查找匹配的品牌（不区分大小写和重音）
        返回匹配的品牌名，如果没有匹配则返回None
        """
        if not brand_name:
            return None
            
        normalized_brand = self.normalize_text(brand_name)
        
        # 在标准化品牌名中查找
        if normalized_brand in self.normalized_brands:
            # 返回第一个匹配的品牌名（原始名称）
            return self.normalized_brands[normalized_brand][0]
            
        return None
        
    def reset_button_state(self):
        """重置按钮状态（在主线程中调用）"""
        self.is_processing = False
        self.process_button.config(state=tk.NORMAL, text="开始检查")
        self.progress.stop()
    
    def show_warning(self, title, message):
        """在主线程中显示警告"""
        messagebox.showwarning(title, message)
    
    def show_error(self, title, message):
        """在主线程中显示错误"""
        messagebox.showerror(title, message)
    
    def show_info(self, title, message):
        """在主线程中显示信息"""
        messagebox.showinfo(title, message)
    
    def process_images(self):
        """处理图片文件"""
        try:
            if not self.image_dir:
                self.update_ui_safe(lambda: self.reset_button_state())
                self.update_ui_safe(lambda: self.status_label.config(text="", foreground="blue"))
                self.update_ui_safe(lambda: self.show_warning("警告", "请先选择图片根目录"))
                return
                
            if not self.brand_dir:
                self.update_ui_safe(lambda: self.reset_button_state())
                self.update_ui_safe(lambda: self.status_label.config(text="", foreground="blue"))
                self.update_ui_safe(lambda: self.show_warning("警告", "请先选择品牌根目录"))
                return
            
            # 点击开始检查时才扫描品牌
            self.log("正在扫描品牌目录...")
            if not self.scan_brands():
                self.update_ui_safe(lambda: self.reset_button_state())
                self.update_ui_safe(lambda: self.status_label.config(text="扫描品牌失败", foreground="red"))
                self.update_ui_safe(lambda: self.show_error("错误", "扫描品牌目录失败，请检查品牌根目录是否正确"))
                return
            
            if not self.brands:
                self.update_ui_safe(lambda: self.reset_button_state())
                self.update_ui_safe(lambda: self.status_label.config(text="未发现品牌", foreground="red"))
                self.update_ui_safe(lambda: self.show_warning("警告", "品牌目录下没有找到任何品牌子目录"))
                return
                
            self.log(f"已加载 {len(self.brands)} 个品牌，开始处理图片...")
                
            image_path = Path(self.image_dir)
            if not image_path.exists():
                self.update_ui_safe(lambda: self.reset_button_state())
                self.update_ui_safe(lambda: self.status_label.config(text="目录不存在", foreground="red"))
                self.update_ui_safe(lambda: self.show_error("错误", "图片目录不存在"))
                return
                
            self.log("\n开始处理图片文件...")
            # 进度条已在 start_processing 中启动
            
            # 支持的图片扩展名
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
            
            processed_files = 0
            found_brand_files = 0
            not_found_files = []  # 存储未找到品牌的文件路径
            
            # 递归遍历所有文件
            for root, dirs, files in os.walk(self.image_dir):
                root_path = Path(root)
                
                # 处理当前目录下的所有文件
                for filename in files:
                    file_path = root_path / filename
                    
                    # 检查是否是图片文件
                    if file_path.suffix.lower() in image_extensions:
                        processed_files += 1
                        
                        # 从文件名提取品牌名
                        brand_name = self.extract_brand_from_filename(filename)
                        
                        if brand_name:
                            # 查找匹配的品牌
                            matched_brand = self.find_brand_match(brand_name)
                            
                            if matched_brand:
                                # 品牌存在，记录
                                found_brand_files += 1
                                self.log(f"✓ 找到品牌: {filename} (品牌: {matched_brand})")
                            else:
                                # 品牌不存在，添加到待复制列表
                                not_found_files.append(file_path)
                                self.log(f"✗ 未找到品牌: {filename} (品牌: {brand_name})")
                        else:
                            # 无法提取品牌名，添加到待复制列表
                            not_found_files.append(file_path)
                            self.log(f"✗ 未找到品牌: {filename} (无法提取品牌名)")
            
            # 处理结果
            if not not_found_files:
                # 所有文件都找到了品牌
                self.update_ui_safe(lambda: self.reset_button_state())
                self.update_ui_safe(lambda: self.status_label.config(text="检测通过！", foreground="green"))
                self.log(f"\n检测完成！")
                self.log(f"  处理文件数: {processed_files}")
                self.log(f"  找到品牌文件数: {found_brand_files}")
                self.log(f"  未找到品牌文件数: 0")
                
                self.update_ui_safe(lambda: self.show_info("检测通过", 
                                  f"检测通过，所有图片都找到对应品牌！\n\n"
                                  f"处理文件数: {processed_files}\n"
                                  f"找到品牌文件数: {found_brand_files}"))
            else:
                # 有未找到品牌的文件，复制到新文件夹
                self.log(f"\n开始复制未找到品牌的文件...")
                
                # 创建新文件夹
                image_path = Path(self.image_dir)
                parent_dir = image_path.parent
                folder_name = f"{image_path.name}_未找到品牌图片"
                output_dir = parent_dir / folder_name
                
                # 创建文件夹（如果不存在）
                output_dir.mkdir(parents=True, exist_ok=True)
                self.log(f"  目标文件夹: {output_dir}")
                
                # 复制文件（所有文件都复制到目标文件夹根目录）
                copied_count = 0
                file_counter = {}  # 用于处理重名文件
                
                for file_path in not_found_files:
                    try:
                        # 所有文件都复制到目标文件夹根目录
                        dest_filename = file_path.name
                        
                        # 如果文件名已存在，添加序号
                        if dest_filename in file_counter:
                            file_counter[dest_filename] += 1
                            name_parts = dest_filename.rsplit('.', 1)
                            if len(name_parts) == 2:
                                dest_filename = f"{name_parts[0]}_{file_counter[dest_filename]}.{name_parts[1]}"
                            else:
                                dest_filename = f"{dest_filename}_{file_counter[dest_filename]}"
                        else:
                            file_counter[dest_filename] = 0
                        
                        dest_path = output_dir / dest_filename
                        
                        # 复制文件
                        shutil.copy2(file_path, dest_path)
                        copied_count += 1
                        self.log(f"  已复制: {file_path.name} -> {dest_filename}")
                    except Exception as e:
                        self.log(f"  复制失败: {file_path.name} - {str(e)}")
                
                self.update_ui_safe(lambda: self.reset_button_state())
                self.update_ui_safe(lambda: self.status_label.config(text="处理完成！", foreground="green"))
                self.log(f"\n处理完成！")
                self.log(f"  处理文件数: {processed_files}")
                self.log(f"  找到品牌文件数: {found_brand_files}")
                self.log(f"  未找到品牌文件数: {len(not_found_files)}")
                self.log(f"  已复制文件数: {copied_count}")
                
                self.update_ui_safe(lambda: self.show_info("处理完成", 
                                  f"处理完成！\n\n"
                                  f"处理文件数: {processed_files}\n"
                                  f"找到品牌文件数: {found_brand_files}\n"
                                  f"未找到品牌文件数: {len(not_found_files)}\n"
                                  f"已复制到: {folder_name}"))
                
                # 自动打开文件夹
                self.open_folder(output_dir)
                              
        except Exception as e:
            # 恢复按钮状态（在主线程中更新）
            self.update_ui_safe(lambda: self.reset_button_state())
            self.update_ui_safe(lambda: self.status_label.config(text="处理失败", foreground="red"))
            self.update_ui_safe(lambda: self.show_error("错误", f"处理图片时出错: {str(e)}"))
            self.log(f"错误: {str(e)}")
    
    def open_folder(self, folder_path):
        """打开文件夹（跨平台）"""
        try:
            folder_path = Path(folder_path)
            if not folder_path.exists():
                self.log(f"  警告: 文件夹不存在: {folder_path}")
                return
                
            system = platform.system()
            if system == "Windows":
                os.startfile(str(folder_path))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(folder_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(folder_path)])
            
            self.log(f"  已打开文件夹: {folder_path}")
        except Exception as e:
            self.log(f"  打开文件夹失败: {str(e)}")
            
    def clean_empty_dirs(self, root_path):
        """清理空目录，返回删除的目录数（递归删除所有空目录）
        
        检查图片根目录下的所有子文件夹，如果子文件夹是空的则删除。
        包括嵌套的子文件夹，如果删除子文件夹后父文件夹也变成空的，也会被删除。
        """
        deleted_count = 0
        
        # 使用循环方式，确保所有空目录都被删除
        # 因为删除子目录后，父目录可能也变成空的，需要多次检查
        max_iterations = 50  # 最多检查50次，避免无限循环（支持深层嵌套）
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            found_empty = False
            
            # 从最深层的目录开始遍历（topdown=False）
            # 这样可以先删除最深层的空目录，然后检查父目录
            for root, dirs, files in os.walk(root_path, topdown=False):
                root_path_obj = Path(root)
                
                # 跳过根目录本身（不删除用户选择的根目录）
                if root_path_obj == root_path:
                    continue
                    
                try:
                    # 检查目录是否为空
                    # 使用 listdir() 获取所有条目（包括隐藏文件）
                    # 但排除系统文件如 .DS_Store, Thumbs.db 等
                    entries = list(root_path_obj.iterdir())
                    
                    # 过滤掉常见的系统文件（这些文件不应该阻止目录删除）
                    system_files = {'.DS_Store', 'Thumbs.db', '.gitkeep', '.gitignore'}
                    filtered_entries = [e for e in entries if e.name not in system_files]
                    
                    if not filtered_entries:
                        # 目录为空（或只有系统文件），删除它
                        try:
                            root_path_obj.rmdir()
                            deleted_count += 1
                            found_empty = True
                            # 显示相对路径，更易读
                            relative_path = root_path_obj.relative_to(root_path)
                            self.log(f"  删除空目录: {relative_path}")
                        except OSError as e:
                            # 如果删除失败，记录详细信息用于调试
                            relative_path = root_path_obj.relative_to(root_path)
                            self.log(f"  无法删除目录 {relative_path}: {str(e)}")
                            # 列出目录内容用于调试
                            if entries:
                                entry_names = [e.name for e in entries]
                                self.log(f"    目录内容: {', '.join(entry_names)}")
                    else:
                        # 目录不为空，记录调试信息（仅在第一次迭代时）
                        if iteration == 1:
                            relative_path = root_path_obj.relative_to(root_path)
                            entry_names = [e.name for e in filtered_entries]
                            self.log(f"  保留目录（非空）: {relative_path} - 包含: {', '.join(entry_names[:5])}{'...' if len(entry_names) > 5 else ''}")
                            
                except PermissionError as e:
                    # 权限不足
                    relative_path = root_path_obj.relative_to(root_path)
                    self.log(f"  权限不足，无法访问目录: {relative_path}")
                except OSError:
                    # 目录可能已经被删除或不存在，忽略
                    pass
                except Exception as e:
                    relative_path = root_path_obj.relative_to(root_path) if root_path_obj != root_path else str(root_path_obj)
                    self.log(f"  检查目录时出错 {relative_path}: {str(e)}")
            
            # 如果这一轮没有找到空目录，说明已经清理完毕
            if not found_empty:
                break
        
        if iteration >= max_iterations:
            self.log(f"  警告: 达到最大迭代次数 ({max_iterations})，可能还有空目录未清理")
                
        return deleted_count
        
    def start_processing(self, event=None):
        """在新线程中开始处理，避免界面冻结"""
        # 防止重复点击
        if self.is_processing:
            return
        
        # 检查按钮状态
        if self.process_button['state'] == 'disabled':
            return
        
        # 检查必要条件
        if not self.brand_dir or not self.image_dir:
            messagebox.showwarning("警告", "请先选择品牌根目录和图片根目录")
            return
        
        # 设置处理状态
        self.is_processing = True
        
        # 显示loading状态（在主线程中更新UI）
        self.process_button.config(state=tk.DISABLED, text="处理中...")
        self.status_label.config(text="正在处理，请稍候...", foreground="blue")
        self.progress.start(10)  # 立即启动进度条动画
        
        # 在新线程中处理，避免界面冻结
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()
    
    def update_ui_safe(self, func):
        """在主线程中安全更新UI"""
        self.root.after(0, func)


def main():
    root = tk.Tk()
    app = BrandCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

