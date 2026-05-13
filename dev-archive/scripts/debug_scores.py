#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, r'c:\AI1 - Copy (3)')

from app import coordinator

# Requirements for the assignment (tuples of text, weight)
requirements = [
    ("Có dùng input()", 10),
    ("Có phép cộng", 10),
    ("Có print()", 10)
]

# Test cases (tuples of input, expected)
testcases = [
    ("2\n3", "5"),
    ("10\n20", "30"),
    ("7\n8", "15")
]

# Code mới từ user (được 64 điểm)
code1 = """# Nhập số thứ nhất
a = int(input("Nhập số thứ nhất: "))

# Nhập số thứ hai
b = int(input("Nhập số thứ hai: "))

# Tính và in tổng hai số
print("Tổng hai số là:", a + b)"""

# Code so sánh - không comment
code2 = """a = int(input())
b = int(input())
print(a + b)"""

print("=" * 60)
print("CODE ẢNH 1:")
print("=" * 60)
print(code1)
print("\n" + "=" * 60)
result1 = coordinator(code1, requirements, testcases)
print("KẾT QUẢ ẢNH 1:")
print(f"  Syntax Score: {result1['syntax']['score']}/25")
print(f"  Requirement Score: {result1['requirement']['score']}/25")
print(f"  Structure Score: {result1['structure']['score']}/25")
print(f"  Test Score: {result1['test']['score']}/25")
print(f"  LLM Score: {result1['llm']['score']}/25")
print(f"  TOTAL: {sum([result1['syntax']['score'], result1['requirement']['score'], result1['structure']['score'], result1['test']['score']])}/100")
print(f"\nDetails:")
print(f"  Syntax Error: {result1['syntax'].get('error', 'None')}")
print(f"  Requirements Met: {result1['requirement'].get('details', [])}")
print(f"  Structure Issues: {result1['structure'].get('details', [])}")
print(f"  Test Results: {result1['test'].get('details', 'No details')}")

print("\n" + "=" * 60)
print("CODE ẢNH 2:")
print("=" * 60)
print(code2)
print("\n" + "=" * 60)
result2 = coordinator(code2, requirements, testcases)
print("KẾT QUẢ ẢNH 2:")
print(f"  Syntax Score: {result2['syntax']['score']}/25")
print(f"  Requirement Score: {result2['requirement']['score']}/25")
print(f"  Structure Score: {result2['structure']['score']}/25")
print(f"  Test Score: {result2['test']['score']}/25")
print(f"  LLM Score: {result2['llm']['score']}/25")
print(f"  TOTAL: {sum([result2['syntax']['score'], result2['requirement']['score'], result2['structure']['score'], result2['test']['score']])}/100")
print(f"\nDetails:")
print(f"  Syntax Error: {result2['syntax'].get('error', 'None')}")
print(f"  Requirements Met: {result2['requirement'].get('details', [])}")
print(f"  Structure Issues: {result2['structure'].get('details', [])}")
print(f"  Test Results: {result2['test'].get('details', 'No details')}")

print("\n" + "=" * 60)
print("SO SÁNH:")
print("=" * 60)
print(f"Score ảnh 1: {sum([result1['syntax']['score'], result1['requirement']['score'], result1['structure']['score'], result1['test']['score']])} điểm")
print(f"Score ảnh 2: {sum([result2['syntax']['score'], result2['requirement']['score'], result2['structure']['score'], result2['test']['score']])} điểm")
