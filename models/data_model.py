#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module xử lý dữ liệu điểm thi THPT

Module này chứa các lớp và hàm để xử lý dữ liệu điểm thi THPT,
bao gồm đọc dữ liệu, xử lý và phân tích thống kê.
"""

import os
import pandas as pd
import numpy as np

class DataModel:
    """Lớp xử lý dữ liệu điểm thi THPT"""
    
    def __init__(self):
        """Khởi tạo model dữ liệu"""
        self.df = None
        self.file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "diem_thi_thpt_2024.csv")
        self.subjects_dict = {
            'toan': 'Toán', 
            'ngu_van': 'Ngữ văn', 
            'ngoai_ngu': 'Ngoại ngữ',
            'vat_li': 'Vật lí', 
            'hoa_hoc': 'Hóa học', 
            'sinh_hoc': 'Sinh học',
            'lich_su': 'Lịch sử', 
            'dia_li': 'Địa lí', 
            'gdcd': 'GDCD'
        }
        self.current_page = 0
        self.rows_per_page = 20
        
    def load_data(self):
        """Đọc dữ liệu từ file CSV"""
        try:
            self.df = pd.read_csv(self.file_path)
            self.process_data()
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def process_data(self):
        """Xử lý dữ liệu sau khi đọc"""
        if self.df is not None:
            # Chuyển các cột điểm về kiểu số
            numeric_columns = ['toan', 'ngu_van', 'ngoai_ngu', 'vat_li', 
                              'hoa_hoc', 'sinh_hoc', 'lich_su', 'dia_li', 'gdcd']
            for col in numeric_columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
    
    def get_subject_names(self):
        """Lấy danh sách tên các môn học"""
        return list(self.subjects_dict.values())
    
    def get_subject_code(self, subject_name):
        """Lấy mã môn học từ tên"""
        for code, name in self.subjects_dict.items():
            if name == subject_name:
                return code
        return None
    
    def get_overview_stats(self):
        """Lấy thống kê tổng quan về dữ liệu"""
        if self.df is None:
            return None
        
        stats = {}
        stats['total_students'] = len(self.df)
        
        # Thống kê số lượng thí sinh tham gia từng môn
        stats['subject_counts'] = {}
        for col, name in self.subjects_dict.items():
            count = self.df[col].count()
            percentage = count / stats['total_students'] * 100
            stats['subject_counts'][name] = (count, percentage)
        
        # Thống kê điểm trung bình từng môn
        stats['subject_means'] = {}
        for col, name in self.subjects_dict.items():
            mean = self.df[col].mean()
            stats['subject_means'][name] = mean if not pd.isna(mean) else None
        
        # Thống kê điểm cao nhất từng môn
        stats['subject_max'] = {}
        for col, name in self.subjects_dict.items():
            max_score = self.df[col].max()
            stats['subject_max'][name] = max_score if not pd.isna(max_score) else None
        
        return stats
    
    def search_by_sbd(self, sbd):
        """Tìm kiếm thí sinh theo SBD"""
        if self.df is None or not sbd:
            return None
        
        result = self.df[self.df['sbd'] == sbd]
        if len(result) > 0:
            return result.iloc[0]
        return None
    
    def analyze_subject(self, subject_name):
        """Phân tích thống kê cho một môn học"""
        if self.df is None:
            return None
        
        subject_col = self.get_subject_code(subject_name)
        if not subject_col:
            return None
        
        data = self.df[subject_col].dropna()
        
        # Thống kê cơ bản
        stats = {}
        stats['count'] = data.count()
        stats['mean'] = data.mean()
        stats['median'] = data.median()
        stats['std'] = data.std()
        stats['min'] = data.min()
        stats['max'] = data.max()
        
        # Phân phối điểm
        bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        hist, edges = np.histogram(data, bins=bins)
        stats['distribution'] = []
        
        for i in range(len(hist)):
            percentage = hist[i] / stats['count'] * 100 if stats['count'] > 0 else 0
            stats['distribution'].append({
                'range': (edges[i], edges[i+1]),
                'count': hist[i],
                'percentage': percentage
            })
        
        return stats
    
    def get_chart_data(self, subject_name):
        """Lấy dữ liệu để vẽ biểu đồ"""
        if self.df is None:
            return None
        
        subject_col = self.get_subject_code(subject_name)
        if not subject_col:
            return None
        
        return self.df[subject_col].dropna()
    
    def get_paginated_data(self):
        """Lấy dữ liệu theo trang"""
        if self.df is None:
            return None, 0
        
        total_pages = (len(self.df) - 1) // self.rows_per_page + 1
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.df))
        
        return self.df.iloc[start_idx:end_idx], total_pages
    
    def get_current_data(self):
        """Lấy toàn bộ dữ liệu hiện tại
        
        Returns:
            DataFrame: Dữ liệu hiện tại
        """
        return self.df
    
    def next_page(self):
        """Chuyển đến trang tiếp theo"""
        if self.df is None:
            return False
        
        total_pages = (len(self.df) - 1) // self.rows_per_page + 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            return True
        return False
    
    def prev_page(self):
        """Chuyển đến trang trước"""
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False
    
    def go_to_page(self, page):
        """Chuyển đến trang cụ thể"""
        if self.df is None:
            return False
        
        total_pages = (len(self.df) - 1) // self.rows_per_page + 1
        if 0 <= page < total_pages:
            self.current_page = page
            return True
        return False
    
    def add_student(self, student_data):
        """Thêm thí sinh mới"""
        if self.df is None:
            return False
        
        try:
            # Kiểm tra SBD đã tồn tại chưa
            if student_data['sbd'] in self.df['sbd'].values:
                return False, "SBD đã tồn tại"
            
            # Thêm thí sinh mới
            self.df = pd.concat([self.df, pd.DataFrame([student_data])], ignore_index=True)
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def update_student(self, sbd, student_data):
        """Cập nhật thông tin thí sinh"""
        if self.df is None:
            return False, "Chưa tải dữ liệu"
        
        try:
            # Tìm thí sinh theo SBD
            idx = self.df[self.df['sbd'] == sbd].index
            if len(idx) == 0:
                return False, "Không tìm thấy thí sinh"
            
            # Cập nhật thông tin
            for key, value in student_data.items():
                if key in self.df.columns:
                    self.df.loc[idx[0], key] = value
            
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def delete_student(self, sbd):
        """Xóa thí sinh"""
        if self.df is None:
            return False, "Chưa tải dữ liệu"
        
        try:
            # Tìm thí sinh theo SBD
            idx = self.df[self.df['sbd'] == sbd].index
            if len(idx) == 0:
                return False, "Không tìm thấy thí sinh"
            
            # Xóa thí sinh
            self.df = self.df.drop(idx[0])
            self.df = self.df.reset_index(drop=True)
            
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def delete_multiple_students(self, sbd_list):
        """Xóa nhiều thí sinh"""
        if self.df is None:
            return False, "Chưa tải dữ liệu"
        
        try:
            # Tìm các thí sinh theo SBD
            idx = self.df[self.df['sbd'].isin(sbd_list)].index
            if len(idx) == 0:
                return False, "Không tìm thấy thí sinh"
            
            # Xóa các thí sinh
            self.df = self.df.drop(idx)
            self.df = self.df.reset_index(drop=True)
            
            return True, f"Đã xóa {len(idx)} thí sinh"
        except Exception as e:
            return False, str(e)
    
    def sort_data(self, column, ascending=True):
        """Sắp xếp dữ liệu theo cột"""
        if self.df is None or column not in self.df.columns:
            return False
        
        try:
            self.df = self.df.sort_values(by=column, ascending=ascending)
            self.current_page = 0  # Reset về trang đầu tiên
            return True
        except Exception:
            return False
    
    def filter_data(self, column, value, condition='equal'):
        """Lọc dữ liệu theo điều kiện"""
        if self.df is None or column not in self.df.columns:
            return None
        
        try:
            if condition == 'equal':
                filtered = self.df[self.df[column] == value]
            elif condition == 'greater':
                filtered = self.df[self.df[column] > value]
            elif condition == 'less':
                filtered = self.df[self.df[column] < value]
            elif condition == 'contains':
                filtered = self.df[self.df[column].astype(str).str.contains(str(value), na=False)]
            else:
                return None
            
            return filtered
        except Exception:
            return None
    
    def save_data(self):
        """Lưu dữ liệu vào file CSV"""
        if self.df is None:
            return False, "Chưa tải dữ liệu"
        
        try:
            self.df.to_csv(self.file_path, index=False)
            return True, "Đã lưu dữ liệu thành công"
        except Exception as e:
            return False, f"Lỗi khi lưu dữ liệu: {str(e)}"