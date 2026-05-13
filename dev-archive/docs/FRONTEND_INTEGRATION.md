# Frontend Integration Guide - Login Page

## Current Form Structure

The `dangnhap.html` login form is already properly configured to work with the backend.

### Form HTML
```html
<form class="space-y-6" action="/login" method="post">
  <!-- Role Selection (required) -->
  <input checked="" name="role" type="radio" value="teacher"/>
  <input name="role" type="radio" value="student"/>
  
  <!-- Email Input (required) -->
  <input name="email" type="email" placeholder="example@university.edu.vn" required/>
  
  <!-- Password Input (required) -->
  <input name="password" type="password" placeholder="••••••••" required/>
  
  <!-- Remember Me Checkbox (optional) -->
  <input name="remember" type="checkbox"/>
  
  <!-- Submit Button -->
  <button type="submit">Đăng nhập</button>
</form>
```

## Field Mapping

| HTML Field | Backend Parameter | Type | Required | Notes |
|-----------|------------------|------|----------|-------|
| `name="role"` | role | string | ✅ Yes | Must be "teacher" or "student" |
| `name="email"` | email | string | ✅ Yes | Must be valid email format |
| `name="password"` | password | string | ✅ Yes | Case-sensitive |
| `name="remember"` | remember | boolean | ❌ No | Extends session to 30 days |

## Backend Integration Details

### Form Submission Flow

```
User fills form with:
├─ Role: "student" (selected radio)
├─ Email: "student1@example.com"
├─ Password: "123456"
└─ Remember: checked (optional)
    ↓
POST /login
    ↓
Compare with database
    ├─ Check email in "students" table
    ├─ Verify password_hash
    └─ If valid → set cookies + redirect
    ↓
Redirect to /student-dashboard (HTTP 303)
    ↓
Dashboard receives cookies:
├─ user_id=1 (httponly)
├─ role=student (httponly)
├─ full_name=Tran Van B
└─ remember_me=true (optional, 30 days)
```

## Response Handling

### Success Response
- **Status:** 303 (See Other / Redirect)
- **Location Header:** 
  - `/teacher-dashboard` (if role = "teacher")
  - `/student-dashboard` (if role = "student")
- **Cookies Set:** user_id, role, full_name, (remember_me if checked)

### Error Responses
```javascript
// Invalid role
{
  "detail": "Vai trò không hợp lệ"
  // (400 Bad Request)
}

// Email not found
{
  "detail": "Email không tồn tại"
  // (401 Unauthorized)
}

// Wrong password
{
  "detail": "Sai mật khẩu"
  // (401 Unauthorized)
}

// Server error
{
  "detail": "Lỗi xử lý đăng nhập: [error details]"
  // (500 Internal Server Error)
}
```

## JavaScript Enhancement (Optional)

### Add Client-Side Validation

```html
<script>
document.querySelector('form').addEventListener('submit', async (e) => {
  const role = document.querySelector('input[name="role"]:checked')?.value;
  const email = document.querySelector('input[name="email"]').value;
  const password = document.querySelector('input[name="password"]').value;
  
  // Basic validation
  if (!role || !email || !password) {
    e.preventDefault();
    alert('Vui lòng điền đầy đủ thông tin');
    return false;
  }
  
  // Email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    e.preventDefault();
    alert('Email không hợp lệ');
    return false;
  }
  
  // Optional: Show loading state
  const submitBtn = document.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Đang đăng nhập...';
});
</script>
```

### Add Loading Indicator

```html
<button class="loading-btn" type="submit">
  <span class="btn-text">Đăng nhập</span>
  <span class="material-symbols-outlined loading-icon" style="display:none">
    hourglass_bottom
  </span>
</button>

<style>
  .loading-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .loading-btn:disabled .loading-icon {
    display: inline-block !important;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>
```

## Post-Login Navigation

### Access Current User Info (in Dashboard Pages)

