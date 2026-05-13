# Code Reference - Login Backend Implementation

## File: app.py - Login Routes

### 1. Login Route (POST /login)

```python
@app.post("/login")
async def login(
    role: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(default=False)
):
    """
    Xử lý đăng nhập cho cả Giảng viên và Sinh viên
    - role: "teacher" hoặc "student"
    - email: email đăng nhập
    - password: mật khẩu
    - remember: tùy chọn ghi nhớ
    """
    # Trim khoảng trắng + lowercase để so sánh
    email = email.strip().lower()
    
    # Kiểm tra vai trò hợp lệ
    if role not in ["teacher", "student"]:
        raise HTTPException(status_code=400, detail="Vai trò không hợp lệ")
    
    # Chọn bảng dựa trên vai trò
    table = "teachers" if role == "teacher" else "students"
    
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Dùng LOWER() để so sánh không phân biệt hoa/thường
                cur.execute(
                    f"SELECT {role[0]}_id, password_hash, full_name FROM {table} WHERE LOWER(email) = %s",
                    (email,)
                )
                row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="Email không tồn tại")

        user_id, password_hash, full_name = row

        # Kiểm tra mật khẩu
        if not _verify_password(password, password_hash):
            raise HTTPException(status_code=401, detail="Sai mật khẩu")

        # Chuyển hướng + set cookie để trang dashboard biết user hiện tại
        if role == "teacher":
            response = RedirectResponse(url="/teacher-dashboard", status_code=303)
        else:
            response = RedirectResponse(url="/student-dashboard", status_code=303)

        # Set cookies
        response.set_cookie(key="user_id", value=str(user_id), httponly=True)
        response.set_cookie(key="role", value=role, httponly=True)
        response.set_cookie(key="full_name", value=full_name or "User", httponly=False)
        
        # Tùy chọn "ghi nhớ" - tăng thời gian sống của cookie
        if remember:
            response.set_cookie(key="remember_me", value="true", httponly=True, max_age=30*24*60*60)
        
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý đăng nhập: {str(e)}")
```

### 2. Logout Route (GET /logout)

```python
@app.get("/logout")
async def logout():
    """Đăng xuất - xóa các cookies"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="user_id")
    response.delete_cookie(key="role")
    response.delete_cookie(key="full_name")
    response.delete_cookie(key="remember_me")
    return response
```

### 3. Current User Route (GET /api/current-user)

```python
@app.get("/api/current-user")
async def get_current_user(request: Request):
    """Lấy thông tin người dùng hiện tại từ cookies"""
    user_id = request.cookies.get("user_id")
    role = request.cookies.get("role")
    full_name = request.cookies.get("full_name")
    
    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    return {
        "user_id": int(user_id) if user_id else None,
        "role": role,
        "full_name": full_name or "User"
    }
```

---

## Helper Functions

### Password Verification Function

```python
def _verify_password(plain_password: str, hashed_password: str) -> bool:
    # Lưu ý: Pass trong DB nên được hash bằng bcrypt. 
    # Nếu đang để text thuần để test thì dùng: return plain_password == hashed_password
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except:
        return plain_password == hashed_password # Chống cháy nếu DB chưa hash
```

### Fixed Fetch Assignments

```python
def _fetch_assignments(conn, student_id: int | None):
    base_select = """
        SELECT
            a.assignment_id,
            a.title,
            a.description,
            a.due_date,
            a.programming_language,
            c.class_id,
            c.class_name,
            t.full_name AS teacher_name
        FROM assignments a
        JOIN classes c ON c.class_id = a.class_id
        LEFT JOIN teachers t ON t.teacher_id = c.teacher_id
    """

    params = []
    where_clause = ""
    if student_id is not None:
        where_clause = "WHERE a.class_id IN (SELECT e.class_id FROM enrollments e WHERE e.student_id = %s)"
        params.append(student_id)

    order_clause = "ORDER BY a.due_date ASC"
    query = "\n".join([base_select, where_clause, order_clause])

    with conn.cursor() as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        assignments = _rows_to_dicts(cur, rows)

    return [_decorate_assignment(a) for a in assignments]
```

---

## Important Changes Made

### 1. Query Changes

**Before (Broken):**
```python
cur.execute(
    "SELECT user_id, password_hash, role FROM users WHERE LOWER(email) = %s",
    (email,)
)
```

**After (Fixed):**
```python
table = "teachers" if role == "teacher" else "students"
cur.execute(
    f"SELECT {role[0]}_id, password_hash, full_name FROM {table} WHERE LOWER(email) = %s",
    (email,)
)
```

### 2. Join Changes

**Before (Assignment Page):**
```python
LEFT JOIN users u ON u.user_id = c.teacher_id
```

**After:**
```python
LEFT JOIN teachers t ON t.teacher_id = c.teacher_id
```

**Before (Submission Result):**
```python
JOIN users u ON u.user_id = s.student_id
```

**After:**
```python
JOIN students st ON st.student_id = s.student_id
```

---

## Required Imports

Ensure these are at the top of app.py:

```python
import os
import bcrypt
import psycopg2
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import contextmanager
```

---

