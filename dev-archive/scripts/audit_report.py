# -*- coding: utf-8 -*-
"""
COMPREHENSIVE AUDIT REPORT: Multi-Agent Code Evaluation System
============================================================
Kiểm tra chi tiết hệ thống chấm bài tự động Multi-Agent
"""

import os
import re

# Task 1: Kiểm tra database connection
print("="*70)
print("1. KIỂM TRA QUẢN LÝ DATABASE")
print("="*70)

# Check app.py DATABASE_URL
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()
    if 'DATABASE_URL' in app_content and 'postgresql' in app_content:
        print("✓ app.py có kết nối PostgreSQL")
        
        # Extract DATABASE_URL
        match = re.search(r'postgresql://.*?(?=",|\')', app_content)
        if match:
            db_url = match.group(0)
            print(f"  DB: {db_url}")
    else:
        print("✗ app.py không kết nối database")

# Check if coordinator is imported
if 'from agents.coordinator import coordinator' in app_content:
    print("✓ /submit endpoint import coordinator")
else:
    print("✗ /submit endpoint không import coordinator")

print("\n" + "="*70)
print("2. KIỂM TRA ENDPOINTS CHẤM ĐIỂM")
print("="*70)

# Count endpoints
endpoints = re.findall(r'@app\.(post|get|put|delete)\("([^"]+)"', app_content)
print(f"✓ Có {len(endpoints)} endpoints")
for method, path in endpoints[:10]:
    print(f"  [{method.upper()}] {path}")

print("\n" + "="*70)
print("3. KIỂM TRA AGENTS")
print("="*70)

agents_to_check = [
    'agents/syntax_agent_fixed.py',
    'agents/requirement_agent_fixed.py',
    'agents/structure_agent_fixed.py',
    'agents/test_agent_fixed.py',
    'agents/llm_agent.py',
    'agents/aggregation_agent_fixed.py',
    'agents/coordinator.py',
]

for agent_file in agents_to_check:
    if os.path.exists(agent_file):
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if agent reads from DB
        has_db = 'psycopg2' in content or 'SELECT' in content
        # Check if agent has main function (fixed modules expose def syntax_agent, not def syntax_agent_fixed)
        base_name = agent_file.split('/')[-1].replace('.py', '')
        func_name = base_name[:-6] if base_name.endswith('_fixed') else base_name
        has_func = f'def {func_name}' in content

        print(f"\n✓ {agent_file}")
        print(f"  Has DB: {'✓' if has_db else '✗'}")
        print(f"  Has {func_name}(): {'✓' if has_func else '✗'}")
        
        # Count lines
        line_count = len(content.split('\n'))
        print(f"  Lines: {line_count}")
        
    else:
        print(f"✗ {agent_file} NOT FOUND!")

print("\n" + "="*70)
print("4. KIỂM TRA DATABASE TABLES")
print("="*70)

tables_to_check = [
    'assignments',
    'assignment_requirements',
    'assignment_testcases',
    'submissions',
    'evaluation_sessions',
    'agent_logs'
]

# Check if app.py references these tables
for table in tables_to_check:
    if f'"{table}"' in app_content or f"'{table}'" in app_content:
        print(f"✓ {table} - referenced in code")
    else:
        print(f"? {table} - check if used")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("Run more detailed checks...")
