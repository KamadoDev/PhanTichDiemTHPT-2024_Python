# import tkinter as tk
# from tkinter import ttk
# import pandas as pd

# class SearchView:
#     """Lớp quản lý giao diện tab tìm kiếm"""
    
#     def __init__(self, parent, controller):
#         """Khởi tạo giao diện tab tìm kiếm
        
#         Args:
#             parent: Frame cha
#             controller: Controller điều khiển ứng dụng
#         """
#         self.parent = parent
#         self.controller = controller
        
#         # Tạo giao diện
#         self.create_widgets()
    
#     def create_widgets(self):
#         """Tạo các widget cho tab tìm kiếm"""
#         # Frame chính
#         main_frame = ttk.LabelFrame(self.parent, text="Tìm kiếm thí sinh")
#         main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Frame tìm kiếm
#         search_frame = ttk.Frame(main_frame)
#         search_frame.pack(fill=tk.X, padx=10, pady=10)
        
#         ttk.Label(search_frame, text="Nhập SBD:").pack(side=tk.LEFT, padx=5)
#         self.sbd_entry = ttk.Entry(search_frame, width=20)
#         self.sbd_entry.pack(side=tk.LEFT, padx=5)
#         self.sbd_entry.bind("<Return>", lambda e: self.search())
        
#         ttk.Button(search_frame, text="Tìm kiếm", command=self.search).pack(side=tk.LEFT, padx=5)
        
#         # Frame kết quả
#         result_frame = ttk.LabelFrame(main_frame, text="Kết quả tìm kiếm")
#         result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tạo các nhãn hiển thị thông tin
#         info_frame = ttk.Frame(result_frame)
#         info_frame.pack(fill=tk.X, padx=10, pady=10)
        
#         ttk.Label(info_frame, text="SBD:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
#         self.sbd_label = ttk.Label(info_frame, text="")
#         self.sbd_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
#         # Frame điểm số
#         scores_frame = ttk.LabelFrame(result_frame, text="Điểm các môn")
#         scores_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Tạo grid hiển thị điểm
#         self.score_labels = {}
#         row, col = 0, 0
        
#         # Tạo trước các nhãn cho các môn học
#         subjects = [
#             "Toán", "Ngữ văn", "Ngoại ngữ", "Vật lí", "Hóa học", 
#             "Sinh học", "Lịch sử", "Địa lí", "GDCD", "Mã NN"
#         ]
        
#         for subject in subjects:
#             ttk.Label(scores_frame, text=f"{subject}:").grid(row=row, column=col*2, padx=5, pady=5, sticky=tk.W)
#             self.score_labels[subject] = ttk.Label(scores_frame, text="")
#             self.score_labels[subject].grid(row=row, column=col*2+1, padx=5, pady=5, sticky=tk.W)
            
#             col += 1
#             if col > 2:  # 3 cột, mỗi cột 2 ô (nhãn + giá trị)
#                 col = 0
#                 row += 1
    
#     def search(self):
#         """Tìm kiếm thí sinh theo SBD"""
#         sbd = self.sbd_entry.get().strip()
#         if not sbd:
#             return
        
#         self.controller.search_sbd(sbd)
    
#     def update_result(self, student, subjects_dict):
#         """Cập nhật kết quả tìm kiếm
        
#         Args:
#             student: Series chứa thông tin thí sinh
#             subjects_dict: Dictionary ánh xạ mã môn học với tên môn học
#         """
#         if student is None:
#             # Xóa kết quả cũ
#             self.sbd_label.config(text="Không tìm thấy")
#             for label in self.score_labels.values():
#                 label.config(text="")
#             return
        
#         # Cập nhật thông tin
#         self.sbd_label.config(text=student['sbd'])
        
#         # Cập nhật điểm các môn
#         for code, name in subjects_dict.items():
#             if name in self.score_labels and code in student:
#                 score = student[code]
#                 if pd.isna(score):
#                     self.score_labels[name].config(text="-")
#                 else:
#                     self.score_labels[name].config(text=f"{score:.2f}")
        
#         # Cập nhật mã ngoại ngữ
#         if "Mã NN" in self.score_labels and "ma_ngoai_ngu" in student:
#             ma_nn = student["ma_ngoai_ngu"]
#             if pd.isna(ma_nn):
#                 self.score_labels["Mã NN"].config(text="-")
#             else:
#                 self.score_labels["Mã NN"].config(text=str(ma_nn))