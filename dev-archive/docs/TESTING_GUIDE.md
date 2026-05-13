# Quick Testing Guide - Login Backend

## Setup Database

1. Create PostgreSQL database:
```sql
CREATE DATABASE MAS_Programming_Assessment;
```

2. Run seed data:
```bash
psql -U postgres MAS_Programming_Assessment < seed_test_data.sql
```

3. Verify data was loaded:
```bash
psql -U postgres MAS_Programming_Assessment -c "SELECT * FROM teachers;"
psql -U postgres MAS_Programming_Assessment -c "SELECT * FROM students;"
```

## Start Server

```bash
# Install dependencies (if not installed)
pip install -r requirements.txt

# Run FastAPI server (default: http://localhost:8000)
uvicorn app:app --reload
```

## Test Login Flow

### 1. **Admin/Debug - Check All Users**
```bash
curl http://localhost:8000/debug/users | python -m json.tool
```

Expected Output:
```json
{
  "teachers_count": 1,
  "students_count": 2,
  "teachers": [
    {
      "teacher_id": 1,
      "username": "teacher1",
      "email": "teacher1@example.com",
      "full_name": "Nguyen Van A"
    }
  ],
  "students": [
    {
      "student_id": 1,
      "username": "student1",
      "email": "student1@example.com",
      "full_name": "Tran Van B"
    },
    {
      "student_id": 2,
      "username": "student2",
      "email": "student2@example.com",
      "full_name": "Le Thi C"
    }
  ]
}
```

### 2. **Test Teacher Login**
```bash
curl -X POST http://localhost:8000/login \
  -d "role=teacher&email=teacher1@example.com&password=123456" \
  -c cookies.txt \
  -L
```

Will redirect to `/teacher-dashboard` (HTTP 303)

### 3. **Test Student Login**
```bash
curl -X POST http://localhost:8000/login \
  -d "role=student&email=student1@example.com&password=123456" \
  -c cookies.txt \
  -L
```

Will redirect to `/student-dashboard` (HTTP 303)

### 4. **Test Remember Me Option**
```bash
curl -X POST http://localhost:8000/login \
  -d "role=student&email=student1@example.com&password=123456&remember=on" \
  -c cookies_remember.txt \
  -L
```

The `remember_me` cookie will be set for 30 days.

### 5. **Check Current User (After Login)**
```bash
# Using cookies from login
curl http://localhost:8000/api/current-user -b cookies.txt | python -m json.tool
```

Expected Output:
```json
{
  "user_id": 1,
  "role": "student",
  "full_name": "Tran Van B"
}
```

### 6. **Test Logout**
```bash
curl -X GET http://localhost:8000/logout \
  -b cookies.txt \
  -L
```

Will redirect to `/` and clear all cookies

### 7. **Test Error Handling**

**Invalid Role:**
```bash
curl -X POST http://localhost:8000/login \
  -d "role=admin&email=student1@example.com&password=123456"
# Response: 400 "Vai trò không hợp lệ"
```

**Wrong Email:**
```bash
curl -X POST http://localhost:8000/login \
  -d "role=student&email=nonexistent@example.com&password=123456"
# Response: 401 "Email không tồn tại"
```

**Wrong Password:**
```bash
curl -X POST http://localhost:8000/login \
  -d "role=student&email=student1@example.com&password=wrongpass"
# Response: 401 "Sai mật khẩu"
```

**Access Protected Route Without Login:**
```bash
curl http://localhost:8000/api/current-user
# Response: 401 "Chưa đăng nhập"
```

## Browser Testing

### Manual Steps:
1. Open http://localhost:8000 in browser
2. Choose role (Teacher or Student)
3. Enter email: `student1@example.com`
4. Enter password: `123456`
5. Optional: Check "Ghi nhớ" (Remember Me)
6. Click "Đăng nhập" (Login)
7. Should redirect to dashboard

### Inspect Cookies (Chrome DevTools):
1. Open DevTools (F12)
2. Go to Application → Cookies → localhost:8000
3. Look for: `user_id`, `role`, `full_name`, `remember_me` (if checked)

## Password Testing

**Current Status:** Passwords in seed data (`123456`) are stored as plain text.

**To use bcrypt hashing:**
```python
import bcrypt

# Generate hash
password = "123456"
hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(hash)  # Store this in password_hash column

# Update database
# UPDATE teachers SET password_hash = '<hash>' WHERE teacher_id = 1;
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "Cannot connect to PostgreSQL"
- Check DATABASE_URL in app.py
- Verify PostgreSQL is running
- Check credentials (default: `postgres:123456@localhost:5432`)

### "Table doesn't exist"
- Run `seed_test_data.sql`: `psql -U postgres MAS_Programming_Assessment < seed_test_data.sql`

### Cookies not persisting
- Check browser privacy settings
- Ensure cookies are not being blocked
- Use `-c` flag with curl to save cookies: `curl ... -c cookies.txt`

## Email Case Sensitivity Test

```bash
# These should all work (thanks to LOWER() in SQL):
curl -X POST http://localhost:8000/login \
  -d "role=student&email=student1@example.com&password=123456"

curl -X POST http://localhost:8000/login \
  -d "role=student&email=STUDENT1@EXAMPLE.COM&password=123456"

curl -X POST http://localhost:8000/login \
  -d "role=student&email=Student1@Example.Com&password=123456"
```

All variations should successfully login.

---

**Last Updated:** 2026-03-24
**Backend Framework:** FastAPI + PostgreSQL
**Status:** ✅ Ready for testing
