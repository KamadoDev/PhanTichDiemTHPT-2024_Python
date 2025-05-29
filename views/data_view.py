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
        
        # Tạo giao diện
        self.create_widgets()
    
    # Thêm các phương thức thiếu
    def add_data(self):
        """Thêm dữ liệu mới"""
        self.controller.add_data()
    
    def edit_data(self):
        """Sửa dữ liệu đã chọn"""
        selected_items = self.tree.selection()
        if not selected_items:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một thí sinh để sửa!")
            return
        
        # Lấy SBD của thí sinh đã chọn
        item = selected_items[0]  # Chỉ lấy dòng đầu tiên nếu chọn nhiều
        values = self.tree.item(item, "values")
        sbd = values[0]  # SBD ở cột đầu tiên
        
        # Gọi controller để sửa dữ liệu
        self.controller.edit_data(sbd)
    
    def delete_data(self):
        """Xóa dữ liệu đã chọn"""
        selected_items = self.tree.selection()
        if not selected_items:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một thí sinh để xóa!")
            return
        
        # Lưu các mục đã chọn
        self.selected_items = selected_items
        
        # Lấy danh sách SBD của các thí sinh đã chọn
        sbd_list = self.get_selected_sbds()
        
        # Gọi controller để xóa dữ liệu
        self.controller.delete_data(sbd_list)
    
    # Thêm các phương thức phân trang
    def first_page(self):
        """Chuyển đến trang đầu tiên"""
        if self.current_page > 1:
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
        if self.current_page < self.total_pages:
            self.current_page = self.total_pages
            self.display_page()
    
    def change_rows_per_page(self, event=None):
        """Thay đổi số dòng mỗi trang"""
        try:
            self.rows_per_page = int(self.rows_combo.get())
            # Tính lại số trang
            self.total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
            # Đảm bảo trang hiện tại không vượt quá tổng số trang
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            if self.current_page < 1:
                self.current_page = 1
            # Hiển thị lại dữ liệu
            self.display_page()
        except ValueError:
            pass
    
    def display_page(self):
        """Hiển thị dữ liệu của trang hiện tại"""
        # Lấy dữ liệu từ controller
        df = self.controller.get_filtered_data() if hasattr(self.controller, 'get_filtered_data') else self.controller.get_data()
        if df is None or df.empty:
            return
        
        # Tính toán chỉ số bắt đầu và kết thúc của trang hiện tại
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(df))
        
        # Lấy dữ liệu của trang hiện tại
        page_data = df.iloc[start_idx:end_idx]
        
        # Xóa dữ liệu cũ trong Treeview
        self.tree.delete(*self.tree.get_children())
        
        # Thêm dữ liệu mới vào Treeview
        for _, row in page_data.iterrows():
            values = [row[col] for col in self.tree["columns"]]
            self.tree.insert("", tk.END, values=values)
        
        # Cập nhật nhãn trang
        self.page_label.config(text=f"Trang {self.current_page}/{self.total_pages}")
    
    def create_widgets(self):
        """Tạo các widget cho tab quản lý dữ liệu"""
        # Frame chính
        main_frame = ttk.LabelFrame(self.parent, text="Quản lý dữ liệu điểm thi")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame công cụ
        tools_frame = ttk.Frame(main_frame)
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Đảm bảo các nút thêm, sửa, xóa được hiển thị
        ttk.Button(tools_frame, text="Thêm mới", command=self.add_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(tools_frame, text="Sửa", command=self.edit_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(tools_frame, text="Xóa", command=self.delete_data).pack(side=tk.LEFT, padx=5)
        
        # Frame tìm kiếm và lọc
        # Thay đổi trong phần search_frame của hàm create_widgets
        search_frame = ttk.Frame(tools_frame)
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(search_frame, text="Tìm kiếm:").\
            pack(side=tk.LEFT, padx=5)
        
        # Thêm combobox chọn cột tìm kiếm
        ttk.Label(search_frame, text="Cột:").\
            pack(side=tk.LEFT, padx=5)
        self.search_column_combo = ttk.Combobox(search_frame, width=10, state="readonly")
        self.search_column_combo.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_data())
        
        ttk.Button(search_frame, text="Tìm", command=self.search_data).\
            pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Sắp xếp theo:").\
            pack(side=tk.LEFT, padx=5)
        self.sort_combo = ttk.Combobox(search_frame, width=15, state="readonly")
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        
        # Thêm nút sắp xếp tăng/giảm dần
        self.sort_asc = tk.BooleanVar(value=True)
        self.sort_asc_button = ttk.Checkbutton(search_frame, text="Tăng dần", 
                                             variable=self.sort_asc, 
                                             command=self.sort_data)
        self.sort_asc_button.pack(side=tk.LEFT, padx=5)
        
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.sort_data())
    
        # Thay đổi trong phần pagination_frame của hàm create_widgets
        pagination_frame = ttk.Frame(main_frame)
        pagination_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(pagination_frame, text="<<", command=self.first_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text="<", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        
        self.page_label = ttk.Label(pagination_frame, text="Trang 1")
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        # Thêm nhảy đến trang cụ thể
        ttk.Label(pagination_frame, text="Đến trang:").pack(side=tk.LEFT, padx=5)
        self.goto_page_entry = ttk.Entry(pagination_frame, width=5)
        self.goto_page_entry.pack(side=tk.LEFT, padx=2)
        self.goto_page_entry.bind("<Return>", lambda e: self.goto_page())
        ttk.Button(pagination_frame, text="Đi", command=self.goto_page, width=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(pagination_frame, text=">", command=self.next_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text=">>", command=self.last_page).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(pagination_frame, text="Số dòng mỗi trang:").pack(side=tk.LEFT, padx=10)
        self.rows_combo = ttk.Combobox(pagination_frame, width=5, values=[10, 20, 50, 100], state="readonly")
        self.rows_combo.current(1)  # Mặc định 20 dòng
        self.rows_combo.pack(side=tk.LEFT, padx=5)
        self.rows_combo.bind("<<ComboboxSelected>>", self.change_rows_per_page)
    
        # Thêm nhãn hiển thị tổng số dòng
        self.total_label = ttk.Label(pagination_frame, text="Tổng số: 0 dòng")
        self.total_label.pack(side=tk.RIGHT, padx=10)
        
        # Thêm phần này để tạo Treeview
        # Frame chứa Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo Scrollbar
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Tạo Treeview với các cột
        columns = ("sbd", "toan", "ngu_van", "ngoai_ngu", "vat_li", "hoa_hoc", 
                  "sinh_hoc", "lich_su", "dia_li", "gdcd", "ma_ngoai_ngu")
        column_headings = ("SBD", "Toán", "Ngữ văn", "Ngoại ngữ", "Vật lí", "Hóa học", 
                          "Sinh học", "Lịch sử", "Địa lí", "GDCD", "Mã NN")
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                               yscrollcommand=scrollbar_y.set,
                               xscrollcommand=scrollbar_x.set)
        
        # Thiết lập các cột
        for col, heading in zip(columns, column_headings):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=80, anchor=tk.CENTER)
        
        # Kết nối scrollbar với Treeview
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Hiển thị Treeview
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bắt sự kiện chọn dòng
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
    
    def on_tree_select(self, event=None):
        """Xử lý sự kiện khi chọn dòng trong Treeview"""
        self.selected_items = self.tree.selection()