## Environment Configuration

### DATABASE_URL

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123456@localhost:5432/MAS_Programming_Assessment",
)
```

Change credentials as needed:
- `postgres` → PostgreSQL username
- `123456` → PostgreSQL password
- `localhost:5432` → PostgreSQL host:port
- `MAS_Programming_Assessment` → Database name

### .env File (Optional)

Create `.env` file in project root:
```
DATABASE_URL=postgresql://postgres:123456@localhost:5432/MAS_Programming_Assessment
```

---

## Form HTML (dangnhap.html)

```html
<form class="space-y-6" action="/login" method="post">
  <!-- Role Selection -->
  <div class="grid grid-cols-2 gap-4">
    <label>
      <input checked="" class="peer sr-only" name="role" type="radio" value="teacher"/>
      <div class="flex flex-col items-center gap-2 p-4 rounded-lg border-2 
                  border-transparent bg-surface-container-low 
                  peer-checked:border-primary peer-checked:bg-primary-fixed-dim/20">
        <span class="material-symbols-outlined">school</span>
        <span class="text-sm font-medium">Giảng viên</span>
      </div>
    </label>
    <label>
      <input class="peer sr-only" name="role" type="radio" value="student"/>
      <div class="flex flex-col items-center gap-2 p-4 rounded-lg border-2 
                  border-transparent bg-surface-container-low 
                  peer-checked:border-primary peer-checked:bg-primary-fixed-dim/20">
        <span class="material-symbols-outlined">person</span>
        <span class="text-sm font-medium">Sinh viên</span>
      </div>
    </label>
  </div>

  <!-- Email Input -->
  <div class="relative">
    <label class="block text-xs font-semibold text-on-surface-variant mb-1 
                   uppercase tracking-wider ml-1">Email</label>
    <input class="w-full bg-surface-container-low border-b-2 border-surface-variant 
                   focus:border-primary focus:ring-0 transition-all px-4 py-3 
                   rounded-t-lg outline-none text-on-surface" 
           placeholder="example@university.edu.vn" type="email" name="email" required/>
  </div>

  <!-- Password Input -->
  <div class="relative">
    <label class="block text-xs font-semibold text-on-surface-variant mb-1 
                   uppercase tracking-wider ml-1">Mật khẩu</label>
    <input class="w-full bg-surface-container-low border-b-2 border-surface-variant 
                   focus:border-primary focus:ring-0 transition-all px-4 py-3 
                   rounded-t-lg outline-none text-on-surface" 
           placeholder="••••••••" type="password" name="password" required/>
  </div>

  <!-- Remember Me -->
  <div class="flex items-center gap-2">
    <input class="rounded border-outline-variant text-primary focus:ring-primary" 
           type="checkbox" name="remember"/>
    <span class="text-on-surface-variant text-sm">Ghi nhớ</span>
  </div>

  <!-- Submit Button -->
  <button class="w-full bg-primary hover:bg-primary-container text-on-primary 
                  font-bold py-4 rounded-lg shadow-lg active:scale-95 
                  transition-all duration-200 flex items-center justify-center gap-2" 
          type="submit">
    <span>Đăng nhập</span>
    <span class="material-symbols-outlined text-sm">login</span>
  </button>
</form>
```

---

## SQL Sample Data (seed_test_data.sql)

```sql
-- Teachers
INSERT INTO teachers (username, password_hash, full_name, email)
VALUES ('teacher1', '123456', 'Nguyen Van A', 'teacher1@example.com');

-- Students
INSERT INTO students (username, password_hash, full_name, email)
VALUES
('student1', '123456', 'Tran Van B', 'student1@example.com'),
('student2', '123456', 'Le Thi C', 'student2@example.com');

-- Classes
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES ('Lap trinh Python KTPM', 1, 'HK1', '2025-2026');

-- Enrollments
INSERT INTO enrollments (class_id, student_id)
VALUES (1, 1), (1, 2);
```

---

## Testing Command Examples

### Test Teacher Login
```bash
curl -X POST http://localhost:8000/login \
  -d "role=teacher&email=teacher1@example.com&password=123456"
```

### Test Student Login
```bash
curl -X POST http://localhost:8000/login \
  -d "role=student&email=student1@example.com&password=123456"
```

### Check Current User
```bash
curl http://localhost:8000/api/current-user \
  -H "Cookie: user_id=1; role=student"
```

### Logout
```bash
curl http://localhost:8000/logout
```

### View All Users (Debug)
```bash
curl http://localhost:8000/debug/users | python -m json.tool
```

---

## Requirements.txt

```
fastapi==0.115.0
uvicorn==0.30.6
psycopg2-binary==2.9.9
bcrypt==4.1.3
jinja2==3.1.4
python-multipart==0.0.9
```

---

## Running the Application

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database
createdb MAS_Programming_Assessment
psql -U postgres MAS_Programming_Assessment < seed_test_data.sql

# 3. Run server
uvicorn app:app --reload

# 4. Open browser
# http://localhost:8000
```

---

**Last Updated:** 2026-03-24
**Framework:** FastAPI + PostgreSQL
**Status:** ✅ Ready for use
