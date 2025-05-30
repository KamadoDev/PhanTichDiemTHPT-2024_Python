import tkinter as tk
from tkinter import ttk
import pandas as pd

class DataView:
    """Lớp quản lý giao diện tab quản lý dữ liệu"""
    
    def __init__(self, parent, controller):
        """Khởi tạo giao diện tab quản lý dữ liệu
        
        Args:
            parent: Frame cha
            controller: Controller điều khiển ứng dụng
        """
        self.parent = parent
        self.controller = controller
        self.current_page = 1
        self.rows_per_page = 20
        self.selected_items = []
        self.current_df = None
        self.filtered_df = None  # THÊM MỚI: DataFrame sau khi lọc
        self.total_rows = 0
        self.total_pages = 1
        
        # Tạo giao diện
        self.create_widgets()
        
        # Tải dữ liệu ban đầu
        self.load_data()

    def create_widgets(self):
        """Tạo các widget cho giao diện quản lý dữ liệu"""
        # Frame chính
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame công cụ
        tools_frame = ttk.Frame(main_frame)
        tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Nút thêm, sửa, xóa
        ttk.Button(tools_frame, text="Thêm", command=self.add_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tools_frame, text="Sửa", command=self.edit_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tools_frame, text="Xóa", command=self.delete_data).pack(side=tk.LEFT, padx=(0, 10))
        
        # THÊM MỚI: Frame bộ lọc dữ liệu
        filter_frame = ttk.LabelFrame(main_frame, text="Bộ lọc dữ liệu")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Dòng 1: Lọc theo môn học và khoảng điểm
        filter_row1 = ttk.Frame(filter_frame)
        filter_row1.pack(fill=tk.X, padx=5, pady=5)
        
        # Lọc theo môn học
        ttk.Label(filter_row1, text="Môn học:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_subject_combo = ttk.Combobox(filter_row1, width=12, state="readonly")
        self.filter_subject_combo['values'] = ('Tất cả', 'Toán', 'Ngữ văn', 'Ngoại ngữ', 'Vật lí', 'Hóa học', 'Sinh học', 'Lịch sử', 'Địa lí', 'GDCD')
        self.filter_subject_combo.set('Tất cả')
        self.filter_subject_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Khoảng điểm
        ttk.Label(filter_row1, text="Điểm từ:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_min_score = ttk.Entry(filter_row1, width=8)
        self.filter_min_score.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(filter_row1, text="đến:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_max_score = ttk.Entry(filter_row1, width=8)
        self.filter_max_score.pack(side=tk.LEFT, padx=(0, 15))
        
        # Dòng 2: Lọc theo tổ hợp môn và điểm trung bình
        filter_row2 = ttk.Frame(filter_frame)
        filter_row2.pack(fill=tk.X, padx=5, pady=5)
        
        # Lọc theo tổ hợp môn
        ttk.Label(filter_row2, text="Tổ hợp:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_combination_combo = ttk.Combobox(filter_row2, width=15, state="readonly")
        self.filter_combination_combo['values'] = ('Tất cả', 'A00 (Toán-Lí-Hóa)', 'A01 (Toán-Lí-Anh)', 'B00 (Toán-Hóa-Sinh)', 'C00 (Văn-Sử-Địa)', 'D01 (Văn-Toán-Anh)')
        self.filter_combination_combo.set('Tất cả')
        self.filter_combination_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Điểm trung bình
        ttk.Label(filter_row2, text="ĐTB từ:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_min_avg = ttk.Entry(filter_row2, width=8)
        self.filter_min_avg.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(filter_row2, text="đến:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_max_avg = ttk.Entry(filter_row2, width=8)
        self.filter_max_avg.pack(side=tk.LEFT, padx=(0, 15))
        
        # Nút áp dụng và xóa bộ lọc
        ttk.Button(filter_row2, text="Áp dụng lọc", command=self.apply_filter).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(filter_row2, text="Xóa lọc", command=self.clear_filter).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Frame tìm kiếm
        search_frame = ttk.LabelFrame(main_frame, text="Tìm kiếm")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_inner_frame = ttk.Frame(search_frame)
        search_inner_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Combobox chọn cột tìm kiếm
        ttk.Label(search_inner_frame, text="Cột:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_column_combo = ttk.Combobox(search_inner_frame, width=12, state="readonly")
        self.search_column_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry tìm kiếm
        ttk.Label(search_inner_frame, text="Từ khóa:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_inner_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_data())
        
        # Nút tìm kiếm
        ttk.Button(search_inner_frame, text="Tìm", command=self.search_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame sắp xếp
        sort_frame = ttk.LabelFrame(main_frame, text="Sắp xếp")
        sort_frame.pack(fill=tk.X, pady=(0, 10))
        
        sort_inner_frame = ttk.Frame(sort_frame)
        sort_inner_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Combobox chọn cột sắp xếp
        ttk.Label(sort_inner_frame, text="Cột:").pack(side=tk.LEFT, padx=(0, 5))
        self.sort_combo = ttk.Combobox(sort_inner_frame, width=15, state="readonly")
        self.sort_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Checkbox sắp xếp tăng dần
        self.sort_asc = tk.BooleanVar(value=True)
        ttk.Checkbutton(sort_inner_frame, text="Tăng dần", variable=self.sort_asc).pack(side=tk.LEFT, padx=(0, 10))
        
        # Nút sắp xếp
        ttk.Button(sort_inner_frame, text="Sắp xếp", command=self.sort_data).pack(side=tk.LEFT)
        
        # Frame chọn số dòng hiển thị
        display_frame = ttk.LabelFrame(sort_inner_frame, text="Hiển thị")
        display_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(display_frame, text="Số dòng:").pack(side=tk.LEFT, padx=(5, 2))
        self.rows_per_page_combo = ttk.Combobox(display_frame, width=8, state="readonly")
        self.rows_per_page_combo['values'] = ('10', '20', '50', '100', '200')
        self.rows_per_page_combo.set('20')  # Giá trị mặc định
        self.rows_per_page_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.rows_per_page_combo.bind('<<ComboboxSelected>>', self.on_rows_per_page_changed)
        
        # Frame bảng dữ liệu
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview hiển thị dữ liệu
        columns = ("sbd", "toan", "ngu_van", "ngoai_ngu", "vat_li", "hoa_hoc", "sinh_hoc", "lich_su", "dia_li", "gdcd")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Định nghĩa tiêu đề cột
        headers = {
            "sbd": "Số báo danh",
            "toan": "Toán",
            "ngu_van": "Ngữ văn",
            "ngoai_ngu": "Ngoại ngữ",
            "vat_li": "Vật lí",
            "hoa_hoc": "Hóa học",
            "sinh_hoc": "Sinh học",
            "lich_su": "Lịch sử",
            "dia_li": "Địa lí",
            "gdcd": "GDCD"
        }
        
        # Thiết lập tiêu đề và độ rộng cột
        for col in columns:
            self.tree.heading(col, text=headers[col])
            if col == "sbd":
                self.tree.column(col, width=100, anchor=tk.CENTER)
            else:
                self.tree.column(col, width=80, anchor=tk.CENTER)
        
        # Scrollbar cho Treeview
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack Treeview và scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame phân trang
        pagination_frame = ttk.Frame(main_frame)
        pagination_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Thông tin tổng số dòng
        self.total_label = ttk.Label(pagination_frame, text="Tổng số: 0 dòng")
        self.total_label.pack(side=tk.LEFT)
        
        # Nút phân trang
        ttk.Button(pagination_frame, text="◀◀", command=self.first_page).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(pagination_frame, text="◀", command=self.prev_page).pack(side=tk.RIGHT)
        
        # Label hiển thị trang hiện tại
        self.page_label = ttk.Label(pagination_frame, text="Trang 0/0")
        self.page_label.pack(side=tk.RIGHT, padx=(10, 10))
        
        ttk.Button(pagination_frame, text="▶", command=self.next_page).pack(side=tk.RIGHT)
        ttk.Button(pagination_frame, text="▶▶", command=self.last_page).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Entry và nút nhảy đến trang
        ttk.Label(pagination_frame, text="Đến trang:").pack(side=tk.RIGHT, padx=(10, 2))
        self.goto_page_entry = ttk.Entry(pagination_frame, width=5)
        self.goto_page_entry.pack(side=tk.RIGHT, padx=(0, 5))
        self.goto_page_entry.bind('<Return>', lambda e: self.goto_page())
        ttk.Button(pagination_frame, text="Đi", command=self.goto_page).pack(side=tk.RIGHT)
        
        # Bind sự kiện chọn dòng
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
    
    def load_data(self, df=None):
        """Tải dữ liệu vào Treeview
        
        Args:
            df: DataFrame chứa dữ liệu (nếu None sẽ lấy từ controller)
        """
        if df is None:
            df = self.controller.get_data()
        
        if df is not None and not df.empty:
            # Lưu DataFrame
            self.current_df = df
            
            # Cập nhật combobox sắp xếp
            if hasattr(self, 'sort_combo'):
                column_names = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
                self.sort_combo['values'] = column_names
                if column_names:
                    self.sort_combo.current(0)
            
            # Cập nhật combobox cột tìm kiếm
            if hasattr(self, 'search_column_combo'):
                column_names = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
                self.search_column_combo['values'] = ["Tất cả"] + column_names
                self.search_column_combo.current(0)
            
            # Tính toán số trang
            self.total_rows = len(df)
            self.total_pages = max(1, (self.total_rows + self.rows_per_page - 1) // self.rows_per_page)
            
            # Cập nhật nhãn tổng số dòng
            if hasattr(self, 'total_label'):
                self.total_label.config(text=f"Tổng số: {self.total_rows} dòng")
            
            # Reset về trang đầu tiên
            self.current_page = 1
            
            # Hiển thị dữ liệu trang hiện tại
            self.display_page()
        else:
            # Xóa dữ liệu nếu không có
            if hasattr(self, 'tree'):
                self.tree.delete(*self.tree.get_children())
            if hasattr(self, 'total_label'):
                self.total_label.config(text="Tổng số: 0 dòng")
            if hasattr(self, 'page_label'):
                self.page_label.config(text="Trang 0/0")
    
    def display_page(self):
        """Hiển thị dữ liệu của trang hiện tại"""
        # Sử dụng DataFrame đã lưu
        df = self.current_df
        
        if df is None or df.empty:
            # Xóa dữ liệu cũ trong Treeview
            self.tree.delete(*self.tree.get_children())
            return
        
        # Đảm bảo current_page hợp lệ
        if self.current_page < 1:
            self.current_page = 1
        elif self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        # Tính toán chỉ số bắt đầu và kết thúc của trang hiện tại
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(df))
        
        # Lấy dữ liệu của trang hiện tại
        page_data = df.iloc[start_idx:end_idx]
        
        # Xóa dữ liệu cũ trong Treeview
        self.tree.delete(*self.tree.get_children())
        
        # Thêm dữ liệu mới vào Treeview
        for _, row in page_data.iterrows():
            values = []
            for col in self.tree["columns"]:
                if col in row.index:
                    value = row[col]
                    # Xử lý giá trị NaN
                    if pd.isna(value):
                        values.append("")
                    else:
                        values.append(str(value))
                else:
                    values.append("")
            self.tree.insert("", tk.END, values=values)
        
        # Cập nhật nhãn trang
        if hasattr(self, 'page_label'):
            self.page_label.config(text=f"Trang {self.current_page}/{self.total_pages}")
    
    def search_data(self):
        """Tìm kiếm dữ liệu"""
        search_text = self.search_entry.get().strip()
        search_column = self.search_column_combo.get()
        
        if not search_text:
            # Nếu không có từ khóa, xóa bộ lọc và hiển thị tất cả dữ liệu
            if hasattr(self.controller, 'clear_filter'):
                self.controller.clear_filter()  # Dòng này dư thừa, vì đã có phương thức clear_filter trong class
            # SỬA: Gọi lại dữ liệu gốc thay vì self.load_data()
            original_data = self.controller.get_data()  # Dòng này dư thừa, có thể gọi trực tiếp self.load_data()
            self.load_data(original_data)
            return
        
        # Hiển thị thông báo đang tìm kiếm
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", tk.END, values=["Đang tìm kiếm..."] + [""] * (len(self.tree["columns"]) - 1))
        self.tree.update()
        
        # Gọi controller để tìm kiếm dữ liệu
        if hasattr(self.controller, 'search_data'):
            result_df = self.controller.search_data(search_text, search_column)
        else:
            result_df = None
        
        # Xóa thông báo "Đang tìm kiếm..."
        self.tree.delete(*self.tree.get_children())
        
        # Hiển thị kết quả tìm kiếm
        if result_df is not None and not result_df.empty:
            self.load_data(result_df)
        else:
            # Hiển thị thông báo không tìm thấy
            self.tree.insert("", tk.END, values=["Không tìm thấy kết quả"] + [""] * (len(self.tree["columns"]) - 1))
            # Cập nhật thông tin phân trang
            self.total_rows = 0
            self.total_pages = 0
            self.current_page = 0
            if hasattr(self, 'total_label'):
                self.total_label.config(text="Tổng số: 0 dòng")
            if hasattr(self, 'page_label'):
                self.page_label.config(text="Trang 0/0")
    
    def sort_data(self):
        """Sắp xếp dữ liệu theo cột đã chọn"""
        sort_column = self.sort_combo.get()
        ascending = self.sort_asc.get()
        
        # Tìm tên cột trong DataFrame
        column_map = {}
        for i, col in enumerate(self.tree["columns"]):
            column_map[self.tree.heading(col)["text"]] = col
        
        df_column = column_map.get(sort_column)
        
        if df_column and hasattr(self.controller, 'sort_data'):
            # Gọi controller để sắp xếp dữ liệu
            sorted_df = self.controller.sort_data(df_column, ascending)
            
            # Hiển thị dữ liệu đã sắp xếp
            self.load_data(sorted_df)
    
    def goto_page(self):
        """Nhảy đến trang cụ thể"""
        try:
            page_num = int(self.goto_page_entry.get())
            if 1 <= page_num <= self.total_pages:
                self.current_page = page_num
                self.display_page()
            else:
                from tkinter import messagebox
                messagebox.showwarning("Cảnh báo", f"Số trang phải từ 1 đến {self.total_pages}!")
        except ValueError:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập số trang hợp lệ!")
    
    def first_page(self):
        """Chuyển đến trang đầu tiên"""
        self.current_page = 1
        self.display_page()
    
    def prev_page(self):
        """Chuyển đến trang trước"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()
    
    def next_page(self):
        """Chuyển đến trang tiếp theo"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_page()
    
    def last_page(self):
        """Chuyển đến trang cuối cùng"""
        self.current_page = self.total_pages
        self.display_page()
    
    def on_select(self, event):
        """Xử lý sự kiện chọn dòng trong Treeview"""
        self.selected_items = self.tree.selection()
    
    def add_data(self):
        """Thêm dữ liệu mới"""
        if hasattr(self.controller, 'add_data'):
            self.controller.add_data()
    
    def edit_data(self):
        """Sửa dữ liệu đã chọn"""
        if not self.selected_items:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng cần sửa!")
            return
        
        if hasattr(self.controller, 'edit_data'):
            # Lấy SBD của dòng đầu tiên được chọn
            item = self.selected_items[0]
            values = self.tree.item(item, "values")
            sbd = values[0]
            self.controller.edit_data(sbd)
    
    def delete_data(self):
        """Xóa dữ liệu đã chọn"""
        if not self.selected_items:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng cần xóa!")
            return
        
        if hasattr(self.controller, 'delete_data'):
            # Lấy danh sách SBD của các dòng được chọn
            sbd_list = []
            for item in self.selected_items:
                values = self.tree.item(item, "values")
                sbd_list.append(values[0])
            
            self.controller.delete_data(sbd_list)
    
    def get_selected_sbds(self):
        """Lấy danh sách SBD của các dòng đã chọn
        
        Returns:
            list: Danh sách SBD
        """
        sbd_list = []
        for item in self.selected_items:
            values = self.tree.item(item, "values")
            sbd_list.append(values[0])
        return sbd_list

    def update_result(self, student, subjects_dict=None):
        """Cập nhật kết quả tìm kiếm
        
        Args:
            student: Series chứa thông tin thí sinh
            subjects_dict: Dictionary ánh xạ mã môn học với tên môn học
        """
        if student is None:
            # Hiển thị thông báo không tìm thấy
            self.tree.delete(*self.tree.get_children())
            self.tree.insert("", tk.END, values=["Không tìm thấy kết quả"] + [""] * (len(self.tree["columns"]) - 1))
            return
        
        # Xóa dữ liệu cũ trong Treeview
        self.tree.delete(*self.tree.get_children())
        
        # Tạo DataFrame chỉ chứa thí sinh đã tìm thấy
        import pandas as pd
        df = pd.DataFrame([student])
        
        # Hiển thị kết quả
        values = [student[col] for col in self.tree["columns"]]
        self.tree.insert("", tk.END, values=values)
        
        # Cập nhật thông tin tổng số dòng
        self.total_rows = 1
        self.total_pages = 1
        self.current_page = 1
        self.total_label.config(text=f"Tổng số: 1 dòng")
        self.page_label.config(text=f"Trang 1/1")

    def on_rows_per_page_changed(self, event=None):
        """Xử lý sự kiện thay đổi số dòng hiển thị trên mỗi trang"""
        try:
            # Lấy giá trị mới
            new_rows_per_page = int(self.rows_per_page_combo.get())
            
            # Cập nhật rows_per_page
            self.rows_per_page = new_rows_per_page
            
            # Tính lại số trang
            if self.current_df is not None:
                self.total_pages = max(1, (self.total_rows + self.rows_per_page - 1) // self.rows_per_page)
                
                # Điều chỉnh trang hiện tại nếu cần
                if self.current_page > self.total_pages:
                    self.current_page = self.total_pages
                
                # Hiển thị lại dữ liệu
                self.display_page()
                
        except ValueError:
            # Nếu giá trị không hợp lệ, giữ nguyên
            pass

    def apply_filter(self):
        """Áp dụng bộ lọc dữ liệu"""
        if self.current_df is None or self.current_df.empty:
            return
        
        try:
            # Bắt đầu với DataFrame gốc
            filtered_df = self.current_df.copy()
            
            # Lọc theo môn học và khoảng điểm
            subject = self.filter_subject_combo.get()
            if subject != 'Tất cả':
                # Ánh xạ tên môn học với cột trong DataFrame
                subject_map = {
                    'Toán': 'toan',
                    'Ngữ văn': 'ngu_van',
                    'Ngoại ngữ': 'ngoai_ngu',
                    'Vật lí': 'vat_li',
                    'Hóa học': 'hoa_hoc',
                    'Sinh học': 'sinh_hoc',
                    'Lịch sử': 'lich_su',
                    'Địa lí': 'dia_li',
                    'GDCD': 'gdcd'
                }
                
                subject_col = subject_map.get(subject)
                if subject_col and subject_col in filtered_df.columns:
                    # Lọc theo khoảng điểm của môn học
                    min_score = self.filter_min_score.get().strip()
                    max_score = self.filter_max_score.get().strip()
                    
                    if min_score:
                        min_val = float(min_score)
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[subject_col], errors='coerce') >= min_val]
                    
                    if max_score:
                        max_val = float(max_score)
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[subject_col], errors='coerce') <= max_val]
            
            # Lọc theo tổ hợp môn
            combination = self.filter_combination_combo.get()
            if combination != 'Tất cả':
                if combination.startswith('A00'):
                    # Tổ hợp A00: Toán-Lí-Hóa
                    filtered_df = filtered_df[
                        (pd.to_numeric(filtered_df['toan'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['vat_li'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['hoa_hoc'], errors='coerce').notna())
                    ]
                elif combination.startswith('A01'):
                    # Tổ hợp A01: Toán-Lí-Anh
                    filtered_df = filtered_df[
                        (pd.to_numeric(filtered_df['toan'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['vat_li'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['ngoai_ngu'], errors='coerce').notna())
                    ]
                elif combination.startswith('B00'):
                    # Tổ hợp B00: Toán-Hóa-Sinh
                    filtered_df = filtered_df[
                        (pd.to_numeric(filtered_df['toan'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['hoa_hoc'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['sinh_hoc'], errors='coerce').notna())
                    ]
                elif combination.startswith('C00'):
                    # Tổ hợp C00: Văn-Sử-Địa
                    filtered_df = filtered_df[
                        (pd.to_numeric(filtered_df['ngu_van'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['lich_su'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['dia_li'], errors='coerce').notna())
                    ]
                elif combination.startswith('D01'):
                    # Tổ hợp D01: Văn-Toán-Anh
                    filtered_df = filtered_df[
                        (pd.to_numeric(filtered_df['ngu_van'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['toan'], errors='coerce').notna()) &
                        (pd.to_numeric(filtered_df['ngoai_ngu'], errors='coerce').notna())
                    ]
            
            # Lọc theo điểm trung bình
            min_avg = self.filter_min_avg.get().strip()
            max_avg = self.filter_max_avg.get().strip()
            
            if min_avg or max_avg:
                # Tính điểm trung bình cho mỗi thí sinh
                numeric_cols = ['toan', 'ngu_van', 'ngoai_ngu', 'vat_li', 'hoa_hoc', 'sinh_hoc', 'lich_su', 'dia_li', 'gdcd']
                available_cols = [col for col in numeric_cols if col in filtered_df.columns]
                
                # Chuyển đổi sang numeric và tính trung bình
                for col in available_cols:
                    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
                
                filtered_df['avg_score'] = filtered_df[available_cols].mean(axis=1, skipna=True)
                
                if min_avg:
                    min_avg_val = float(min_avg)
                    filtered_df = filtered_df[filtered_df['avg_score'] >= min_avg_val]
                
                if max_avg:
                    max_avg_val = float(max_avg)
                    filtered_df = filtered_df[filtered_df['avg_score'] <= max_avg_val]
                
                # Xóa cột avg_score tạm thời
                if 'avg_score' in filtered_df.columns:
                    filtered_df = filtered_df.drop('avg_score', axis=1)
            
            # Lưu DataFrame đã lọc
            self.filtered_df = filtered_df
            
            # Hiển thị kết quả
            self.load_data(filtered_df)
            
            # Hiển thị thông báo
            from tkinter import messagebox
            messagebox.showinfo("Thông báo", f"Đã lọc được {len(filtered_df)} kết quả từ {len(self.current_df)} dòng dữ liệu.")
            
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Lỗi", f"Giá trị lọc không hợp lệ: {str(e)}")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi lọc dữ liệu: {str(e)}")
    
    def clear_filter(self):
        """Xóa bộ lọc và hiển thị lại toàn bộ dữ liệu"""
        # Reset các trường lọc
        self.filter_subject_combo.set('Tất cả')
        self.filter_combination_combo.set('Tất cả')
        self.filter_min_score.delete(0, tk.END)
        self.filter_max_score.delete(0, tk.END)
        self.filter_min_avg.delete(0, tk.END)
        self.filter_max_avg.delete(0, tk.END)
        
        # Xóa DataFrame đã lọc
        self.filtered_df = None
        
        # Hiển thị lại toàn bộ dữ liệu
        if self.current_df is not None:
            self.load_data(self.current_df)
        
        from tkinter import messagebox
        messagebox.showinfo("Thông báo", "Đã xóa bộ lọc và hiển thị toàn bộ dữ liệu.")