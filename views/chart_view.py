import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import seaborn as sns

class ChartView:
    """Lớp quản lý giao diện tab biểu đồ"""
    
    def __init__(self, parent, controller):
        """Khởi tạo giao diện tab biểu đồ"""
        self.parent = parent
        self.controller = controller
        self.canvas = None
        self.figure = None
        
        # Tạo giao diện
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo các widget cho tab biểu đồ"""
        # Frame chính
        main_frame = ttk.LabelFrame(self.parent, text="Biểu đồ phan tích đa dạng")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame điều khiển
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Chọn loại biểu đồ
        ttk.Label(control_frame, text="Loại biểu đồ:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.chart_type_combo = ttk.Combobox(control_frame, width=40, state="readonly")
        self.chart_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.chart_type_combo['values'] = [
            "Biểu đồ cột - Điểm trung bình các môn học",
            "Histogram - Phân phối điểm theo môn học", 
            "Biểu đồ tròn - Tỷ lệ học sinh theo tổ hợp môn",
            "Box plot - So sánh điểm các tổ hợp môn",
            "Scatter plot - Tương quan giữa 2 môn học",
            "Biểu đồ cột ngang - Top học sinh điểm cao",
            "Ma trận tương quan - Tất cả môn học",
            "Phân phối điểm - Tất cả môn học"
        ]
        self.chart_type_combo.current(0)
        self.chart_type_combo.bind('<<ComboboxSelected>>', self.on_chart_type_change)
        
        # Frame cho các tùy chọn bổ sung
        self.options_frame = ttk.Frame(control_frame)
        self.options_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # Tùy chọn chọn môn học (cho histogram và scatter plot)
        self.subject_frame = ttk.Frame(self.options_frame)
        ttk.Label(self.subject_frame, text="Chọn môn:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_combo = ttk.Combobox(self.subject_frame, width=20, state="readonly")
        self.subject_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Tùy chọn chọn môn học thứ 2 (cho scatter plot)
        ttk.Label(self.subject_frame, text="Môn thứ 2:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.subject2_combo = ttk.Combobox(self.subject_frame, width=20, state="readonly")
        self.subject2_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Tùy chọn số lượng top học sinh
        self.top_frame = ttk.Frame(self.options_frame)
        ttk.Label(self.top_frame, text="Số lượng top:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.top_spinbox = tk.Spinbox(self.top_frame, from_=10, to=50, width=10, value=20)
        self.top_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Nút vẽ biểu đồ
        ttk.Button(control_frame, text="Tạo biểu đồ", command=self.draw_chart).grid(row=0, column=2, padx=5, pady=5)
        
        # Khung hiển thị biểu đồ
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo figure matplotlib
        self.figure = plt.Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Cập nhật danh sách môn học
        self.update_subject_combos()
        
        # Cập nhật hiển thị tùy chọn ban đầu
        self.on_chart_type_change()
    
    def update_subject_combos(self):
        """Cập nhật danh sách môn học cho combobox"""
        subjects = self.controller.get_subjects_list()
        
        # Xử lý cả trường hợp list và dictionary
        if isinstance(subjects, dict):
            subject_names = [name for code, name in subjects.items()]
        else:
            # Nếu là list, sử dụng trực tiếp
            subject_names = subjects
        
        self.subject_combo['values'] = subject_names
        self.subject2_combo['values'] = subject_names
        
        if subject_names:
            self.subject_combo.current(0)
            if len(subject_names) > 1:
                self.subject2_combo.current(1)
    
    def update_subject_list(self, subjects):
        """Cập nhật danh sách môn học (interface method cho main_view)"""
        # Gọi method hiện có để cập nhật combobox
        self.update_subject_combos()
    
    def on_chart_type_change(self, event=None):
        """Xử lý khi thay đổi loại biểu đồ"""
        chart_type = self.chart_type_combo.get()
        
        # Ẩn tất cả frame tùy chọn
        self.subject_frame.grid_remove()
        self.top_frame.grid_remove()
        
        # Hiển thị frame tùy chọn phù hợp
        if "Histogram" in chart_type:
            self.subject_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            # Ẩn môn thứ 2 cho histogram
            self.subject2_combo.grid_remove()
            # Tìm và ẩn label "Môn thứ 2:"
            for widget in self.subject_frame.winfo_children():
                if isinstance(widget, ttk.Label) and widget.cget('text') == "Môn thứ 2:":
                    widget.grid_remove()
                    break
        elif "Scatter plot" in chart_type:
            self.subject_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            # Hiển thị môn thứ 2 cho scatter plot
            self.subject2_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
            # Tìm và hiển thị label "Môn thứ 2:"
            for widget in self.subject_frame.winfo_children():
                if isinstance(widget, ttk.Label) and widget.cget('text') == "Môn thứ 2:":
                    widget.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
                    break
        elif "Top học sinh" in chart_type:
            self.top_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    
    def draw_chart(self):
        """Vẽ biểu đồ theo loại được chọn"""
        chart_type = self.chart_type_combo.get()
        
        # Xóa biểu đồ cũ
        self.figure.clear()
        
        try:
            if "Biểu đồ cột - Điểm trung bình" in chart_type:
                self.draw_average_scores_chart()
            elif "Histogram" in chart_type:
                self.draw_histogram_chart()
            elif "Biểu đồ tròn" in chart_type:
                self.draw_pie_chart()
            elif "Box plot" in chart_type:
                self.draw_boxplot_chart()
            elif "Scatter plot" in chart_type:
                self.draw_scatter_chart()
            elif "Top học sinh" in chart_type:
                self.draw_top_students_chart()
            elif "Ma trận tương quan" in chart_type:
                self.draw_correlation_matrix()
            elif "Phân phối điểm - Tất cả môn học" in chart_type:
                self.draw_all_subjects_comparison()
            
            self.canvas.draw()
        except Exception as e:
            # Hiển thị lỗi trên biểu đồ
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Lỗi: {str(e)}', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='red')
            ax.set_title('Lỗi khi tạo biểu đồ')
            self.canvas.draw()
    
    def draw_average_scores_chart(self):
        """Vẽ biểu đồ cột điểm trung bình các môn"""
        data = self.controller.model.get_subject_averages()
        if not data:
            return
        
        ax = self.figure.add_subplot(111)
        subjects = list(data.keys())
        averages = list(data.values())
        
        bars = ax.bar(subjects, averages, color='skyblue', edgecolor='navy', alpha=0.7)
        ax.set_title('Điểm trung bình các môn thi THPT 2024', fontsize=16, fontweight='bold')
        ax.set_xlabel('Môn học', fontsize=12)
        ax.set_ylabel('Điểm trung bình', fontsize=12)
        ax.set_ylim(0, 10)
        
        # Thêm giá trị lên đầu cột
        for bar, avg in zip(bars, averages):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   f'{avg:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
    
    def draw_histogram_chart(self):
        """Vẽ histogram phân phối điểm một môn"""
        subject_name = self.subject_combo.get()
        if not subject_name:
            return
        
        # Tìm mã môn học - xử lý cả dictionary và list
        subjects = self.controller.get_subjects_list()
        subject_code = None
        
        if isinstance(subjects, dict):
            # Nếu là dictionary
            for code, name in subjects.items():
                if name == subject_name:
                    subject_code = code
                    break
        else:
            # Nếu là list, sử dụng subjects_dict trực tiếp
            subjects_dict = self.controller.model.subjects_dict
            for code, name in subjects_dict.items():
                if name == subject_name:
                    subject_code = code
                    break
        
        if not subject_code:
            return
        
        data = self.controller.model.get_subject_distribution_data(subject_code)
        if data is None or len(data) == 0:
            return
        
        ax = self.figure.add_subplot(111)
        n, bins, patches = ax.hist(data, bins=20, color='lightcoral', edgecolor='darkred', alpha=0.7)
        
        ax.set_title(f'Phân phối điểm môn {subject_name}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Điểm số', fontsize=12)
        ax.set_ylabel('Số lượng học sinh', fontsize=12)
        
        # Thêm thống kê
        mean_score = data.mean()
        std_score = data.std()
        ax.axvline(mean_score, color='red', linestyle='--', linewidth=2, label=f'TB: {mean_score:.1f}')
        ax.legend()
        
        # Thêm text box thống kê
        stats_text = f'Trung bình: {mean_score:.2f}\nĐộ lệch chuẩn: {std_score:.2f}\nSố học sinh: {len(data)}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
    
    def draw_pie_chart(self):
        """Vẽ biểu đồ tròn tỷ lệ tổ hợp môn"""
        data = self.controller.model.get_combination_ratios()
        if not data:
            return
        
        ax = self.figure.add_subplot(111)
        
        combinations = list(data.keys())
        percentages = [data[combo]['percentage'] for combo in combinations]
        counts = [data[combo]['count'] for combo in combinations]
        
        # Loại bỏ tổ hợp có tỷ lệ quá nhỏ
        filtered_data = [(combo, pct, cnt) for combo, pct, cnt in zip(combinations, percentages, counts) if pct > 1]
        
        if not filtered_data:
            return
        
        combos, pcts, cnts = zip(*filtered_data)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(combos)))
        wedges, texts, autotexts = ax.pie(pcts, labels=combos, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        ax.set_title('Tỷ lệ học sinh theo tổ hợp môn thi', fontsize=16, fontweight='bold')
        
        # Thêm legend với số lượng
        legend_labels = [f'{combo}: {cnt} học sinh' for combo, cnt in zip(combos, cnts)]
        ax.legend(wedges, legend_labels, title="Tổ hợp môn", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        self.figure.tight_layout()
    
    def draw_boxplot_chart(self):
        """Vẽ box plot so sánh điểm các tổ hợp"""
        data = self.controller.model.get_combination_comparison_data()
        if not data:
            return
        
        ax = self.figure.add_subplot(111)
        
        combinations = list(data.keys())
        scores_data = [data[combo].tolist() for combo in combinations]
        
        bp = ax.boxplot(scores_data, labels=combinations, patch_artist=True)
        
        # Tô màu các box
        colors = plt.cm.Set2(np.linspace(0, 1, len(combinations)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title('So sánh phân phối điểm các tổ hợp môn', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tổ hợp môn', fontsize=12)
        ax.set_ylabel('Tổng điểm 3 môn', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
    
    def draw_scatter_chart(self):
        """Vẽ scatter plot tương quan 2 môn"""
        subject1_name = self.subject_combo.get()
        subject2_name = self.subject2_combo.get()
        
        if not subject1_name or not subject2_name or subject1_name == subject2_name:
            return
        
        # Tìm mã môn học
        subjects = self.controller.get_subjects_list()
        subject1_code = subject2_code = None
        
        for code, name in subjects.items():
            if name == subject1_name:
                subject1_code = code
            elif name == subject2_name:
                subject2_code = code
        
        if not subject1_code or not subject2_code:
            return
        
        data = self.controller.model.get_subject_correlation_data(subject1_code, subject2_code)
        if not data:
            return
        
        ax = self.figure.add_subplot(111)
        
        scatter = ax.scatter(data['x'], data['y'], alpha=0.6, c='blue', s=20)
        
        # Tính hệ số tương quan
        correlation = np.corrcoef(data['x'], data['y'])[0, 1]
        
        # Vẽ đường trend
        z = np.polyfit(data['x'], data['y'], 1)
        p = np.poly1d(z)
        ax.plot(data['x'], p(data['x']), "r--", alpha=0.8, linewidth=2)
        
        ax.set_title(f'Tương quan giữa {subject1_name} và {subject2_name}\n(r = {correlation:.3f})', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel(f'Điểm {subject1_name}', fontsize=12)
        ax.set_ylabel(f'Điểm {subject2_name}', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
    
    def draw_top_students_chart(self):
        """Vẽ biểu đồ cột ngang top học sinh"""
        top_n = int(self.top_spinbox.get())
        data = self.controller.model.get_top_students_data(top_n)  # Sửa tên method
        
        if not data:
            return
        
        ax = self.figure.add_subplot(111)
        
        y_pos = np.arange(len(data['sbd']))
        bars = ax.barh(y_pos, data['scores'], color='gold', edgecolor='orange', alpha=0.8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"SBD: {sbd}" for sbd in data['sbd']])
        ax.invert_yaxis()  # Top student ở trên
        
        ax.set_title(f'Top {top_n} học sinh có tổng điểm cao nhất', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tổng điểm', fontsize=12)
        
        # Thêm giá trị điểm vào cuối mỗi cột
        for i, (bar, score) in enumerate(zip(bars, data['scores'])):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                   f'{score:.1f}', ha='left', va='center', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        self.figure.tight_layout()
    
    def draw_correlation_matrix(self):
        """Vẽ ma trận tương quan các môn học"""
        correlation_data = self.controller.model.get_correlation_matrix()
        
        ax = self.figure.add_subplot(111)
        
        if correlation_data is None:
            # Hiển thị thông báo lỗi thay vì return
            ax.text(0.5, 0.5, 'Không có dữ liệu để tính ma trận tương quan\nVui lòng kiểm tra dữ liệu đầu vào', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=12, color='red', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            ax.set_title('Ma trận tương quan - Không có dữ liệu', fontsize=16, fontweight='bold')
            return
        
        # Vẽ heatmap
        im = ax.imshow(correlation_data.values, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
        
        # Thiết lập labels
        subjects_dict = self.controller.get_subjects_list()
        subject_names = [subjects_dict[col] for col in correlation_data.columns]
        
        ax.set_xticks(range(len(subject_names)))
        ax.set_yticks(range(len(subject_names)))
        ax.set_xticklabels(subject_names, rotation=45, ha='right')
        ax.set_yticklabels(subject_names)
        
        # Thêm giá trị tương quan
        for i in range(len(subject_names)):
            for j in range(len(subject_names)):
                value = correlation_data.iloc[i, j]
                color = 'white' if abs(value) > 0.5 else 'black'
                ax.text(j, i, f'{value:.2f}', ha='center', va='center', color=color, fontweight='bold')
        
        ax.set_title('Ma trận tương quan điểm các môn thi', fontsize=16, fontweight='bold')
        
        # Thêm colorbar
        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label('Hệ số tương quan', rotation=270, labelpad=20)
        
        self.figure.tight_layout()
    
    def draw_combinations_chart(self):
        """Vẽ biểu đồ phân phối điểm theo tổ hợp môn"""
        combinations_data = self.controller.model.get_subject_combinations_data()
        if not combinations_data:
            return
        
        # Tạo subplot cho từng tổ hợp
        n_combos = len(combinations_data)
        cols = 3
        rows = (n_combos + cols - 1) // cols
        
        for i, (combo_name, data) in enumerate(combinations_data.items()):
            ax = self.figure.add_subplot(rows, cols, i + 1)
            
            scores = data['scores']
            ax.hist(scores, bins=15, alpha=0.7, color='lightgreen', edgecolor='darkgreen')
            ax.set_title(f'{combo_name}\n(TB: {data["mean"]:.1f}, SL: {data["count"]})', fontsize=10)
            ax.set_xlabel('Tổng điểm')
            ax.set_ylabel('Số lượng')
            ax.grid(True, alpha=0.3)
        
        self.figure.suptitle('Phân phối điểm theo tổ hợp môn thi', fontsize=16, fontweight='bold')
        self.figure.tight_layout()
    
    def draw_all_subjects_comparison(self):
        """Vẽ biểu đồ so sánh phân phối tất cả môn học"""
        all_subjects_data = self.controller.model.get_all_subjects_distribution()
        if not all_subjects_data:
            return
        
        # Tạo subplot cho từng môn
        n_subjects = len(all_subjects_data)
        cols = 3
        rows = (n_subjects + cols - 1) // cols
        
        for i, (subject_name, data) in enumerate(all_subjects_data.items()):
            ax = self.figure.add_subplot(rows, cols, i + 1)
            
            ax.hist(data, bins=10, alpha=0.7, color='lightblue', edgecolor='black')
            ax.set_title(f'{subject_name}', fontsize=12)
            ax.set_xlabel('Điểm')
            ax.set_ylabel('SL', fontsize=8)
            ax.grid(True, alpha=0.3)
            
        self.figure.suptitle('Phân phối điểm các môn thi THPT 2024', fontsize=16, fontweight='bold')
        self.figure.tight_layout()