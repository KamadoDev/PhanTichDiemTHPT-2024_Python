#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controller chính của ứng dụng

Module này chứa lớp AppController điều khiển luồng dữ liệu và
xử lý sự kiện giữa model và view.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Thêm dòng này để import module ttk

from models.data_model import DataModel
from views.main_view import MainView

class AppController:
    """Controller chính của ứng dụng"""
    
    def __init__(self, root):
        """Khởi tạo controller"""
        self.root = root
        self.model = DataModel()
        self.view = MainView(root, self)
        
        # Tải dữ liệu
        self.load_data()
    
    def load_data(self):
        """Tải dữ liệu từ file CSV"""
        success, message = self.model.load_data()
        if success:
            self.update_all_views()
            messagebox.showinfo("Thông báo", "Đã tải dữ liệu thành công!")
        else:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {message}")
    
    def update_all_views(self):
        """Cập nhật tất cả các view"""
        self.update_overview()
        self.update_data_view()
        
        # Cập nhật danh sách môn học cho các combobox
        subjects = self.model.get_subject_names()
        self.view.update_subject_lists(subjects)
    
    def get_subjects_list(self):
        """Lấy dictionary môn học (code: name)"""
        return self.model.subjects_dict
    
    def update_overview(self):
        """Cập nhật tab tổng quan"""
        stats = self.model.get_overview_stats()
        if stats:
            self.view.update_overview(stats)
    
    def search_sbd(self, sbd):
        """Tìm kiếm thí sinh theo SBD"""
        if not sbd:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập SBD!")
            return
        
        student = self.model.search_by_sbd(sbd)
        self.view.update_search_result(student, self.model.subjects_dict)
    
    def analyze_subject(self, subject_name):
        """Phân tích thống kê cho một môn học"""
        stats = self.model.analyze_subject(subject_name)
        if stats:
            self.view.update_analysis_result(subject_name, stats)
    
    def draw_chart(self, subject_name, chart_type):
        """Vẽ biểu đồ cho một môn học"""
        data = self.model.get_chart_data(subject_name)
        if data is not None:
            self.view.draw_chart(subject_name, chart_type, data)
    
    def draw_advanced_chart(self, chart_type):
        """Vẽ biểu đồ nâng cao"""
        if chart_type == "correlation_matrix":
            data = self.model.get_correlation_matrix()
            if data:
                self.view.chart_view.update_chart(None, chart_type, data)
        elif chart_type == "combinations":
            data = self.model.get_subject_combinations_data()
            if data:
                self.view.chart_view.update_chart(None, chart_type, data)
        elif chart_type == "all_subjects":
            data = self.model.get_all_subjects_distribution()
            if data:
                self.view.chart_view.update_chart(None, chart_type, data)
    
    def update_data_view(self):
        """Cập nhật tab dữ liệu"""
        # Thay đổi từ get_paginated_data() sang get_data() toàn bộ
        data = self.model.get_current_data()
        if data is not None:
            self.view.data_view.load_data(data)
        data, total_pages = self.model.get_paginated_data()
        if data is not None:
            self.view.update_data_table(data, self.model.current_page + 1, total_pages)
    
    def next_page(self):
        """Chuyển đến trang tiếp theo"""
        if self.model.next_page():
            self.update_data_view()
    
    def prev_page(self):
        """Chuyển đến trang trước"""
        if self.model.prev_page():
            self.update_data_view()
    
    def go_to_page(self, page):
        """Chuyển đến trang cụ thể"""
        try:
            page_num = int(page) - 1  # Chuyển từ số trang hiển thị sang index
            if self.model.go_to_page(page_num):
                self.update_data_view()
            else:
                messagebox.showwarning("Cảnh báo", "Số trang không hợp lệ!")
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập số trang hợp lệ!")
    
    def add_student(self, student_data):
        """Thêm thí sinh mới"""
        success, message = self.model.add_student(student_data)
        if success:
            messagebox.showinfo("Thông báo", "Đã thêm thí sinh mới thành công!")
            self.update_data_view()
            self.update_overview()
            return True
        else:
            messagebox.showerror("Lỗi", f"Không thể thêm thí sinh: {message}")
            return False
    
    def update_student(self, sbd, student_data):
        """Cập nhật thông tin thí sinh"""
        success, message = self.model.update_student(sbd, student_data)
        if success:
            messagebox.showinfo("Thông báo", "Đã cập nhật thông tin thí sinh thành công!")
            self.update_data_view()
            self.update_overview()
            return True
        else:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin: {message}")
            return False
    
    def delete_student(self, sbd):
        """Xóa thí sinh"""
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa thí sinh có SBD: {sbd}?"):
            success, message = self.model.delete_student(sbd)
            if success:
                messagebox.showinfo("Thông báo", "Đã xóa thí sinh thành công!")
                self.update_data_view()
                self.update_overview()
                return True
            else:
                messagebox.showerror("Lỗi", f"Không thể xóa thí sinh: {message}")
        return False
    
    def delete_multiple_students(self, sbd_list):
        """Xóa nhiều thí sinh"""
        if not sbd_list:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một thí sinh!")
            return False
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {len(sbd_list)} thí sinh đã chọn?"):
            success, message = self.model.delete_multiple_students(sbd_list)
            if success:
                messagebox.showinfo("Thông báo", message)
                self.update_data_view()
                self.update_overview()
                return True
            else:
                messagebox.showerror("Lỗi", f"Không thể xóa thí sinh: {message}")
        return False
    
    def search_data(self, search_text, search_column="Tất cả"):
        """Tìm kiếm dữ liệu theo từ khóa và cột"""
        if self.model.df is None:
            return None
        
        # Ánh xạ tên hiển thị của cột sang tên cột trong DataFrame
        column_map = {
            "SBD": "sbd",
            "Toán": "toan", 
            "Ngữ văn": "ngu_van", 
            "Ngoại ngữ": "ngoai_ngu",
            "Vật lí": "vat_li", 
            "Hóa học": "hoa_hoc", 
            "Sinh học": "sinh_hoc",
            "Lịch sử": "lich_su", 
            "Địa lí": "dia_li", 
            "GDCD": "gdcd",
            "Mã NN": "ma_ngoai_ngu"
        }
        
        # Nếu tìm kiếm tất cả các cột
        if search_column == "Tất cả":
            # Tạo mask cho từng cột và kết hợp chúng
            mask = False
            for display_name, col in column_map.items():
                if col in self.model.df.columns:
                    # Chỉ chuyển đổi cột hiện tại sang chuỗi, không phải toàn bộ DataFrame
                    col_mask = self.model.df[col].astype(str).str.contains(search_text, case=False, na=False)
                    mask = mask | col_mask
        else:
            # Tìm kiếm trong cột cụ thể
            df_column = column_map.get(search_column)
            if df_column and df_column in self.model.df.columns:
                mask = self.model.df[df_column].astype(str).str.contains(search_text, case=False, na=False)
            else:
                return None
        
        # Áp dụng mask để lọc DataFrame
        result = self.model.df[mask]
        
        # Giới hạn số lượng kết quả để tránh quá tải
        if len(result) > 1000:
            result = result.head(1000)
            
        # LưU KẾT QUẢ TÌM KIẾM - DÒNG QUAN TRỌNG NHẤT
        self.filtered_data = result
            
        return result
    
    def sort_data(self, column, ascending=True):
        """Sắp xếp dữ liệu theo cột"""
        if self.model.sort_data(column, ascending):
            return self.model.df
        return None
    
    def filter_data(self, column, value, condition):
        """Lọc dữ liệu theo điều kiện"""
        filtered_data = self.model.filter_data(column, value, condition)
        if filtered_data is not None:
            self.view.show_filtered_data(filtered_data)
        else:
            messagebox.showwarning("Cảnh báo", "Không thể lọc dữ liệu với điều kiện đã chọn!")
    
    def clear_filter(self):
        """Xóa bộ lọc dữ liệu"""
        self.filtered_data = None
        # Refresh data view với dữ liệu gốc
        if hasattr(self, 'view') and hasattr(self.view, 'data_view'):
            self.view.data_view.load_data(self.get_data())
    
    def get_filtered_data(self):
        """Lấy dữ liệu đã được lọc (kết quả tìm kiếm)
        
        Returns:
            DataFrame: Dữ liệu đã được lọc
        """
        # Nếu có dữ liệu đã lọc, trả về dữ liệu đó
        if hasattr(self, 'filtered_data') and self.filtered_data is not None:
            return self.filtered_data
        # Nếu không, trả về toàn bộ dữ liệu
        return self.model.get_current_data()
    
    def get_data(self):
        """Lấy dữ liệu hiện tại từ model
        
        Returns:
            DataFrame: Dữ liệu hiện tại
        """
        return self.model.get_current_data()
    
    # Các phương thức bổ sung cần thiết cho menu
    
    def open_file(self):
        """Mở file CSV cố định"""
        # Sử dụng đường dẫn file cố định đã được định nghĩa trong model
        # Không hiển thị hộp thoại chọn file nữa
        self.load_data()
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Chọn file CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            # Cập nhật đường dẫn file trong model và tải dữ liệu
            self.model.file_path = file_path
            self.load_data()
    
    def add_data(self):
        """Thêm dữ liệu mới"""
        # Mở cửa sổ dialog để nhập dữ liệu mới
        # Tạo cửa sổ dialog mới thay vì gọi phương thức không tồn tại
        self.create_student_dialog("Thêm thí sinh mới", None)
    
    def delete_data(self, sbd_list=None):
        """Xóa dữ liệu đã chọn"""
        # Nếu không có danh sách SBD được truyền vào, lấy từ data_view
        if sbd_list is None:
            # Kiểm tra xem data_view có phương thức get_selected_sbds không
            if hasattr(self.view.data_view, 'get_selected_sbds'):
                sbd_list = self.view.data_view.get_selected_sbds()
            else:
                messagebox.showwarning("Cảnh báo", "Không thể lấy danh sách SBD đã chọn!")
                return
        
        if sbd_list:
            self.delete_multiple_students(sbd_list)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một thí sinh để xóa!")
    
    def export_report(self):
        """Xuất báo cáo"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Lưu báo cáo",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Xuất dữ liệu ra file Excel
                success = self.model.export_to_excel(file_path)
                if success:
                    messagebox.showinfo("Thông báo", f"Đã xuất báo cáo thành công vào {file_path}")
                else:
                    messagebox.showerror("Lỗi", "Không thể xuất báo cáo!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xuất báo cáo: {str(e)}")
    
    def show_chart(self, chart_type):
        """Hiển thị biểu đồ theo loại"""
        # Chuyển đến tab biểu đồ
        self.view.tab_control.select(3)  # Index của tab biểu đồ
        
        # Cập nhật loại biểu đồ trong chart_view
        self.view.chart_view.set_chart_type(chart_type)
        
        # Nếu đã chọn môn học, vẽ biểu đồ luôn
        selected_subject = self.view.chart_view.get_selected_subject()
        if selected_subject:
            data = self.model.get_chart_data(selected_subject)
            if data is not None:
                self.view.draw_chart(selected_subject, chart_type, data)
    
    def show_help(self):
        """Hiển thị hướng dẫn sử dụng"""
        help_text = """
        HƯỚNG DẪN SỬ DỤNG PHẦM MỀM PHÂN TÍCH ĐIỂM THI THPT 2024
        
        1. Tab Quản lý dữ liệu: Xem, thêm, sửa, xóa dữ liệu thí sinh và tìm kiếm
        2. Tab Tổng quan: Hiển thị thống kê tổng quan về dữ liệu điểm thi
        3. Tab Phân tích: Phân tích thống kê chi tiết theo từng môn học
        4. Tab Biểu đồ: Vẽ các loại biểu đồ phân tích điểm thi
        
        Các chức năng chính:
        - Mở file CSV: Tải dữ liệu từ file CSV khác
        - Lưu dữ liệu: Lưu các thay đổi vào file CSV hiện tại
        - Thêm/Xóa dữ liệu: Quản lý thông tin thí sinh
        - Xuất báo cáo: Xuất dữ liệu ra file Excel
        - Biểu đồ: Vẽ các loại biểu đồ phân tích
        """
        
        # Hiển thị cửa sổ hướng dẫn
        help_window = tk.Toplevel(self.root)
        help_window.title("Hướng dẫn sử dụng")
        help_window.geometry("600x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # Chỉ đọc
        
        # Thêm nút đóng
        close_button = ttk.Button(help_window, text="Đóng", command=help_window.destroy)
        close_button.pack(pady=10)
    
    def show_about(self):
        """Hiển thị thông tin về phầm mềm"""
        about_text = """
        PHẦN MỀM PHÂN TÍCH ĐIỂM THI THPT 2024
        
        Phiên bản: 1.0
        
        Phần mềm được phát triển để phân tích và trực quan hóa dữ liệu điểm thi THPT Quốc gia 2024.
        
        Tính năng chính:
        - Thống kê tổng quan về điểm thi
        - Tìm kiếm thông tin thí sinh
        - Phân tích chi tiết theo môn học
        - Vẽ biểu đồ phân tích điểm thi
        - Quản lý dữ liệu thí sinh
        """
        
        messagebox.showinfo("Giới thiệu", about_text)

    def edit_data(self, sbd):
        """Sửa thông tin thí sinh"""
        # Lấy dữ liệu của thí sinh từ model
        student = self.model.search_by_sbd(sbd)
        if student is not None:
            # Mở cửa sổ dialog để sửa thông tin
            self.create_student_dialog("Sửa thông tin thí sinh", student)
        else:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy thí sinh với SBD đã chọn!")
    
    def show_confirm(self, title, message):
        """Hiển thị hộp thoại xác nhận"""
        return messagebox.askyesno(title, message)

    def create_student_dialog(self, title, student=None):
        """Tạo hộp thoại thêm/sửa thí sinh
        
        Args:
            title: Tiêu đề hộp thoại
            student: Dữ liệu thí sinh (None nếu thêm mới)
        """
        # Tạo cửa sổ dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x500")
        dialog.transient(self.root)  # Đặt cửa sổ dialog là con của cửa sổ chính
        dialog.grab_set()  # Ngăn tương tác với cửa sổ chính khi dialog đang mở
        
        # Frame chính
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        header_label = ttk.Label(main_frame, text="Thêm thí sinh mới" if student is None else "Sửa thông tin thí sinh", font=("Arial", 12, "bold"))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)
        
        # Các trường nhập liệu
        ttk.Label(main_frame, text="SBD:").grid(row=1, column=0, sticky=tk.W, pady=5)
        sbd_entry = ttk.Entry(main_frame, width=30)
        sbd_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Thêm các trường nhập liệu cho các môn học
        subjects = [
            ("Toán", "toan"), 
            ("Ngữ văn", "ngu_van"), 
            ("Ngoại ngữ", "ngoai_ngu"),
            ("Vật lí", "vat_li"), 
            ("Hóa học", "hoa_hoc"), 
            ("Sinh học", "sinh_hoc"),
            ("Lịch sử", "lich_su"), 
            ("Địa lí", "dia_li"), 
            ("GDCD", "gdcd")
        ]
        
        entries = {"sbd": sbd_entry}
        
        for i, (subject_name, subject_code) in enumerate(subjects):
            ttk.Label(main_frame, text=f"{subject_name}:").grid(row=i+2, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i+2, column=1, pady=5, padx=5, sticky=tk.W)
            entries[subject_code] = entry
        
        # Mã ngoại ngữ
        ttk.Label(main_frame, text="Mã ngoại ngữ:").grid(row=len(subjects)+2, column=0, sticky=tk.W, pady=5)
        ma_nn_combo = ttk.Combobox(main_frame, width=28, values=["N1", "N2", "N3", "N4", "N5", "N6", "N7"], state="readonly")
        ma_nn_combo.grid(row=len(subjects)+2, column=1, pady=5, padx=5, sticky=tk.W)
        entries["ma_ngoai_ngu"] = ma_nn_combo
        
        # Nếu là sửa, điền dữ liệu vào các trường
        if student is not None:
            sbd_entry.insert(0, student["sbd"])
            sbd_entry.config(state="readonly")  # Không cho phép sửa SBD
            
            for field_code in entries.keys():
                if field_code != "sbd" and field_code in student:
                    if field_code == "ma_ngoai_ngu":
                        entries[field_code].set(student[field_code])
                    else:
                        entries[field_code].insert(0, student[field_code])
        
        # Frame nút
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Hàm lưu dữ liệu
        def save_data():
            # Thu thập dữ liệu từ các trường nhập liệu
            student_data = {}
            for field, entry in entries.items():
                if field == "ma_ngoai_ngu":
                    value = entry.get()
                else:
                    value = entry.get().strip()
                
                # Kiểm tra SBD không được để trống
                if field == "sbd" and not value:
                    messagebox.showwarning("Cảnh báo", "SBD không được để trống!")
                    return
                
                # Chuyển điểm về kiểu số nếu có giá trị
                if field not in ["sbd", "ma_ngoai_ngu"] and value:
                    try:
                        value = float(value)
                        # Kiểm tra điểm hợp lệ (0-10)
                        if value < 0 or value > 10:
                            messagebox.showwarning("Cảnh báo", f"Điểm {field} phải từ 0 đến 10!")
                            return
                    except ValueError:
                        messagebox.showwarning("Cảnh báo", f"Điểm {field} phải là số!")
                        return
                
                student_data[field] = value
            
            # Lưu dữ liệu
            if student is None:
                # Thêm mới
                success = self.add_student(student_data)
            else:
                # Cập nhật
                success = self.update_student(student["sbd"], student_data)
            
            if success:
                dialog.destroy()
        
        # Nút Lưu và Hủy
        ttk.Button(button_frame, text="Lưu", command=save_data).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Hủy", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Đặt focus vào trường đầu tiên
        if student is None:
            sbd_entry.focus()
        else:
            entries["toan"].focus()
    def show_message(self, title, message, message_type="info"):
        """Hiển thị thông báo"""
        self.view.show_message(title, message, message_type)

def draw_advanced_chart(self, chart_type):
    """Vẽ biểu đồ nâng cao"""
    if chart_type == "correlation_matrix":
        data = self.model.get_correlation_matrix()
        if data:
            self.view.chart_view.update_chart(None, chart_type, data)
    elif chart_type == "combinations":
        data = self.model.get_subject_combinations_data()
        if data:
            self.view.chart_view.update_chart(None, chart_type, data)
    elif chart_type == "all_subjects":
        data = self.model.get_all_subjects_distribution()
        if data:
            self.view.chart_view.update_chart(None, chart_type, data)
    
    def get_subject_distribution_data(self, subject_code):
        """Lấy dữ liệu phân phối điểm của một môn học"""
        return self.model.get_subject_distribution_data(subject_code)
    
    def get_combination_distribution_data(self):
        """Lấy dữ liệu phân phối tổ hợp môn"""
        return self.model.get_combination_distribution_data()
    
    def get_average_scores_data(self):
        """Lấy dữ liệu điểm trung bình các môn"""
        return self.model.get_average_scores_data()
    
    def get_top_students_data(self, top_n=10):
        """Lấy dữ liệu top học sinh"""
        return self.model.get_top_students_data(top_n)