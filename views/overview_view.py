import tkinter as tk
from tkinter import ttk
import pandas as pd

class OverviewView:
    """Lớp quản lý giao diện tab tổng quan"""
    
    def __init__(self, parent, controller):
        """Khởi tạo giao diện tab tổng quan
        
        Args:
            parent: Frame cha
            controller: Controller điều khiển ứng dụng
        """
        self.parent = parent
        self.controller = controller
        
        # Tạo giao diện
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo các widget cho tab tổng quan"""
        # Frame chính
        main_frame = ttk.LabelFrame(self.parent, text="Thống kê tổng quan")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame thông tin cơ bản
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin cơ bản")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Số lượng thí sinh
        self.total_label = ttk.Label(info_frame, text="Tổng số thí sinh: 0")
        self.total_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        # Frame thống kê môn học
        subjects_frame = ttk.LabelFrame(main_frame, text="Thống kê theo môn học")
        subjects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo bảng thống kê
        columns = ("subject", "count", "percentage", "mean", "max")
        self.tree = ttk.Treeview(subjects_frame, columns=columns, show="headings")
        
        # Thiết lập tiêu đề cột
        self.tree.heading("subject", text="Môn học")
        self.tree.heading("count", text="Số lượng")
        self.tree.heading("percentage", text="Tỷ lệ (%)")
        self.tree.heading("mean", text="Điểm TB")
        self.tree.heading("max", text="Điểm cao nhất")
        
        # Thiết lập độ rộng cột
        self.tree.column("subject", width=150)
        self.tree.column("count", width=100, anchor=tk.CENTER)
        self.tree.column("percentage", width=100, anchor=tk.CENTER)
        self.tree.column("mean", width=100, anchor=tk.CENTER)
        self.tree.column("max", width=100, anchor=tk.CENTER)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(subjects_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí các thành phần
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def update(self, stats):
        """Cập nhật thông tin thống kê
        
        Args:
            stats: Dictionary chứa thông tin thống kê
        """
        if not stats:
            return
        
        # Cập nhật tổng số thí sinh
        self.total_label.config(text=f"Tổng số thí sinh: {stats['total_students']}")
        
        # Xóa dữ liệu cũ trong bảng
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Thêm dữ liệu mới vào bảng
        for subject, (count, percentage) in stats['subject_counts'].items():
            mean = stats['subject_means'].get(subject, None)
            max_score = stats['subject_max'].get(subject, None)
            
            mean_str = f"{mean:.2f}" if mean is not None else "N/A"
            max_str = f"{max_score:.2f}" if max_score is not None else "N/A"
            
            self.tree.insert("", tk.END, values=(
                subject,
                count,
                f"{percentage:.2f}",
                mean_str,
                max_str
            ))