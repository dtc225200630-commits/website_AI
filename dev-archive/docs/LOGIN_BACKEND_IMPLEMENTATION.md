# Backend Implementation: Login (Đăng nhập)

## Overview
Implemented the backend for the login page (`dangnhap.html`) using FastAPI and PostgreSQL, with support for both **Teacher (Giảng viên)** and **Student (Sinh viên)** authentication.

## Database Schema Used
- **teachers** table: Contains teacher accounts with fields `teacher_id`, `username`, `email`, `password_hash`, `full_name`
- **students** table: Contains student accounts with fields `student_id`, `username`, `email`, `password_hash`, `full_name`
- **classes** table: Links teachers to classes
- **enrollments** table: Links students to classes

### Sample Data  
From `seed_test_data.sql`:
```sql
-- Teacher
INSERT INTO teachers (username, password_hash, full_name, email)
VALUES ('teacher1', '123456', 'Nguyen Van A', 'teacher1@example.com');

-- Students
INSERT INTO students (username, password_hash, full_name, email)
VALUES 
('student1', '123456', 'Tran Van B', 'student1@example.com'),
('student2', '123456', 'Le Thi C', 'student2@example.com');
```

## API Endpoints

### 1. **POST /login** - Login
**Purpose:** Authenticate user and create session via cookies

**Request Parameters:**
```json
{
  "role": "teacher" or "student",
  "email": "user@example.com",
  "password": "password123",
  "remember": true/false (optional)
}
```

**Responses:**
- **Success (303):** Redirects to dashboard with session cookies set
  - `user_id`: User's ID (httponly)
  - `role`: "teacher" or "student" (httponly)
  - `full_name`: User's full name
  - `remember_me`: Set for 30 days if "remember" checked (optional)

- **Errors:**
  - `400`: Invalid role (must be "teacher" or "student")
  - `401`: Email not found or wrong password
  - `500`: Server error

**Example:**
```bash
curl -X POST http://localhost:8000/login \
  -d "role=student&email=student1@example.com&password=123456&remember=true"
```

---

### 2. **GET /logout** - Logout
**Purpose:** Clear session and redirect to homepage

**Response:** Redirects to "/" with all cookies deleted

**Cookies Deleted:**
- `user_id`
- `role`
- `full_name`
- `remember_me`

---

### 3. **GET /api/current-user** - Get Current User
**Purpose:** Retrieve logged-in user's information

**Response (200):**
```json
{
  "user_id": 1,
  "role": "student",
  "full_name": "Tran Van B"
}
```

**Errors:**
- `401`: User not logged in (missing cookies)

---

## Implementation Details

### Authentication Flow
1. Form submission from `dangnhap.html` to `POST /login`
2. Select appropriate table based on `role` parameter:
   - `role = "teacher"` → query `teachers` table
   - `role = "student"` → query `students` table
3. Find user by email (case-insensitive)
4. Verify password using `_verify_password()` function
5. Set session cookies and redirect to appropriate dashboard:
   - Teachers → `/teacher-dashboard` (displays `tranggiaovien.html`)
   - Students → `/student-dashboard` (displays `bangdkSV.html`)

### Security Features
- **Password Verification:** Uses bcrypt (with fallback to plain text if DB hasn't been hashed yet)
  ```python
  def _verify_password(plain_password: str, hashed_password: str) -> bool:
      try:
          return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
      except:
          return plain_password == hashed_password
  ```

- **Email Case-Insensitive:** Uses `LOWER()` in SQL to match emails regardless of case
- **HttpOnly Cookies:** `user_id` and `role` marked as httponly to prevent XSS attacks
- **Extended Session Option:** "Remember me" checkbox sets 30-day cookie expiration

### Bug Fixes Applied
Fixed references to non-existent `users` table throughout the application:
1. **Login endpoint** - Now queries `teachers` or `students` based on role
2. **_fetch_assignments()** - Changed `LEFT JOIN users u` to `LEFT JOIN teachers t`
3. **assignment_submission_page()** - Changed `LEFT JOIN users u` to `LEFT JOIN teachers t`
4. **submission_result_page()** - Changed `JOIN users u` to `JOIN students st`
5. **debug_users()** - Now returns both teachers and students separately

## Testing

### Test Credentials (from seed_test_data.sql)
```
Teacher:
  Email: teacher1@example.com
  Password: 123456
  Role: teacher

Student 1:
  Email: student1@example.com
  Password: 123456
  Role: student

Student 2:
  Email: student2@example.com
  Password: 123456
  Role: student
```

### Test with cURL
```bash
# Test teacher login
curl -X POST http://localhost:8000/login -L \
  -d "role=teacher&email=teacher1@example.com&password=123456"

# Test student login
curl -X POST http://localhost:8000/login -L \
  -d "role=student&email=student1@example.com&password=123456"

# Check current user (with cookies)
curl http://localhost:8000/api/current-user \
  --cookie "user_id=1; role=student; full_name=Tran%20Van%20B"

# Debug endpoint - view all users
curl http://localhost:8000/debug/users
```

## Frontend Integration

The form in `dangnhap.html` should POST to `/login` with:
- `role` radio button (selected by user)
- `email` text input
- `password` password input
- `remember` checkbox (optional)

After successful login, user is redirected to their dashboard based on role.
For logout, add a link/button to `/logout`.

## Future Enhancements
1. Hash passwords in database using bcrypt before storing
2. Add CSRF protection with tokens
3. Implement JWT for stateless authentication instead of cookies
4. Add login attempt rate limiting
5. Add email verification for new accounts
6. Add password reset functionality
7. Add 2FA (two-factor authentication)

---

**Created:** 2026-03-24
**Status:** ✅ Working (tested with sample data)
