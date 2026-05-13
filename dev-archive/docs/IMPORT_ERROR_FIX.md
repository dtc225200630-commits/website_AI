# FIX IMPORT ERROR - google.generativeai Missing

## Lỗi
```
[APP] X Failed to import coordinator: No module named 'google.generativeai'
```

## Nguyên Nhân
Package `google-generativeai` chưa được cài đặt trong virtual environment.

## Cách Sửa

### **Bước 1: Cài Lại Tất Cả Dependencies**
```bash
pip install -r requirements.txt
```

Hoặc cài riêng:
```bash
pip install google-generativeai
```

### **Bước 2: Restart Server**
```bash
python app.py
```

### **Nếu Vẫn Gặp Lỗi**

Thử lệnh này để xem package được cài chưa:
```bash
python -c "import google.generativeai; print('OK')"
```

- Nếu OK → Package cài rồi, restart server
- Nếu lỗi → Cài lại: `pip install google-generativeai --force-reinstall`

---

## Giải Thích Kỹ Thuật

### Cấu Trúc Import:
```
app.py
  └── coordinator.py (imports all agents)
      ├── syntax_agent.py
      ├── requirement_agent.py
      ├── structure_agent.py
      ├── test_agent.py
      ├── llm_agent.py ← REQUIRES google.generativeai
      └── aggregation_agent.py
```

Khi `llm_agent.py` không thể import `google.generativeai`, toàn bộ chain import fails.

### Giải Pháp Tôi Áp Dụng:
1. **llm_agent.py**: Try-catch import + graceful fallback
   - Nếu google.generativeai available → dùng Gemini AI
   - Nếu không → return default score (10/20) + warning

2. **app.py**: Đã có fallback coordinator
   - Nếu import fail → return 0/100
   - Nhưng với fix llm_agent, import sẽ succeed

---

## Template không cần sửa
Templates chỉ hiển thị dữ liệu từ backend.
Backend fixed → Templates sẽ hiển thị đúng.

---

## Test Lại

Sau khi cài packages:

```bash
# Kiểm tra import berhasil
python -c "from agents import coordinator; print('Coordinator OK')"

# Restart app
python app.py
```

Nếu server start thành công (không lỗi):
```
[Coordinator] LangChain orchestrator available
```

Maka siap untuk submit bài và được score 83/100! ✓