```html
<!-- Add this script in tranggiaovien.html or bangdkSV.html -->
<script>
fetch('/api/current-user')
  .then(res => {
    if (res.status === 401) {
      // Not logged in, redirect to login
      window.location.href = '/';
      return;
    }
    return res.json();
  })
  .then(user => {
    // Update page with user info
    document.querySelector('.user-name').textContent = user.full_name;
    document.querySelector('.user-role').textContent = 
      user.role === 'teacher' ? 'Giảng viên' : 'Sinh viên';
  });
</script>
```

### Logout Button

```html
<a href="/logout" class="logout-btn">Đăng xuất</a>
```

## Cookie Management

### View Cookies in Browser Console

```javascript
// Get all cookies
console.log(document.cookie);

// Get specific cookie
const userRole = document.cookie
  .split('; ')
  .find(row => row.startsWith('role='))
  ?.split('=')[1];

console.log('Current role:', userRole);
```

### Note: HttpOnly Cookies
The `user_id` and `role` cookies are marked as `httponly`, which means:
- ✅ They are automatically sent with every request to the server
- ❌ They cannot be accessed via JavaScript (`document.cookie`)
- ✅ They are protected from XSS attacks

The `full_name` and `remember_me` cookies are not httponly, so they can be accessed if needed:

```javascript
const fullName = getCookie('full_name');

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}
```

## Security Best Practices for Frontend

1. **Use HTTPS in Production**
   - Cookies should only be sent over encrypted connections
   - Set `secure` flag on cookies (FastAPI can do this)

2. **CSRF Protection**
   - Add CSRF tokens to forms if needed
   - FastAPI can use middleware for this

3. **XSS Prevention**
   - Sanitize any user input displayed on page
   - Jinja2 templates auto-escape by default (safe)

4. **Password Field**
   - Never autocomplete or remember passwords in form
   - Use `autocomplete="current-password"` for best practices

```html
<input 
  name="password" 
  type="password" 
  autocomplete="current-password"
  placeholder="••••••••" 
  required
/>
```

## Testing the Integration

### Manual Test Flow

1. **Open Login Page**
   ```
   http://localhost:8000/
   ```

2. **Select Role** (default is "teacher")
   - Click "Sinh viên" (Student) radio button

3. **Enter Credentials**
   - Email: `student1@example.com`
   - Password: `123456`
   - Check: "Ghi nhớ" (Remember Me)

4. **Submit Form**
   - Should redirect to `/student-dashboard`
   - Page should load student dashboard

5. **Verify Session**
   - DevTools → Application → Cookies
   - Should see: `user_id=1`, `role=student`, `full_name=Tran Van B`, `remember_me=true`

6. **Test Logout**
   - Click logout button
   - Should return to `/`
   - Cookies should be cleared

### API Test with JavaScript Fetch

```javascript
// Simulate form submission with fetch
const formData = new FormData();
formData.append('role', 'student');
formData.append('email', 'student1@example.com');
formData.append('password', '123456');
formData.append('remember', 'on');

fetch('/login', {
  method: 'POST',
  body: formData,
  credentials: 'include', // Important: to manage cookies
  redirect: 'follow'
})
.then(res => {
  if (res.ok) {
    console.log('Login successful');
    // The redirect will be followed automatically
  } else {
    console.error('Login failed:', res.status);
  }
})
.catch(err => console.error('Error:', err));
```

## Troubleshooting

### Form not submitting
- Check that `<form>` has `action="/login"` and `method="post"`
- Verify browser allows form submission
- Check browser console for JavaScript errors

### Always redirects to login
- Check if cookies are being blocked
- Verify database connection is working
- Check browser privacy settings

### Form data not reaching backend
- Check HTTP method is POST
- Verify form field names match backend parameters
- Use DevTools Network tab to inspect POST request

### Session lost on page refresh
- Cookies might be expiring
- Check `remember_me` functionality if enabled
- Use browser DevTools to verify cookies are persisted

---

**Last Updated:** 2026-03-24
**Status:** ✅ Ready for integration
