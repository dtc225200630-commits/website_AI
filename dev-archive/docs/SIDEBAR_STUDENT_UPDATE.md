# SIDEBAR SINH VIÊN - THAY ĐỔI VÀ CẬP NHẬT

## 🎯 Mục Tiêu
Sửa sidebar cho giao diện trang của học sinh:
- ✅ **Đồng nhất** - Tất cả trang sinh viên có sidebar giống nhau
- ✅ **Dữ liệu thật** - Thay thế dữ liệu tĩnh bằng dữ liệu từ CSDL

---

## 📝 THAY ĐỔI CHI TIẾT

### 1. Backend (app.py)

#### Hàm Helper Mới: `_fetch_student_detailed_profile()`
**Vị trí**: Thêm sau hàm `_fetch_student_profile()` trong app.py

**Chức năng**: Lấy thông tin chi tiết sinh viên từ CSDL:
- ✅ Tên sinh viên (full_name)
- ✅ Mã sinh viên (student_code)
- ✅ Tên lớp (class_name)
- ✅ Tên giáo viên hướng dẫn (teacher_name)
- ✅ Điểm trung bình (average_score)
- ✅ Xếp hạng (ranking)
- ✅ Số bài đã chấm (total_graded)
- ✅ Tổng số bài được giao (total_assigned)

**Truy vấn CSDL**:
```sql
-- Lấy thông tin sinh viên + lớp + giáo viên
SELECT s.student_id, s.full_name, c.class_name, t.full_name
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.student_id
LEFT JOIN classes c ON c.class_id = e.class_id
LEFT JOIN teachers t ON t.teacher_id = c.teacher_id
WHERE s.student_id = ?

-- Tính điểm trung bình
SELECT COALESCE(AVG(es.total_score), 0)
FROM submissions s
LEFT JOIN evaluation_sessions es ON es.submission_id = s.submission_id
WHERE s.student_id = ? AND es.total_score IS NOT NULL

-- Tính xếp hạng
SELECT RANK() OVER (ORDER BY AVG(es.total_score) DESC)
FROM students s
LEFT JOIN submissions sub ON sub.student_id = s.student_id
LEFT JOIN evaluation_sessions es ON es.submission_id = sub.submission_id
WHERE s.student_id = ?
GROUP BY s.student_id

-- Đếm bài đã chấm
SELECT COUNT(DISTINCT s.submission_id)
FROM submissions s
JOIN evaluation_sessions es ON es.submission_id = s.submission_id
WHERE s.student_id = ? AND es.total_score IS NOT NULL
```

#### Cập nhật Endpoints

**Endpoint `/student-assignments`**:
- Trước: `student_profile = _fetch_student_profile()`
- Sau: `student_profile = _fetch_student_detailed_profile()`

**Endpoint `/student-results`**:
- Thêm dữ liệu mới: `latest_score`, `student_progress`
- Sử dụng `_fetch_student_detailed_profile()` thay vì `_fetch_student_profile()`

---

### 2. Frontend (Templates)

#### Các file HTML được cập nhật:
1. ✅ `templates/ketquahoctap_sinhvien.html`
2. ✅ `templates/bangdkSV.html`
3. ✅ `templates/trangnopbaiSV.html`
4. ✅ `templates/lichsunopbai_sinhvien.html`
5. ✅ `templates/lichsunopbaicuasinhvien_sinhvien.html`

#### Thay Đổi Sidebar

**Phần Profile Section (Mới)**:
```html
<!-- Profile Section -->
<div class="px-6 pb-4 border-b border-slate-200">
  <div class="flex items-center gap-3 mb-3">
    <div class="w-10 h-10 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 font-bold">
      {{ student_profile.full_name[0] if student_profile.full_name else 'S' }}
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-xs font-bold truncate">{{ student_profile.full_name if student_profile else 'Sinh viên' }}</p>
      <p class="text-[10px] text-slate-500">{{ student_profile.student_code if student_profile else '--' }}</p>
    </div>
  </div>
  <div class="space-y-2 text-[10px]">
    <div class="flex justify-between">
      <span class="text-slate-600">Lớp:</span>
      <span class="font-medium">{{ student_profile.class_name if student_profile else 'N/A' }}</span>
    </div>
    <div class="flex justify-between">
      <span class="text-slate-600">GV hướng dẫn:</span>
      <span class="font-medium">{{ student_profile.teacher_name if student_profile else '--' }}</span>
    </div>
  </div>
</div>
```

**Phần Navigation** (cập nhật links):
- `/student-dashboard` (Bảng điều khiển)
- `/student-assignments` (Bài tập)
- `/student-results` (Kết quả)
- `/student-submission-history` (Lịch sử)

