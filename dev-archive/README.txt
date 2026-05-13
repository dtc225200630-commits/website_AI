Thư mục dev-archive — tài liệu seed SQL, script kiểm tra / debug / benchmark, không dùng khi chạy ứng dụng (chỉ còn app.py + agents + templates + static ở gốc project).

- sql/          : file .sql seed, migration, verify (chạy thủ công trong PostgreSQL).
- scripts/      : mọi file .py gốc project trừ app.py (test_*, check_*, debug_*, solution_*, …).
- uploads-mirrors/ : bản sao file mẫu / test từng nằm trong uploads/ (uploads/ giờ để trống cho file nộp bài runtime).
- docs/         : báo cáo / hướng dẫn .md và .txt (ARCHITECTURE_*, HUONG_DAN_*, …) — không dùng khi chạy FastAPI.

Lưu ý agents/: chỉ còn các module production (bản *_fixed.py + coordinator, llm, …). Các file agent cũ trùng tên không _fixed đã xóa — tài liệu lịch sử trong docs/ vẫn có thể nhắc tên file cũ.

Chạy script Python trong scripts/: nên cd vào thư mục đó hoặc chỉnh đường dẫn tới solution_*.py cho khớp cwd.
