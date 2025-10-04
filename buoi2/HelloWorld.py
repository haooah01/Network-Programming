#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HelloWorld.py - Simple Hello World program in Python
Created for Network Programming course
"""

def main():
    """Main function to display Hello World message"""
    print("Hello, World!")
    print("Chào mừng đến với lập trình Python!")
    print("=" * 40)
    
    # Display some system information
    import sys
    import platform
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print("=" * 40)
    
    # Simple interaction
    name = input("Nhập tên của bạn: ")
    print(f"Xin chào, {name}!")
    print(f"Chúc mừng bạn đã chạy thành công chương trình Python!")

if __name__ == "__main__":
    main()