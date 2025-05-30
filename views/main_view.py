import tkinter as tk
from tkinter import ttk, messagebox

# Import các view con
from views.overview_view import OverviewView
# Xóa dòng import SearchView vì không còn sử dụng
from views.analysis_view import AnalysisView
from views.chart_view import ChartView
from views.data_view import DataView

class MainView:
    """Lớp quản lý giao diện chính của ứng dụng"""
    
    def __init__(self, root, controller):
        """Khởi tạo giao diện chính
        
        Args:
            root: Cửa sổ gốc Tkinter
            controller: Controller điều khiển ứng dụng
        """
        self.root = root
        self.controller = controller
        
        # Thiết lập cửa sổ chính
        self.root.title("Phân tích điểm thi THPT 2024")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Tạo giao diện
        self.create_widgets()
        
        # Khởi tạo các view con
        self.initialize_views()
    
    def create_widgets(self):
        """Tạo các widget cho giao diện chính"""
        # Frame chính
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (Tab Control)
        self.tab_control = ttk.Notebook(main_frame)
        
        # Tab 1: Quản lý dữ liệu (đưa lên đầu tiên)
        self.tab_data = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_data, text="Quản lý dữ liệu")
        
        # Tab 2: Tổng quan
        self.tab_overview = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_overview, text="Tổng quan")
        
        # Tab 3: Phân tích
        self.tab_analysis = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_analysis, text="Phân tích")
        
        # Tab 4: Biểu đồ
        self.tab_charts = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_charts, text="Biểu đồ")
        
        # Bỏ tab tìm kiếm vì đã gộp vào quản lý dữ liệu
        
        self.tab_control.pack(expand=1, fill=tk.BOTH)
    
    def initialize_views(self):
        """Khởi tạo các view con"""
        # Khởi tạo view cho từng tab
        self.data_view = DataView(self.tab_data, self.controller)
        self.overview_view = OverviewView(self.tab_overview, self.controller)
        self.analysis_view = AnalysisView(self.tab_analysis, self.controller)
        self.chart_view = ChartView(self.tab_charts, self.controller)
        # Bỏ khởi tạo search_view vì đã gộp vào data_view
    
    def create_menu(self):
        """Tạo menu cho ứng dụng"""
        menubar = tk.Menu(self.root)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Mở file CSV", command=self.controller.open_file)
        file_menu.add_command(label="Lưu dữ liệu", command=self.controller.save_data)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Menu Dữ liệu
        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label="Thêm dữ liệu mới", command=self.controller.add_data)
        data_menu.add_command(label="Xóa dữ liệu đã chọn", command=self.controller.delete_data)
        data_menu.add_command(label="Xuất báo cáo", command=self.controller.export_report)
        menubar.add_cascade(label="Dữ liệu", menu=data_menu)
        
        # Menu Biểu đồ
        chart_menu = tk.Menu(menubar, tearoff=0)
        # Đã loại bỏ: chart_menu.add_command(label="Biểu đồ phân phối điểm", command=lambda: self.controller.show_chart("distribution"))
        chart_menu.add_command(label="Biểu đồ so sánh", command=lambda: self.controller.show_chart("comparison"))
        chart_menu.add_command(label="Biểu đồ xu hướng", command=lambda: self.controller.show_chart("trend"))
        menubar.add_cascade(label="Biểu đồ", menu=chart_menu)
        
        # Menu Trợ giúp
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Hướng dẫn sử dụng", command=self.controller.show_help)
        help_menu.add_command(label="Giới thiệu", command=self.controller.show_about)
        menubar.add_cascade(label="Trợ giúp", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def show_message(self, title, message, message_type="info"):
        """Hiển thị thông báo
        
        Args:
            title: Tiêu đề thông báo
            message: Nội dung thông báo
            message_type: Loại thông báo (info, warning, error)
        """
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)
    
    def get_tab_frames(self):
        """Trả về các frame của các tab
        
        Returns:
            dict: Dictionary chứa các frame của các tab
        """
        return {
            "overview": self.tab_overview,
            "search": self.tab_search,
            "analysis": self.tab_analysis,
            "charts": self.tab_charts,
            "data": self.tab_data
        }
    
    # Các phương thức chuyển tiếp (forwarding methods) để gọi các view con
    
    def update_overview(self, stats):
        """Cập nhật tab tổng quan"""
        self.overview_view.update(stats)
    
    # Thêm phương thức này vào lớp MainView
    def update_search_result(self, student, subjects_dict):
        """Cập nhật kết quả tìm kiếm
        
        Args:
            student: Series chứa thông tin thí sinh
            subjects_dict: Dictionary ánh xạ mã môn học với tên môn học
        """
        # Chuyển hướng đến data_view
        self.data_view.update_result(student, subjects_dict)
    
    def update_analysis_result(self, subject_name, stats):
        """Cập nhật kết quả phân tích"""
        self.analysis_view.update_result(subject_name, stats)
    
    def draw_chart(self, subject_name, chart_type, data):
        """Vẽ biểu đồ"""
        self.chart_view.update_chart(subject_name, chart_type, data)
    
    def update_data_table(self, data, current_page, total_pages):
        """Cập nhật bảng dữ liệu"""
        self.data_view.load_data(data)
    
    def update_subject_lists(self, subjects):
        """Cập nhật danh sách môn học cho các combobox"""
        self.analysis_view.update_subject_list(subjects)
        self.chart_view.update_subject_list(subjects)