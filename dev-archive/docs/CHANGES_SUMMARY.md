# Tóm tắt các thay đổi - Trang Nộp Bài Dynamic

## Tổng quan
Đã cập nhật hệ thống để hiển thị thông tin bài tập động trên trang `trangnopbai.html` dựa trên dữ liệu từ database. Khi sinh viên nhấn "Nộp bài" ở `bangdkSV.html`, sẽ chuyển đến trang nộp bài với thông tin chi tiết của bài tập đã chọn.

## Các thay đổi chi tiết

### 1. **bangdkSV.html** - Cập nhật nút "Nộp bài"
- **Trước**: Button tĩnh không có hành động
- **Sau**: Thay bằng form GET gửi yêu cầu tới `/assignment/{assignment_id}`
```html
<form method="get" action="/assignment/{{ a.assignment_id }}" style="display: inline;">
<button type="submit" class="px-5 py-2.5 bg-primary text-on-primary text-xs font-bold rounded-lg hover:bg-primary-container transition-colors active:scale-95">Nộp bài</button>
</form>
```

### 2. **app.py** - Thêm route mới
Thêm endpoint `/assignment/{assignment_id}` để:
- Lấy thông tin chi tiết bài tập từ database dựa trên `assignment_id`
- Truy vấn bảng `assignments`, `classes`, và `users` để lấy tất cả dữ liệu cần thiết
- Định dạng ngày hạn thành format: `dd/mm/yyyy, hh:mm`
- Truyền dữ liệu assignment tới template `trangnopbai.html`

**Dữ liệu được lấy:**
- `assignment_id` - ID bài tập
- `title` - Tiêu đề bài tập
- `description` - Mô tả bài tập
- `due_date` / `due_date_display` - Ngày hạn nộp
- `programming_language` - Ngôn ngữ lập trình
- `class_name` - Tên lớp học
- `teacher_name` - Tên giáo viên
- `class_id` - ID lớp

### 3. **trangnopbai.html** - Cập nhật để hiển thị dữ liệu động

#### Phần tiêu đề
```html
<h2 class="text-3xl font-bold text-on-surface tracking-tight mb-2">{{ assignment.title }}</h2>
<p class="text-on-surface-variant text-sm max-w-2xl leading-relaxed">
    {{ assignment.description if assignment.description else 'Nộp mã nguồn của bạn để AI thực hiện đánh giá...' }}
</p>
```

#### Phần thông tin bài tập
- Hiển thị tên lớp học: `{{ assignment.class_name }}`
- Hiển thị tên giáo viên: `{{ assignment.teacher_name }}`

#### Phần chọn ngôn ngữ
- Pre-select ngôn ngữ lập trình dựa trên `{{ assignment.programming_language }}`
- Hỗ trợ: Python, Java, C++, JavaScript

#### Phần meta information
- Hạn nộp: `{{ assignment.due_date_display }}`
- Lớp học: `{{ assignment.class_name }}`

#### Phần code preview
- Tên file: `{{ assignment.title | replace(' ', '_') }}.{{ assignment.programming_language or 'py' }}`

## Luồng công việc
1. Sinh viên xem danh sách bài tập trong `bangdkSV.html`
2. Nhấn nút "Nộp bài" trên bài tập mong muốn
3. Form gửi request: `GET /assignment/{assignment_id}`
4. Backend lấy dữ liệu bài tập từ database
5. Trả về `trangnopbai.html` với thông tin bài tập
6. Trang hiển thị tất cả thông tin chi tiết bài tập từ database

## Xử lý lỗi
- Nếu `assignment_id` không tồn tại: Returns 404 "Bài tập không tồn tại"
- Nếu có lỗi database: Returns 500 với thông báo lỗi chi tiết

## Lợi ích
✅ Tránh hardcode thông tin bài tập
✅ Thông tin luôn cập nhật từ database
✅ Hỗ trợ nhiều bài tập với thông tin khác nhau
✅ User experience tốt hơn - sinh viên biết chính xác thông tin bài tập họ sắp nộp