# Sửa hàm load_data để cập nhật combobox cột tìm kiếm
    def load_data(self, df=None):
        """Tải dữ liệu vào Treeview
        
        Args:
            df: DataFrame chứa dữ liệu (nếu None sẽ lấy từ controller)
        """
        if df is None:
            df = self.controller.get_data()
        
        if df is not None:
            # Cập nhật combobox sắp xếp
            column_names = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
            self.sort_combo['values'] = column_names
            self.sort_combo.current(0)
            
            # Cập nhật combobox cột tìm kiếm
            self.search_column_combo['values'] = ["Tất cả"] + column_names
            self.search_column_combo.current(0)
            
            # Tính toán số trang
            self.total_rows = len(df)
            self.total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
            
            # Cập nhật nhãn tổng số dòng
            self.total_label.config(text=f"Tổng số: {self.total_rows} dòng")
            
            # Hiển thị dữ liệu trang hiện tại
            self.display_page()

# Sửa hàm search_data để hỗ trợ tìm kiếm theo cột
    def search_data(self):
        """Tìm kiếm dữ liệu"""
        search_text = self.search_entry.get().strip()
        search_column = self.search_column_combo.get()
        
        if not search_text:
            # Nếu không có từ khóa, xóa bộ lọc và hiển thị tất cả dữ liệu
            self.controller.clear_filter()  # THÊM DÒNG NÀY
            self.load_data()
            return
        
        # Hiển thị thông báo đang tìm kiếm
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", tk.END, values=["Đang tìm kiếm..."] + [""] * (len(self.tree["columns"]) - 1))
        self.tree.update()
        
        # Gọi controller để tìm kiếm dữ liệu
        result_df = self.controller.search_data(search_text, search_column)
        
        # Xóa thông báo "Đang tìm kiếm..."
        self.tree.delete(*self.tree.get_children())
        
        # Hiển thị kết quả tìm kiếm
        if result_df is not None and not result_df.empty:
            self.load_data(result_df)
            # Cập nhật thông tin tổng số dòng
            self.total_rows = len(result_df)
            self.total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
            self.current_page = 1  # Reset về trang đầu tiên
            self.total_label.config(text=f"Tổng số: {self.total_rows} dòng")
            self.page_label.config(text=f"Trang {self.current_page}/{self.total_pages}")
        else:
            # Hiển thị thông báo không tìm thấy
            self.tree.insert("", tk.END, values=["Không tìm thấy kết quả"] + [""] * (len(self.tree["columns"]) - 1))

# Sửa hàm sort_data để hỗ trợ sắp xếp tăng/giảm dần
    def sort_data(self):
        """Sắp xếp dữ liệu theo cột đã chọn"""
        sort_column = self.sort_combo.get()
        ascending = self.sort_asc.get()
        
        # Tìm tên cột trong DataFrame
        column_map = {}
        for i, col in enumerate(self.tree["columns"]):
            column_map[self.tree.heading(col)["text"]] = col
        
        df_column = column_map.get(sort_column)
        
        if df_column:
            # Gọi controller để sắp xếp dữ liệu
            sorted_df = self.controller.sort_data(df_column, ascending)
            
            # Hiển thị dữ liệu đã sắp xếp
            self.load_data(sorted_df)

# Thêm hàm goto_page để nhảy đến trang cụ thể
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

def update_result(self, student, subjects_dict):
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