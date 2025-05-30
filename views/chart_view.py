import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.font_manager as fm
import warnings

# Tắt cảnh báo font
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', message='.*font.*')

# Cấu hình font hỗ trợ tiếng Việt tốt hơn
try:
    # Thử sử dụng font Arial Unicode MS hoặc Segoe UI (Windows)
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    if 'Arial Unicode MS' in available_fonts:
        plt.rcParams['font.family'] = ['Arial Unicode MS']
    elif 'Segoe UI' in available_fonts:
        plt.rcParams['font.family'] = ['Segoe UI']
    elif 'Arial' in available_fonts:
        plt.rcParams['font.family'] = ['Arial']
    else:
        plt.rcParams['font.family'] = ['DejaVu Sans']
except:
    plt.rcParams['font.family'] = ['DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

class ChartView:
    """Lớp quản lý giao diện tab biểu đồ"""
    
    def __init__(self, parent, controller):
        """Khởi tạo giao diện tab biểu đồ"""
        self.parent = parent
        self.controller = controller
        self.canvas = None
        self.figure = None
        
        # Thêm color palette
        self.show_values_var = tk.BooleanVar()
        self.color_palette = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', 
                             '#1ABC9C', '#34495E', '#E67E22', '#95A5A6', '#F1C40F']
        
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
            "Biểu đồ cột ngang - Top học sinh điểm cao",
            "Histogram - Phân phối điểm theo môn học",
            "Biểu đồ tròn - Tỷ lệ học sinh theo tổ hợp môn"
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
        ttk.Button(control_frame, text="Tạo biểu đồ", command=self.on_draw_button_click).grid(row=0, column=2, padx=5, pady=5)
        
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
        
        # Ẩn tất cả các frame tùy chọn
        self.subject_frame.grid_remove()
        self.top_frame.grid_remove()
        
        # Hiển thị frame tùy chọn phù hợp
        if "Histogram" in chart_type:
            self.subject_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            # Ẩn môn thứ 2 cho histogram
            for widget in self.subject_frame.grid_slaves():
                if widget.grid_info()['column'] >= 2:
                    widget.grid_remove()
        elif "Scatter plot" in chart_type:
            self.subject_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            # Hiển thị cả 2 môn cho scatter plot
            for widget in self.subject_frame.grid_slaves():
                if widget.grid_info()['column'] >= 2:
                    widget.grid()
                    if hasattr(widget, 'current'):
                        break
            # Tìm và hiển thị label "Môn thứ 2:"
            for widget in self.subject_frame.winfo_children():
                if isinstance(widget, ttk.Label) and widget.cget('text') == "Môn thứ 2:":
                    widget.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
                    break
        elif "Top học sinh" in chart_type:
            self.top_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    
    def on_color_theme_change(self, event=None):
        """Thay đổi chủ đề màu sắc"""
        theme = self.color_theme_combo.get()
        if theme == 'Pastel':
            self.color_palette = ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFD1BA']
        elif theme == 'Đậm':
            self.color_palette = ['#FF4444', '#44FF44', '#4444FF', '#FFFF44', '#FF44FF']
        elif theme == 'Monochrome':
            self.color_palette = ['#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7']
        else:  # Mặc định
            self.color_palette = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        sns.set_palette(self.color_palette)
        
    def on_draw_button_click(self):
        """Xử lý khi nhấn nút Tạo biểu đồ"""
        chart_type = self.chart_type_combo.get()
        if chart_type:
            self.draw_chart()  # Remove the chart_type argument
    
    def draw_chart(self):
        """Vẽ biểu đồ theo loại đã chọn"""
        try:
            chart_type = self.chart_type_combo.get()
            if not chart_type:
                self.show_error_message("⚠️ Chưa chọn loại biểu đồ", 
                                       "Vui lòng chọn loại biểu đồ để hiển thị.")
                return
            
            # Xóa biểu đồ cũ
            if self.figure:
                self.figure.clear()
            
            # Kiểm tra dữ liệu trước khi vẽ
            if self.controller.model.df is None or len(self.controller.model.df) == 0:
                self.show_error_message("⚠️ Không có dữ liệu", 
                                       "Vui lòng tải dữ liệu trước khi tạo biểu đồ.")
                return
            
            # Vẽ biểu đồ theo loại
            if "Điểm trung bình" in chart_type:
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
            elif "Phân phối điểm" in chart_type:
                self.draw_all_subjects_comparison()
            else:
                self.show_error_message("❌ Loại biểu đồ không hỗ trợ", 
                                       f"Loại biểu đồ '{chart_type}' chưa được triển khai.")
                return
            
            # Cập nhật canvas
            if self.canvas:
                self.canvas.draw()
                
        except Exception as e:
            error_msg = f"Lỗi khi vẽ biểu đồ: {str(e)}"
            print(f"Chart Error: {error_msg}")  # Debug log
            self.show_error_on_chart(error_msg)
            
    def validate_subject_selection(self):
        """Kiểm tra việc chọn môn học"""
        subject_name = self.subject_combo.get()
        if not subject_name:
            self.show_error_message("⚠️ Chưa chọn môn học", 
                                   "Vui lòng chọn môn học để tạo biểu đồ.")
            return False
        return True
    
    def show_error_message(self, title, message):
        """Hiển thị thông báo lỗi"""
        messagebox.showwarning(title, message)
        
    def show_error_on_chart(self, error_message):
        """Hiển thị lỗi trên biểu đồ với giao diện đẹp"""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.6, '❌ Có lỗi xảy ra', ha='center', va='center', 
               transform=ax.transAxes, fontsize=16, color='#E74C3C', fontweight='bold')
        ax.text(0.5, 0.4, f'Chi tiết: {error_message}', ha='center', va='center', 
               transform=ax.transAxes, fontsize=12, color='#7F8C8D')
        ax.text(0.5, 0.2, '💡 Vui lòng kiểm tra dữ liệu và thử lại', ha='center', va='center', 
               transform=ax.transAxes, fontsize=10, color='#3498DB')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
    
    def draw_histogram_chart(self):
        """Vẽ histogram phân phối điểm theo môn học"""
        try:
            subject_name = self.subject_combo.get()
            if not subject_name:
                self.show_error_message("❌ Lỗi", "Vui lòng chọn môn học!")
                return
            
            # Tìm mã môn học
            subjects = self.controller.get_subjects_list()
            subject_code = None
            for code, name in subjects.items():
                if name == subject_name:
                    subject_code = code
                    break
            
            if not subject_code:
                self.show_error_message("❌ Lỗi môn học", 
                                       f"Không tìm thấy mã môn cho '{subject_name}'.")
                return
            
            # Lấy dữ liệu trực tiếp từ model nếu controller không có method
            try:
                data = self.controller.get_subject_distribution_data(subject_code)
            except AttributeError:
                data = self.controller.model.get_subject_distribution_data(subject_code)
            
            if data is None or len(data) == 0:
                self.show_no_data_message(subject_name)
                return
            
            # Xóa biểu đồ cũ
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Kiểm tra dữ liệu hợp lệ
            valid_data = data[~np.isnan(data)]  # Loại bỏ NaN
            if len(valid_data) == 0:
                self.show_no_data_message(subject_name)
                return
                
            n, bins, patches = ax.hist(valid_data, bins=20, alpha=0.7, 
                                     color='#3498DB', edgecolor='white', linewidth=1.2)
            
            # Thêm gradient color cho các cột
            for i, patch in enumerate(patches):
                patch.set_facecolor(plt.cm.viridis(i / len(patches)))
            
            # Thêm thống kê
            mean_val = np.mean(valid_data)
            std_val = np.std(valid_data)
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                      label=f'Trung bình: {mean_val:.2f}')
            
            # Hiển thị giá trị trên các cột nếu được chọn
            if hasattr(self, 'show_values_var') and self.show_values_var.get():
                for i, (count, bin_edge) in enumerate(zip(n, bins[:-1])):
                    if count > 0:
                        ax.text(bin_edge + (bins[1] - bins[0])/2, count + max(n)*0.01, 
                               f'{int(count)}', ha='center', va='bottom', fontsize=8)
            
            ax.set_title(f'📊 Phân phối điểm {subject_name}\n(Trung bình: {mean_val:.2f}, Độ lệch chuẩn: {std_val:.2f})', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Điểm số', fontsize=12)
            ax.set_ylabel('Số lượng học sinh', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.show_error_on_chart(f"Lỗi vẽ histogram: {str(e)}")
    
    def draw_pie_chart(self):
        """Vẽ biểu đồ tròn tỷ lệ học sinh theo tổ hợp môn"""
        try:
            # Xóa biểu đồ cũ
            self.figure.clear()
            
            # Lấy dữ liệu từ controller hoặc model
            try:
                data = self.controller.get_combination_distribution_data()
            except AttributeError:
                data = self.controller.model.get_combination_distribution_data()
            
            if not data or len(data) == 0:
                self.show_error_on_chart("Không có dữ liệu tổ hợp môn để vẽ biểu đồ")
                return
            
            ax = self.figure.add_subplot(111)
            
            # Sắp xếp dữ liệu theo số lượng giảm dần
            sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
            
            labels = list(sorted_data.keys())
            sizes = list(sorted_data.values())
            
            # Chỉ hiển thị top 10 tổ hợp phổ biến nhất
            if len(labels) > 10:
                labels = labels[:10]
                sizes = sizes[:10]
                other_count = sum(list(sorted_data.values())[10:])
                if other_count > 0:
                    labels.append('Khác')
                    sizes.append(other_count)
            
            # Tạo màu sắc đẹp
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            # Tạo explode cho các phần lớn
            explode = [0.1 if size == max(sizes) else 0.05 for size in sizes]
            
            # Vẽ biểu đồ tròn
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(sizes))} HS)',
                colors=colors, 
                startangle=90,
                explode=explode,
                shadow=True,
                textprops={'fontsize': 9}
            )
            
            # Tùy chỉnh text trong biểu đồ
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
            
            # Tùy chỉnh labels
            for text in texts:
                text.set_fontsize(8)
                text.set_fontweight('bold')
            
            # Tiêu đề
            ax.set_title('🥧 Tỷ lệ học sinh theo tổ hợp môn\n(Top 3 môn điểm cao nhất)', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Thêm legend với thông tin chi tiết
            legend_labels = [f'{label}: {size} học sinh ({size/sum(sizes)*100:.1f}%)' 
                           for label, size in zip(labels, sizes)]
            
            ax.legend(wedges, legend_labels,
                     title="Chi tiết tổ hợp môn", 
                     loc="center left", 
                     bbox_to_anchor=(1, 0, 0.5, 1),
                     fontsize=9)
            
            # Thêm thông tin tổng quan
            total_students = sum(sizes)
            ax.text(0.5, -1.3, f'Tổng số học sinh: {total_students}', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=12, fontweight='bold', 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.show_error_on_chart(f"Lỗi vẽ biểu đồ tròn: {str(e)}")
            print(f"Chi tiết lỗi: {e}")
    
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
    
    def draw_average_scores_chart(self):
        """Vẽ biểu đồ cột điểm trung bình các môn học"""
        data = self.controller.model.get_average_scores_data()
        if not data:
            self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
            return
        
        ax = self.figure.add_subplot(111)
        
        subjects = list(data.keys())
        scores = list(data.values())
        
        bars = ax.bar(subjects, scores, color=self.color_palette[:len(subjects)], 
                     alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_title('Điểm trung bình các môn học', fontsize=16, fontweight='bold')
        ax.set_xlabel('Môn học', fontsize=12)
        ax.set_ylabel('Điểm trung bình', fontsize=12)
        ax.set_ylim(0, 10)
        
        # Thêm giá trị lên đầu cột
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'{score:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        self.figure.tight_layout()
    
    def draw_pie_chart(self):
        """Vẽ biểu đồ tròn tỷ lệ học sinh theo tổ hợp môn"""
        try:
            # Lấy dữ liệu trực tiếp từ model nếu controller không có method
            try:
                data = self.controller.get_combination_distribution_data()
            except AttributeError:
                data = self.controller.model.get_combination_distribution_data()
            
            if not data:
                self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
                return
            
            # Xóa biểu đồ cũ
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            labels = list(data.keys())
            sizes = list(data.values())
            
            # Tạo màu sắc
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                             colors=colors, startangle=90, 
                                             explode=[0.05] * len(labels))
            
            # Tùy chỉnh text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Tỷ lệ học sinh theo tổ hợp môn', fontsize=16, fontweight='bold')
            
            # Thêm legend
            ax.legend(wedges, [f'{label}: {size} học sinh' for label, size in zip(labels, sizes)],
                 title="Tổ hợp môn", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.show_error_on_chart(f"Lỗi vẽ biểu đồ tròn: {str(e)}")
            print(f"Chi tiết lỗi: {e}")
    
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
    
    def draw_average_scores_chart(self):
        """Vẽ biểu đồ cột điểm trung bình các môn học"""
        data = self.controller.model.get_average_scores_data()
        if not data:
            self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
            return
        
        ax = self.figure.add_subplot(111)
        
        subjects = list(data.keys())
        scores = list(data.values())
        
        bars = ax.bar(subjects, scores, color=self.color_palette[:len(subjects)], 
                     alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_title('Điểm trung bình các môn học', fontsize=16, fontweight='bold')
        ax.set_xlabel('Môn học', fontsize=12)
        ax.set_ylabel('Điểm trung bình', fontsize=12)
        ax.set_ylim(0, 10)
        
        # Thêm giá trị lên đầu cột
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'{score:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        self.figure.tight_layout()
    
    def draw_pie_chart(self):
        """Vẽ biểu đồ tròn tỷ lệ học sinh theo tổ hợp môn"""
        try:
            # Lấy dữ liệu trực tiếp từ model nếu controller không có method
            try:
                data = self.controller.get_combination_distribution_data()
            except AttributeError:
                data = self.controller.model.get_subject_combinations_data()
            
            if not data:
                self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
                return
            
            # Xóa biểu đồ cũ
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            labels = list(data.keys())
            sizes = list(data.values())
            
            # Tạo màu sắc
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                             colors=colors, startangle=90, 
                                             explode=[0.05] * len(labels))
            
            # Tùy chỉnh text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Tỷ lệ học sinh theo tổ hợp môn', fontsize=16, fontweight='bold')
            
            # Thêm legend
            ax.legend(wedges, [f'{label}: {size} học sinh' for label, size in zip(labels, sizes)],
                 title="Tổ hợp môn", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.show_error_on_chart(f"Lỗi vẽ biểu đồ tròn: {str(e)}")
            
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
    
    def draw_average_scores_chart(self):
        """Vẽ biểu đồ cột điểm trung bình các môn học"""
        data = self.controller.model.get_average_scores_data()
        if not data:
            self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
            return
        
        ax = self.figure.add_subplot(111)
        
        subjects = list(data.keys())
        scores = list(data.values())
        
        bars = ax.bar(subjects, scores, color=self.color_palette[:len(subjects)], 
                     alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_title('Điểm trung bình các môn học', fontsize=16, fontweight='bold')
        ax.set_xlabel('Môn học', fontsize=12)
        ax.set_ylabel('Điểm trung bình', fontsize=12)
        ax.set_ylim(0, 10)
        
        # Thêm giá trị lên đầu cột
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'{score:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        self.figure.tight_layout()
    
    def draw_pie_chart(self):
        """Vẽ biểu đồ tròn tỷ lệ học sinh theo tổ hợp môn"""
        try:
            # Lấy dữ liệu trực tiếp từ model nếu controller không có method
            try:
                data = self.controller.get_combination_distribution_data()
            except AttributeError:
                data = self.controller.model.get_subject_combinations_data()
            
            if not data:
                self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
                return
            
            # Xóa biểu đồ cũ
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            labels = list(data.keys())
            sizes = list(data.values())
            
            # Tạo màu sắc
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                             colors=colors, startangle=90, 
                                             explode=[0.05] * len(labels))
            
            # Tùy chỉnh text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Tỷ lệ học sinh theo tổ hợp môn', fontsize=16, fontweight='bold')
            
            # Thêm legend
            ax.legend(wedges, [f'{label}: {size} học sinh' for label, size in zip(labels, sizes)],
                 title="Tổ hợp môn", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.show_error_on_chart(f"Lỗi vẽ biểu đồ tròn: {str(e)}")
            
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
    
    def draw_average_scores_chart(self):
        """Vẽ biểu đồ cột điểm trung bình các môn học"""
        data = self.controller.model.get_average_scores_data()
        if not data:
            self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
            return
        
        ax = self.figure.add_subplot(111)
        
        subjects = list(data.keys())
        scores = list(data.values())
        
        bars = ax.bar(subjects, scores, color=self.color_palette[:len(subjects)], 
                     alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_title('Điểm trung bình các môn học', fontsize=16, fontweight='bold')
        ax.set_xlabel('Môn học', fontsize=12)
        ax.set_ylabel('Điểm trung bình', fontsize=12)
        ax.set_ylim(0, 10)
        
        # Thêm giá trị lên đầu cột
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'{score:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        self.figure.tight_layout()
    
    def draw_pie_chart(self):
        """Vẽ biểu đồ tròn tỷ lệ học sinh theo tổ hợp môn"""
        try:
            # Cấu hình font phù hợp với Windows
            import matplotlib.font_manager as fm
            
            # Tìm font phù hợp có sẵn trên hệ thống
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            # Ưu tiên các font hỗ trợ tiếng Việt trên Windows
            preferred_fonts = ['Segoe UI', 'Tahoma', 'Microsoft Sans Serif', 'Arial', 'DejaVu Sans']
            selected_font = 'DejaVu Sans'  # Default fallback
            
            for font in preferred_fonts:
                if font in available_fonts:
                    selected_font = font
                    break
            
            plt.rcParams['font.family'] = selected_font
            plt.rcParams['axes.unicode_minus'] = False
            
            # Lấy dữ liệu trực tiếp từ model nếu controller không có method
            try:
                data = self.controller.get_combination_distribution_data()
            except AttributeError:
                data = self.controller.model.get_combination_distribution_data()
            
            if not data:
                self.show_error_on_chart("Không có dữ liệu để vẽ biểu đồ")
                return
            
            # Xóa biểu đồ cũ
            self.figure.clear()
            
            # Tạo subplot với khoảng cách lớn hơn cho legend
            ax = self.figure.add_subplot(111)
            
            labels = list(data.keys())
            sizes = list(data.values())
            
            # Rút ngắn label nếu quá dài
            short_labels = []
            for label in labels:
                if len(label) > 12:
                    short_labels.append(label[:9] + "...")
                else:
                    short_labels.append(label)
            
            # Tạo màu sắc
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            # Chỉ hiển thị % cho các phần > 3%
            total = sum(sizes)
            autopct_func = lambda pct: f'{pct:.1f}%' if pct > 3 else ''
            
            wedges, texts, autotexts = ax.pie(sizes, labels=short_labels, autopct=autopct_func,
                                             colors=colors, startangle=90, 
                                             explode=[0.02] * len(labels),
                                             textprops={'fontsize': 8})
            
            # Tùy chỉnh text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(7)
            
            # Tùy chỉnh label text - làm nhỏ hơn
            for text in texts:
                text.set_fontsize(7)
            
            ax.set_title('Tỷ lệ học sinh theo tổ hợp môn (Top 10)', fontsize=13, fontweight='bold', pad=15)
            
            # Tạo legend với thông tin chi tiết bên ngoài biểu đồ - tách xa hơn
            legend_labels = []
            for label, size in zip(labels, sizes):
                percentage = (size / total) * 100
                legend_labels.append(f'{label}: {size} HS ({percentage:.1f}%)')
            
            # Đặt legend bên phải với khoảng cách lớn hơn
            legend = ax.legend(wedges, legend_labels,
                              title="Chi tiết tổ hợp môn", 
                              loc="center left", 
                              bbox_to_anchor=(1.2, 0.5),
                              fontsize=7,
                              title_fontsize=8)
            
            # Điều chỉnh layout để tách biệt biểu đồ và legend
            self.figure.subplots_adjust(left=0.05, right=0.55, top=0.9, bottom=0.1)
            
            self.canvas.draw()
            
        except Exception as e:
            self.show_error_on_chart(f"Lỗi vẽ biểu đồ tròn: {str(e)}")
            print(f"Chi tiết lỗi: {e}")
    
    def draw_boxplot_chart(self):
        """Vẽ box plot so sánh điểm các tổ hợp"""
        data = self.controller.model.get_combination_comparison_data()
        if not data:
            return