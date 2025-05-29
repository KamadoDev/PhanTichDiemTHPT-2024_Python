#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ứng dụng phân tích điểm thi THPT 2024

Ứng dụng này cho phép người dùng phân tích dữ liệu điểm thi THPT 2024
thông qua giao diện đồ họa với các chức năng như hiển thị thống kê,
tìm kiếm, phân tích và vẽ biểu đồ.
"""

import tkinter as tk
import sys
import os

# Thêm thư mục gốc vào đường dẫn tìm kiếm
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.app_controller import AppController

def main():
    """Hàm chính để khởi chạy ứng dụng"""
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()

if __name__ == "__main__":
    main()