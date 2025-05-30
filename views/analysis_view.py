import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AnalysisView:
    """Lớp quản lý giao diện tab phân tích"""
    
    def __init__(self, parent, controller):
        """Khởi tạo giao diện tab phân tích
        
        Args:
            parent: Frame cha
            controller: Controller điều khiển ứng dụng
        """
        self.parent = parent
        self.controller = controller
        self.subject_names = []
        self.canvas = None
        self.figure = None
        
        # Tạo giao diện
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo các widget cho tab phân tích"""
        # Frame chính
        main_frame = ttk.LabelFrame(self.parent, text="Phân tích điểm thi")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame chọn môn học
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(select_frame, text="Chọn môn học:").pack(side=tk.LEFT, padx=5)
        self.subject_combo = ttk.Combobox(select_frame, width=20, state="readonly")
        self.subject_combo.pack(side=tk.LEFT, padx=5)
        self.subject_combo.bind("<<ComboboxSelected>>", self.analyze_subject)
        
        # Frame kết quả phân tích - chia thành 3 phần
        result_frame = ttk.LabelFrame(main_frame, text="Kết quả phân tích")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Phần trên: thống kê cơ bản và phân phối điểm
        top_frame = ttk.Frame(result_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Phần dưới: biểu đồ
        chart_frame = ttk.LabelFrame(result_frame, text="Biểu đồ phân phối điểm")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Phần thống kê cơ bản
        stats_frame = ttk.LabelFrame(left_frame, text="Thống kê cơ bản")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo các nhãn hiển thị thông tin
        self.stats_labels = {}
        stats = [
            "Số lượng", "Điểm trung bình", "Điểm trung vị", 
            "Độ lệch chuẩn", "Điểm thấp nhất", "Điểm cao nhất"
        ]
        
        for i, stat in enumerate(stats):
            ttk.Label(stats_frame, text=f"{stat}:").grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            self.stats_labels[stat] = ttk.Label(stats_frame, text="")
            self.stats_labels[stat].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Phần phân phối điểm
        dist_frame = ttk.LabelFrame(right_frame, text="Phân phối điểm")
        dist_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo bảng phân phối
        columns = ("range", "count", "percentage")
        self.tree = ttk.Treeview(dist_frame, columns=columns, show="headings")
        
        # Thiết lập tiêu đề cột
        self.tree.heading("range", text="Khoảng điểm")
        self.tree.heading("count", text="Số lượng")
        self.tree.heading("percentage", text="Tỷ lệ (%)")
        
        # Thiết lập độ rộng cột
        self.tree.column("range", width=100, anchor=tk.CENTER)
        self.tree.column("count", width=100, anchor=tk.CENTER)
        self.tree.column("percentage", width=100, anchor=tk.CENTER)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(dist_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí các thành phần
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Tạo biểu đồ matplotlib
        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_subject_list(self, subjects):
        """Cập nhật danh sách môn học
        
        Args:
            subjects: Danh sách tên các môn học
        """
        self.subject_names = subjects
        self.subject_combo['values'] = subjects
        if subjects:
            self.subject_combo.current(0)
    
    def analyze_subject(self, event=None):
        """Phân tích môn học đã chọn"""
        subject = self.subject_combo.get()
        if subject:
            self.controller.analyze_subject(subject)
    
    def update_result(self, subject_name, stats):
        """Cập nhật kết quả phân tích"""
        if not stats:
            print("Không có dữ liệu thống kê để hiển thị")
            return
        
        print(f"Cập nhật kết quả cho môn: {subject_name}")
        print(f"Stats nhận được: {stats}")
        
        # Cập nhật thống kê cơ bản
        self.stats_labels["Số lượng"].config(text=str(stats['count']))
        self.stats_labels["Điểm trung bình"].config(text=f"{stats['mean']:.2f}")
        self.stats_labels["Điểm trung vị"].config(text=f"{stats['median']:.2f}")
        self.stats_labels["Độ lệch chuẩn"].config(text=f"{stats['std']:.2f}")
        self.stats_labels["Điểm thấp nhất"].config(text=f"{stats['min']:.2f}")
        self.stats_labels["Điểm cao nhất"].config(text=f"{stats['max']:.2f}")
        
        print(f"Đã cập nhật điểm thấp nhất: {stats['min']:.2f}")
        
        # Xóa dữ liệu cũ trong bảng phân phối
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Thêm dữ liệu mới vào bảng phân phối
        for dist in stats['distribution']:
            range_str = f"{dist['range'][0]} - {dist['range'][1]}"
            self.tree.insert("", tk.END, values=(
                range_str,
                dist['count'],
                f"{dist['percentage']:.2f}"
            ))
        
        # Vẽ biểu đồ phân phối điểm
        self.draw_distribution_chart(subject_name, stats)
    
    def draw_distribution_chart(self, subject_name, stats):
        """Vẽ biểu đồ phân phối điểm
        
        Args:
            subject_name: Tên môn học
            stats: Dictionary chứa thông tin thống kê
        """
        # Xóa biểu đồ cũ
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Tạo dữ liệu cho biểu đồ từ phân phối
        ranges = []
        counts = []
        
        for dist in stats['distribution']:
            # Tạo nhãn cho khoảng điểm
            range_label = f"{dist['range'][0]}-{dist['range'][1]}"
            ranges.append(range_label)
            counts.append(dist['count'])
        
        # Vẽ biểu đồ cột
        bars = ax.bar(ranges, counts, color='skyblue', edgecolor='black', alpha=0.7)
        
        # Thiết lập tiêu đề và nhãn
        ax.set_title(f'Biểu đồ phân phối điểm thi THPT môn {subject_name} - năm 2024', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Điểm', fontsize=12)
        ax.set_ylabel('Số lượng thí sinh', fontsize=12)
        
        # Thêm giá trị lên đầu mỗi cột
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                   f'{count}', ha='center', va='bottom', fontsize=10)
        
        # Thiết lập lưới và định dạng
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')
        ax.set_axisbelow(True)
        
        # Xoay nhãn trục x nếu cần
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Thêm chú thích
        # ax.text(0.02, 0.98, 'Phổ điểm tốt nghiệp THPT 2024: Cần cứ quan trọng trong lựa chọn ngành nghề', 
        #        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        #        bbox=dict(boxstyle='round', facecolor='black', alpha=0.8, edgecolor='none'),
        #        color='white')
        
        # Điều chỉnh layout và cập nhật canvas
        self.figure.tight_layout()
        self.canvas.draw()