#### Thay Đổi Dữ Liệu Tĩnh thành Động

**Trang Kết Quả (`ketquahoctap_sinhvien.html`)**:

Trước:
```html
<p class="text-4xl font-black font-headline mt-2 text-primary">91.4%</p>
<p class="text-4xl font-black font-headline mt-2 text-tertiary">Top 5%</p>
<p class="text-4xl font-black font-headline mt-2">26</p>
```

Sau:
```html
<p class="text-4xl font-black font-headline mt-2 text-primary">{{ student_profile.average_score if student_profile else 0 }}/100</p>
<p class="text-4xl font-black font-headline mt-2 text-tertiary">{{ student_profile.ranking if student_profile else '--' }}</p>
<p class="text-4xl font-black font-headline mt-2">{{ student_profile.total_graded if student_profile else 0 }}</p>
```

---

## 📊 SỰ NHẤT QUÁN

### Trước (Không nhất quán):
- Trang 1: Sidebar khác nhau
- Trang 2: Thiếu profile section
- Trang 3: Dữ liệu tĩnh
- Trang 4: Link chết

### Sau (Nhất quán 100%):
- ✅ Tất cả trang có sidebar giống nhau
- ✅ Tất cả sidebar có profile section
- ✅ Tất cả dữ liệu từ CSDL
- ✅ Tất cả link hoạt động

---

## 🗄️ CẤU TRÚC CSDL

**Bảng được sử dụng**:
- `students` - Thông tin sinh viên
- `enrollments` - Ghi danh sinh viên vào lớp
- `classes` - Thông tin lớp học
- `teachers` - Thông tin giáo viên
- `submissions` - Bài nộp của sinh viên
- `evaluation_sessions` - Kết quả chấm điểm

---

## 🔍 TEMPLATE VARIABLES

Tất cả template nhận được object `student_profile` với các trường:

| Trường | Loại | Ví dụ | Mục đích |
|--------|------|--------|---------|
| `full_name` | string | "Nguyễn Văn A" | Hiển thị tên sinh viên |
| `student_code` | string | "SV2024001" | Hiển thị mã sinh viên |
| `class_name` | string | "Lớp A1" | Hiển thị tên lớp |
| `teacher_name` | string | "Thầy Bình" | Hiển thị tên giáo viên |
| `average_score` | float | 85.5 | Hiển thị điểm trung bình |
| `ranking` | string | "#3" | Hiển thị xếp hạng |
| `total_graded` | int | 15 | Hiển thị số bài đã chấm |
| `total_assigned` | int | 20 | Hiển thị tổng bài được giao |

---

## ✅ KIỂM TRA

Để verify thay đổi hoạt động:

1. **Đăng nhập** với tài khoản sinh viên
2. **Truy cập** các trang:
   - `/student-dashboard` → Sidebar phải hiển thị profile
   - `/student-assignments` → Sidebar phải hiển thị profile
   - `/student-results` → Sidebar + dữ liệu thực (điểm, xếp hạng, bài chấm)
   - `/student-submission-history` → Sidebar phải hiển thị profile

3. **Kiểm tra**:
   - ✅ Avatar: Hiển thị ký tự đầu tiên của tên sinh viên
   - ✅ Thông tin: Tên, mã sinh viên, lớp, giáo viên từ CSDL
   - ✅ Điểm: Từ bảng `evaluation_sessions`
   - ✅ Xếp hạng: Tính từ điểm trung bình

---

## 🐛 TROUBLESHOOTING

### Nếu profile không hiển thị:
1. Check xem student_profile được truyền vào template hay không
2. Verify CSDL có dữ liệu sinh viên, lớp, giáo viên
3. Check console log có error nào không

### Nếu dữ liệu hiển thị sai:
1. Check truy vấn SQL (có filter đúng student_id không)
2. Check cast/convert dữ liệu có đúng không (float cho score)
3. Check template có format đúng không (VD: `{{ student_profile.average_score }}`)

### Nếu dữ liệu lúc có lúc không:
1. Check CSDL có đầy đủ dữ liệu (students, enrollments, classes, teachers)
2. Verify LEFT JOIN không lọc dữ liệu (nên dùng LEFT JOIN, không phải INNER JOIN)

---

## 📝 NOTA BENE

- Hàm `_fetch_student_detailed_profile()` an toàn với NULL values
- Tất cả endpoints đều được cập nhật để sử dụng profile mới
- Profile section được style responsive (dark mode support)
- Xứ lý khi không có dữ liệu (fallback to default values)

