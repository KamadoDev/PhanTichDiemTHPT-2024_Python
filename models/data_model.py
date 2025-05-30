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
        self._cache = {}  # Cache cho các kết quả đã tính
        
    def clear_cache(self):
        """Xóa cache khi dữ liệu thay đổi"""
        self._cache.clear()
    
    def load_data(self):
        """Đọc dữ liệu từ file CSV"""
        try:
            self.df = pd.read_csv(self.file_path)
            self.process_data()  # Xử lý dữ liệu sau khi đọc
            self.clear_cache()  # Xóa cache khi tải dữ liệu mới
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def process_data(self):
        """Xử lý dữ liệu sau khi đọc"""
        if self.df is not None:
            # Đảm bảo cột SBD là kiểu chuỗi
            self.df['sbd'] = self.df['sbd'].astype(str).str.strip()
            
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
        
        # Chuyển đổi sbd đầu vào thành chuỗi và loại bỏ khoảng trắng
        sbd = str(sbd).strip()
        
        # Sử dụng phương thức loc thay vì tạo DataFrame mới
        # Đảm bảo cột 'sbd' trong DataFrame là chuỗi và so sánh chính xác
        mask = self.df['sbd'].astype(str).str.strip() == sbd
        
        if mask.any():
            return self.df.loc[mask.idxmax()]
        return None
    
    def analyze_subject(self, subject_name):
        """Phân tích thống kê cho một môn học"""
        if self.df is None:
            return None
        
        subject_col = self.get_subject_code(subject_name)
        if not subject_col:
            print(f"Không tìm thấy mã môn học cho: {subject_name}")
            return None
        
        print(f"Phân tích môn: {subject_name}, Cột: {subject_col}")
      
        # Sử dụng:
        data = self.df[subject_col].dropna()
        data = data[data > 0]  # Loại bỏ điểm 0
        print(f"Số lượng dữ liệu hợp lệ: {len(data)}")
        
        if len(data) == 0:
            print("Không có dữ liệu hợp lệ để phân tích")
            return None
        
        # Thêm kiểm tra dữ liệu chi tiết
        print(f"Giá trị nhỏ nhất trong dữ liệu: {data.min()}")
        print(f"Số lượng điểm 0: {(data == 0).sum()}")
        print(f"Số lượng điểm < 1: {(data < 1).sum()}")
        print(f"10 giá trị nhỏ nhất: {data.nsmallest(10).tolist()}")
        
        # Thống kê cơ bản
        stats = {}
        stats['count'] = data.count()
        stats['mean'] = data.mean()
        stats['median'] = data.median()
        stats['std'] = data.std()
        stats['min'] = data.min()
        stats['max'] = data.max()
        
        print(f"Điểm thấp nhất: {stats['min']}")
        print(f"Điểm cao nhất: {stats['max']}")
        
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
    
    def save_data(self, file_path=None):
        """Lưu dữ liệu ra file CSV"""
        try:
            if file_path is None:
                file_path = self.file_path
            
            self.df.to_csv(file_path, index=False)
            return True, "Đã lưu dữ liệu thành công"
        except Exception as e:
            return False, f"Lỗi khi lưu dữ liệu: {str(e)}"
    
    def get_correlation_matrix(self):
        """Tính ma trận tương quan giữa các môn học"""
        print("=== DEBUG CORRELATION MATRIX ===")
        
        if self.df is None:
            print("ERROR: self.df is None - dữ liệu chưa được load")
            return None
        
        print(f"DataFrame shape: {self.df.shape}")
        print(f"DataFrame columns: {list(self.df.columns)}")
        
        # Lấy dữ liệu các môn học
        subject_cols = list(self.subjects_dict.keys())
        print(f"Tìm kiếm các cột: {subject_cols}")
        
        # Kiểm tra cột nào tồn tại
        existing_cols = [col for col in subject_cols if col in self.df.columns]
        missing_cols = [col for col in subject_cols if col not in self.df.columns]
        
        print(f"Các cột TỒN TẠI: {existing_cols}")
        print(f"Các cột THIẾU: {missing_cols}")
        
        if len(existing_cols) < 2:
            print(f"ERROR: Không đủ cột để tính correlation (cần ít nhất 2, có {len(existing_cols)})")
            return None
        
        # Kiểm tra dữ liệu trước khi dropna
        print(f"Số dòng trước dropna: {len(self.df)}")
        for col in existing_cols:
            null_count = self.df[col].isnull().sum()
            print(f"Cột {col}: {null_count} giá trị null")
        
        # Thay dòng này:
        # correlation_data = self.df[subject_cols].dropna()
        
        # Bằng dòng này (yêu cầu ít nhất 3 môn có điểm):
        correlation_data = self.df[existing_cols].dropna(thresh=3)
        print(f"Số dòng SAU dropna: {len(correlation_data)}")
        
        if len(correlation_data) == 0:
            print("ERROR: Không có dữ liệu sau khi dropna")
            return None
        
        # Tính ma trận tương quan
        correlation_matrix = correlation_data.corr()
        print(f"Ma trận tương quan shape: {correlation_matrix.shape}")
        print("=== END DEBUG ===")
        return correlation_matrix

    def get_subject_combinations_data(self):
        """Lấy dữ liệu phân tích theo tổ hợp môn"""
        if self.df is None:
            return None
        
        # Định nghĩa các tổ hợp môn phổ biến
        combinations = {
            'A00': ['toan', 'vat_li', 'hoa_hoc'],
            'A02': ['toan', 'vat_li', 'sinh_hoc'],
            'B00': ['toan', 'hoa_hoc', 'sinh_hoc'],
            'C00': ['ngu_van', 'lich_su', 'dia_li'],
            'C19': ['ngu_van', 'lich_su', 'gdcd'],
            'C20': ['ngu_van', 'dia_li', 'gdcd']
        }
        
        results = {}
        for combo_name, subjects in combinations.items():
            # Tính điểm tổng cho tổ hợp
            valid_data = self.df[subjects].dropna()
            if len(valid_data) > 0:
                total_scores = valid_data.sum(axis=1)
                results[combo_name] = {
                    'scores': total_scores,
                    'count': len(total_scores),
                    'mean': total_scores.mean(),
                    'std': total_scores.std(),
                    'subjects': [self.subjects_dict[s] for s in subjects]
                }
        
        return results

    def get_all_subjects_distribution(self):
        """Lấy dữ liệu phân phối điểm tất cả các môn"""
        if self.df is None:
            return None
        
        results = {}
        for col, name in self.subjects_dict.items():
            data = self.df[col].dropna()
            if len(data) > 0:
                results[name] = data
        
        return results

    def get_average_scores_data(self):
        """Lấy dữ liệu điểm trung bình các môn học"""
        if self.df is None:
            return None
        
        avg_scores = {}
        for code, name in self.subjects_dict.items():
            if code in self.df.columns:
                avg_score = self.df[code].mean()
                avg_scores[name] = avg_score
        
        return avg_scores
    
    def get_combination_distribution_data(self):
        """Lấy dữ liệu phân phối tổ hợp môn với tối ưu hiệu suất"""
        if self.df is None or len(self.df) == 0:
            return {'Không có dữ liệu': 1}
        
        # Sử dụng cache để tránh tính toán lại
        cache_key = 'combination_distribution'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Lấy các cột môn học có sẵn trong DataFrame
            subject_columns = [code for code in self.subjects_dict.keys() if code in self.df.columns]
            
            if len(subject_columns) < 3:
                result = {'Không đủ dữ liệu môn học': 1}
                self._cache[cache_key] = result
                return result
            
            combinations = {}
            
            # Giới hạn số lượng dòng xử lý để tránh crash (tối đa 1000 dòng)
            max_rows = min(1000, len(self.df))
            subject_data = self.df[subject_columns].head(max_rows).copy()
            
            print(f"Đang xử lý {len(subject_data)} học sinh...")
            
            # Xử lý từng dòng với progress tracking
            for idx, (_, row) in enumerate(subject_data.iterrows()):
                if idx % 100 == 0:  # Progress indicator
                    print(f"Đã xử lý {idx}/{len(subject_data)} học sinh")
                
                # Lọc các môn có điểm hợp lệ (>= 0)
                valid_scores = row.dropna()
                valid_scores = valid_scores[valid_scores >= 0]  # Loại bỏ điểm âm
                
                if len(valid_scores) < 3:
                    continue
                    
                # Lấy 3 môn có điểm cao nhất
                top_3 = valid_scores.nlargest(3)
                
                # Tạo tên tổ hợp từ tên môn học (sắp xếp theo thứ tự alphabet)
                try:
                    combo_subjects = sorted([self.subjects_dict.get(code, code) for code in top_3.index])
                    combo_name = ' - '.join(combo_subjects)
                    combinations[combo_name] = combinations.get(combo_name, 0) + 1
                except Exception as e:
                    print(f"Lỗi xử lý tổ hợp cho học sinh {idx}: {e}")
                    continue
            
            print(f"Hoàn thành xử lý. Tìm thấy {len(combinations)} tổ hợp khác nhau.")
            
            # Lưu vào cache và return
            if combinations:
                # Chỉ lấy top 10 tổ hợp phổ biến nhất
                sorted_combinations = dict(sorted(combinations.items(), key=lambda x: x[1], reverse=True)[:10])
                self._cache[cache_key] = sorted_combinations
                return sorted_combinations
            else:
                result = {'Không có dữ liệu hợp lệ': 1}
                self._cache[cache_key] = result
                return result
                
        except Exception as e:
            print(f"Lỗi trong get_combination_distribution_data: {e}")
            result = {'Lỗi xử lý dữ liệu': 1}
            self._cache[cache_key] = result
            return result
    
    def get_subject_distribution_data(self, subject_code):
        """Lấy dữ liệu phân phối điểm với tối ưu hóa"""
        cache_key = f'distribution_{subject_code}'
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if self.df is None or subject_code not in self.df.columns:
            return None
            
        # Sử dụng vectorized operations
        scores = pd.to_numeric(self.df[subject_code], errors='coerce')
        scores = scores.dropna()
        
        if len(scores) == 0:
            return None
            
        result = scores.values
        self._cache[cache_key] = result
        return result
    
    def clear_cache(self):
        """Xóa cache khi dữ liệu thay đổi"""
        self._cache.clear()

    def get_combination_ratios(self):
        """Lấy tỷ lệ học sinh theo từng tổ hợp môn (cho biểu đồ tròn)"""
        if self.df is None:
            return None
        
        combinations = {
            'A00': ['toan', 'vat_li', 'hoa_hoc'],
            'A02': ['toan', 'vat_li', 'sinh_hoc'], 
            'B00': ['toan', 'hoa_hoc', 'sinh_hoc'],
            'C00': ['ngu_van', 'lich_su', 'dia_li'],
            'C19': ['ngu_van', 'lich_su', 'gdcd'],
            'C20': ['ngu_van', 'dia_li', 'gdcd']
        }
        
        ratios = {}
        total_students = len(self.df)
        
        for combo_name, subjects in combinations.items():
            valid_data = self.df[subjects].dropna()
            count = len(valid_data)
            ratios[combo_name] = {
                'count': count,
                'percentage': (count / total_students) * 100 if total_students > 0 else 0
            }
        
        return ratios
    
    def get_combination_comparison_data(self):
        """Lấy dữ liệu so sánh điểm các tổ hợp (cho boxplot)"""
        if self.df is None:
            return None
        
        combinations = {
            'A00': ['toan', 'vat_li', 'hoa_hoc'],
            'A02': ['toan', 'vat_li', 'sinh_hoc'],
            'B00': ['toan', 'hoa_hoc', 'sinh_hoc'],
            'C00': ['ngu_van', 'lich_su', 'dia_li'],
            'C19': ['ngu_van', 'lich_su', 'gdcd'],
            'C20': ['ngu_van', 'dia_li', 'gdcd']
        }
        
        comparison_data = {}
        for combo_name, subjects in combinations.items():
            valid_data = self.df[subjects].dropna()
            if len(valid_data) > 0:
                total_scores = valid_data.sum(axis=1)
                comparison_data[combo_name] = total_scores
        
        return comparison_data
    
    # Xóa hoàn toàn phương thức get_correlation_matrix (dòng 345-392)
    def get_subject_correlation_data(self, subject1_code, subject2_code):
        """Lấy dữ liệu tương quan giữa 2 môn học (cho scatter plot)"""
        if (self.df is None or 
            subject1_code not in self.subjects_dict or 
            subject2_code not in self.subjects_dict):
            return None
        
        data = self.df[[subject1_code, subject2_code]].dropna()
        if len(data) > 0:
            return {
                'x': data[subject1_code],
                'y': data[subject2_code],
                'subject1_name': self.subjects_dict[subject1_code],
                'subject2_name': self.subjects_dict[subject2_code]
            }
        return None
    
    def get_top_students_data(self, top_n=20):
        """Lấy dữ liệu top học sinh có điểm cao nhất cho biểu đồ cột ngang"""
        if self.df is None:
            return None
        
        # Tính tổng điểm 3 môn chính (Toán, Văn, Anh)
        main_subjects = ['toan', 'ngu_van', 'ngoai_ngu']
        valid_data = self.df[main_subjects + ['sbd']].dropna()
        
        if len(valid_data) > 0:
            valid_data['total_score'] = valid_data[main_subjects].sum(axis=1)
            top_students = valid_data.nlargest(top_n, 'total_score')
            
            return {
                'sbd': top_students['sbd'].tolist(),
                'scores': top_students['total_score'].tolist(),
                'count': len(top_students)
            }
        return None