# -*- coding: utf-8 -*-
import logging
import os
from unittest.mock import Base
import bcrypt
import psycopg2
import psycopg2.errors
import ast
import re
import subprocess
import json
import tempfile
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import contextmanager


# Import Multi-Agent Coordinator
try:
    from agents.coordinator import coordinator
    print("[APP] [OK] Multi-agent coordinator imported successfully")
except ImportError as e:
    print(f"[APP] [FAIL] Failed to import coordinator: {e}")
    
    # Fallback coordinator if agents unavailable
    def coordinator(filepath, requirements, testcases, assignment_context=None):
        return {
            "syntax": {"score": 0, "success": False, "error": "Coordinator unavailable"},
            "requirement": {"score": 0, "details": []},
            "structure": {"score": 0, "details": []},
            "test": {"score": 0, "details": []},
            "llm": {"score": 0, "feedback": "Coordinator unavailable"},
            "total": {"total_score": 0, "grade": "F"}
        }

# Import LLM agent for AI-based code analysis (kept for backward compatibility)
try:
    from agents.llm_agent import llm_agent
except ImportError:
    # Fallback if llm_agent is not available
    def llm_agent(code):
        return {"score": 10, "feedback": "LLM agent không khả dụng"}

app = FastAPI()




logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Cấu hình CSDL (Đảm bảo db name MAS_Programming_Assessment đã tạo trong pgAdmin)
# Có thể override bằng biến môi trường DATABASE_URL để tránh lệch DB khi chạy.
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://postgres:123456@localhost:5432/AI3",
# )

# Tự động đọc link database từ Render, nếu chạy dưới máy local thì dùng localhost
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:matkhau@localhost:5432/AI3")

# Mount thư mục chứa các file giao diện
# Tạo thư mục 'templates' và bỏ các file html vào đó nhé
if not os.path.exists("templates"):
    os.makedirs("templates")

@contextmanager
def get_db():
    # Lấy link từ Render, nếu không có thì mới dùng cấu hình localhost ở máy
    db_url = os.getenv("DATABASE_URL", "postgresql://admin:syQULuHTP03idK10CPwiAIZVAucJJtCb@dpg-d82gv050lvsc738f1480-a.oregon-postgres.render.com/website_db_4cha")
    conn = psycopg2.connect(db_url)
    # conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    # Lưu ý: Pass trong DB nên được hash bằng bcrypt. 
    # Nếu đang để text thuần để test thì dùng: return plain_password == hashed_password
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except:
        return plain_password == hashed_password # Chống cháy nếu DB chưa hash


def _rows_to_dicts(cur, rows):
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in rows]


def _table_exists(conn, table_name: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s) IS NOT NULL", (table_name,))
        row = cur.fetchone()
        return bool(row[0]) if row else False


def _get_teacher_name(conn, teacher_id: int) -> str:
    with conn.cursor() as cur:
        cur.execute("SELECT full_name FROM teachers WHERE teacher_id = %s", (teacher_id,))
        row = cur.fetchone()
    return row[0] if row and row[0] else "Giáo viên"


def _submission_result_viewer_role(
    conn, request: Request, submission_student_id: int, assignment_id: int
) -> str:
    """Who may open /submission-result: owner student or teacher of the assignment's class."""
    role = (request.cookies.get("role") or "").strip()
    try:
        user_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để xem kết quả")

    if role == "student":
        if user_id != submission_student_id:
            raise HTTPException(status_code=403, detail="Bạn chỉ được xem bài nộp của chính mình")
        return "student"

    if role == "teacher":
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM assignments a
                JOIN classes c ON c.class_id = a.class_id
                WHERE a.assignment_id = %s AND c.teacher_id = %s
                LIMIT 1
                """,
                (assignment_id, user_id),
            )
            if cur.fetchone():
                return "teacher"
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem bài nộp này")

    raise HTTPException(status_code=403, detail="Vai trò không hợp lệ để xem kết quả này")


def _is_student_assigned(conn, assignment_id: int, student_id: int) -> bool:
    """Return True if student belongs to assignment's class and is in optional target list."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM assignments a
            JOIN enrollments e ON e.class_id = a.class_id
            WHERE a.assignment_id = %s
              AND e.student_id = %s
            LIMIT 1
            """,
            (assignment_id, student_id),
        )
        class_membership = cur.fetchone()

    if not class_membership:
        return False

    if not _table_exists(conn, "public.assignment_targets"):
        return True

    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM assignment_targets WHERE assignment_id = %s LIMIT 1",
            (assignment_id,),
        )
        has_targets = cur.fetchone() is not None

        if not has_targets:
            return True

        cur.execute(
            """
            SELECT 1
            FROM assignment_targets
            WHERE assignment_id = %s AND student_id = %s
            LIMIT 1
            """,
            (assignment_id, student_id),
        )
        return cur.fetchone() is not None


def _decorate_assignment(row: dict) -> dict:
    due_date = row.get("due_date")
    now = datetime.now(timezone.utc)
    row["due_date_display"] = None
    if due_date is not None and hasattr(due_date, "strftime"):
        row["due_date_display"] = due_date.strftime("%H:%M - %d/%m/%Y")

    # Badge classes reuse existing Tailwind tokens already in the HTML.
    row["status_label"] = "Đang tiến hành"
    row["status_badge_class"] = "bg-secondary-container text-on-secondary-container"
    try:
        if due_date is not None and due_date < now:
            row["status_label"] = "Quá hạn"
            row["status_badge_class"] = "bg-error-container text-on-error-container"
        elif due_date is not None and due_date <= now + timedelta(days=2):
            row["status_label"] = "Cần nộp gấp"
            row["status_badge_class"] = "bg-error-container text-on-error-container"
    except TypeError:
        # In case due_date has no timezone info or cannot be compared.
        pass
    return row


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
        if _table_exists(conn, "public.assignment_targets"):
            where_clause = """
                WHERE a.class_id IN (SELECT e.class_id FROM enrollments e WHERE e.student_id = %s)
                  AND (
                    NOT EXISTS (
                        SELECT 1
                        FROM assignment_targets at0
                        WHERE at0.assignment_id = a.assignment_id
                    )
                    OR EXISTS (
                        SELECT 1
                        FROM assignment_targets at1
                        WHERE at1.assignment_id = a.assignment_id
                          AND at1.student_id = %s
                    )
                  )
            """
            params.extend([student_id, student_id])
        else:
            where_clause = "WHERE a.class_id IN (SELECT e.class_id FROM enrollments e WHERE e.student_id = %s)"
            params.append(student_id)

    order_clause = "ORDER BY a.due_date ASC"
    query = "\n".join([base_select, where_clause, order_clause])

    with conn.cursor() as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        assignments = _rows_to_dicts(cur, rows)

    return [_decorate_assignment(a) for a in assignments]


def _subject_filters_from_assignments(assignments: list[dict]) -> list[dict]:
    """Danh sách môn/lớp (distinct) để lọc bài tập — dùng class_name làm nhãn môn."""
    seen: dict[int, str] = {}
    for a in assignments:
        cid = a.get("class_id")
        if cid is None:
            continue
        try:
            ik = int(cid)
        except (TypeError, ValueError):
            continue
        if ik not in seen:
            label = (a.get("class_name") or "").strip() or f"Lớp {ik}"
            seen[ik] = label
    return [{"class_id": k, "class_name": v} for k, v in sorted(seen.items(), key=lambda x: x[1].lower())]


def _parse_class_id_query(request: Request) -> int | None:
    raw = request.query_params.get("class_id")
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _filter_assignments_by_class(assignments: list[dict], class_id: int | None) -> list[dict]:
    if class_id is None:
        return list(assignments)
    out = []
    for a in assignments:
        try:
            if int(a.get("class_id")) == class_id:
                out.append(a)
        except (TypeError, ValueError):
            continue
    return out


def _fetch_student_profile(conn, student_id: int | None) -> dict:
    profile = {"full_name": "Sinh viên", "student_code": "--"}
    if not student_id:
        return profile

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT student_id, full_name
            FROM students
            WHERE student_id = %s
            """,
            (student_id,),
        )
        row = cur.fetchone()

    if not row:
        return profile

    profile["student_code"] = str(row[0])
    profile["full_name"] = row[1] or "Sinh viên"
    return profile


def _fetch_student_detailed_profile(conn, student_id: int | None) -> dict:
    """Fetch comprehensive student profile with grades, ranking, class info."""
    profile = {
        "full_name": "Sinh viên",
        "student_code": "--",
        "class_name": "Chưa xác định",
        "teacher_name": "--",
        "average_score": 0,
        "ranking": "--",
        "total_graded": 0,
        "total_assigned": 0,
    }
    
    if not student_id:
        return profile
    
    with conn.cursor() as cur:
        # Get student info, class, teacher
        cur.execute(
            """
            SELECT s.student_id, s.full_name, c.class_name, t.full_name
            FROM students s
            LEFT JOIN enrollments e ON e.student_id = s.student_id
            LEFT JOIN classes c ON c.class_id = e.class_id
            LEFT JOIN teachers t ON t.teacher_id = c.teacher_id
            WHERE s.student_id = %s
            LIMIT 1
            """,
            (student_id,),
        )
        row = cur.fetchone()
        
        if row:
            profile["student_code"] = str(row[0])
            profile["full_name"] = row[1] or "Sinh viên"
            profile["class_name"] = row[2] or "Chưa xác định"
            profile["teacher_name"] = row[3] or "--"
        
        # Get average score from all submissions
        cur.execute(
            """
            SELECT COALESCE(AVG(es.total_score), 0)
            FROM submissions s
            LEFT JOIN evaluation_sessions es ON es.submission_id = s.submission_id
            WHERE s.student_id = %s AND es.total_score IS NOT NULL
            """,
            (student_id,),
        )
        avg_row = cur.fetchone()
        avg_score = float(avg_row[0] or 0) if avg_row else 0
        profile["average_score"] = round(avg_score, 1)
        
        # Get student ranking
        cur.execute(
            """
            SELECT RANK() OVER (ORDER BY AVG(es.total_score) DESC)
            FROM students s
            LEFT JOIN submissions sub ON sub.student_id = s.student_id
            LEFT JOIN evaluation_sessions es ON es.submission_id = sub.submission_id
            WHERE s.student_id = %s
            GROUP BY s.student_id
            """,
            (student_id,),
        )
        rank_row = cur.fetchone()
        if rank_row and rank_row[0]:
            profile["ranking"] = f"#{rank_row[0]}"
        
        # Count total graded submissions
        cur.execute(
            """
            SELECT COUNT(DISTINCT s.submission_id)
            FROM submissions s
            JOIN evaluation_sessions es ON es.submission_id = s.submission_id
            WHERE s.student_id = %s AND es.total_score IS NOT NULL
            """,
            (student_id,),
        )
        graded_row = cur.fetchone()
        profile["total_graded"] = int(graded_row[0] or 0) if graded_row else 0
        
        # Count total assigned
        cur.execute(
            """
            SELECT COUNT(DISTINCT a.assignment_id)
            FROM assignments a
            JOIN enrollments e ON e.class_id = a.class_id
            WHERE e.student_id = %s
            """,
            (student_id,),
        )
        assigned_row = cur.fetchone()
        profile["total_assigned"] = int(assigned_row[0] or 0) if assigned_row else 0
    
    return profile


def _due_as_utc_for_compare(due_date: datetime) -> datetime:
    """Chuẩn hóa due_date để so sánh / sắp xếp (DB thường trả TIMESTAMPTZ hoặc naive)."""
    if due_date.tzinfo is None:
        return due_date.replace(tzinfo=timezone.utc)
    return due_date.astimezone(timezone.utc)


def _build_upcoming_deadlines(assignments: list[dict], limit: int = 3) -> list[dict]:
    weekday_map = {
        0: "Thứ 2",
        1: "Thứ 3",
        2: "Thứ 4",
        3: "Thứ 5",
        4: "Thứ 6",
        5: "Thứ 7",
        6: "Chủ nhật",
    }
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()
    candidates: list[tuple[datetime, dict]] = []

    for assignment in assignments:
        due_date = assignment.get("due_date")
        if due_date is None or not hasattr(due_date, "strftime"):
            continue

        try:
            if due_date < now_utc:
                continue
        except TypeError:
            if due_date < now_local:
                continue

        try:
            sort_key = _due_as_utc_for_compare(due_date)
        except (TypeError, ValueError):
            continue

        candidates.append((sort_key, assignment))

    candidates.sort(key=lambda x: x[0])

    upcoming: list[dict] = []
    for _, assignment in candidates[:limit]:
        due_date = assignment.get("due_date")
        if due_date is None or not hasattr(due_date, "strftime"):
            continue
        upcoming.append(
            {
                "assignment_id": assignment.get("assignment_id"),
                "title": assignment.get("title") or "Bài tập",
                "class_name": (assignment.get("class_name") or "").strip() or None,
                "due_time": due_date.strftime("%H:%M"),
                "weekday": weekday_map.get(due_date.weekday(), "--"),
                "day_of_month": str(due_date.day),
                "month_short": f"Th{due_date.month}",
            }
        )

    return upcoming


def _fetch_latest_student_score(conn, student_id: int | None) -> dict | None:
    if not student_id:
        return None

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                a.title,
                COALESCE(latest_eval.total_score, 0)::float AS total_score,
                s.submitted_at
            FROM submissions s
            JOIN assignments a ON a.assignment_id = s.assignment_id
            LEFT JOIN LATERAL (
                SELECT es.total_score, es.created_at
                FROM evaluation_sessions es
                WHERE es.submission_id = s.submission_id
                ORDER BY es.created_at DESC
                LIMIT 1
            ) latest_eval ON TRUE
            WHERE s.student_id = %s
            ORDER BY COALESCE(latest_eval.created_at, s.submitted_at) DESC, s.submission_id DESC
            LIMIT 1
            """,
            (student_id,),
        )
        row = cur.fetchone()

    if not row:
        return None

    title, total_score, submitted_at = row
    submitted_at_display = "--"
    if submitted_at is not None and hasattr(submitted_at, "strftime"):
        submitted_at_display = submitted_at.strftime("%d/%m/%Y %H:%M")

    return {
        "title": title or "Bài nộp gần nhất",
        "score": round(float(total_score or 0), 1),
        "submitted_at_display": submitted_at_display,
    }


def _student_time_greeting() -> str:
    h = datetime.now().hour
    if 5 <= h < 12:
        return "Chào buổi sáng"
    if 12 <= h < 18:
        return "Chào buổi chiều"
    return "Chào buổi tối"


def _student_dashboard_insight(
    student_profile: dict | None,
    student_progress: dict | None,
    latest_score: dict | None,
) -> str:
    """Mô tả ngắn dựa trên dữ liệu thật (thay nội dung AI tĩnh)."""
    pending = (student_progress or {}).get("pending_count") or 0
    total = (student_progress or {}).get("total_assigned") or 0
    pct = (student_progress or {}).get("completion_percent") or 0
    if pending > 0:
        return (
            f"Bạn còn {pending} trong {total} bài được giao chưa nộp "
            f"({pct}% đã hoàn thành). Mở mục Bài tập để xem hạn và nộp đúng thời hạn."
        )
    if latest_score:
        return (
            f"Lần chấm gần nhất: «{latest_score.get('title') or 'Bài nộp'}» "
            f"— {latest_score.get('score', 0)}/100 điểm. Tiếp tục giữ nhịp nộp bài đều đặn."
        )
    avg = (student_profile or {}).get("average_score") or 0
    if avg and float(avg) > 0:
        return f"Điểm trung bình các bài đã chấm: {avg}/100. Hãy xem chi tiết từng bài ở mục Kết quả."
    return "Khi có bài mới hoặc điểm chấm, thông tin sẽ hiển thị tại đây và trong mục Kết quả / Lịch sử."


def _fetch_student_graded_assignments(conn, student_id: int | None, limit: int = 50) -> list[dict]:
    """Mỗi bài tập một dòng: điểm mới nhất đã chấm (theo thời gian chấm)."""
    if not student_id:
        return []

    with conn.cursor() as cur:
        cur.execute(
            """
            WITH ranked AS (
                SELECT
                    s.assignment_id,
                    a.title,
                    c.class_name,
                    c.class_id,
                    es.total_score::double precision AS total_score,
                    es.created_at AS graded_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.assignment_id
                        ORDER BY es.created_at DESC NULLS LAST, s.submission_id DESC
                    ) AS rn
                FROM submissions s
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                JOIN evaluation_sessions es ON es.submission_id = s.submission_id
                WHERE s.student_id = %s AND es.total_score IS NOT NULL
            )
            SELECT assignment_id, title, class_name, class_id, total_score, graded_at
            FROM ranked
            WHERE rn = 1
            ORDER BY graded_at DESC NULLS LAST
            LIMIT %s
            """,
            (student_id, limit),
        )
        rows = cur.fetchall()

    out: list[dict] = []
    for row in rows:
        graded_at = row[5]
        display = "--"
        if graded_at is not None and hasattr(graded_at, "strftime"):
            display = graded_at.strftime("%d/%m/%Y %H:%M")
        out.append(
            {
                "assignment_id": row[0],
                "title": row[1] or "Bài tập",
                "class_name": row[2] or "",
                "class_id": int(row[3]) if row[3] is not None else None,
                "score": round(float(row[4] or 0), 1),
                "graded_at_display": display,
            }
        )
    return out


def _fetch_student_submission_rollups(conn, student_id: int | None) -> dict:
    """Thống kê thật trên toàn bộ bản nộp của sinh viên (cho giao diện / gợi ý ngắn)."""
    empty = {
        "total_submissions": 0,
        "pending_eval_count": 0,
        "compile_error_count": 0,
        "high_score_count": 0,
    }
    if not student_id:
        return empty

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                COUNT(*)::int AS total,
                COUNT(*) FILTER (WHERE le.ev_at IS NULL)::int AS pending_eval,
                COUNT(*) FILTER (
                    WHERE le.ev_at IS NOT NULL
                      AND COALESCE(le.ts, 0) = 0
                      AND COALESCE(le.syn, 0) = 0
                )::int AS compile_fail,
                COUNT(*) FILTER (WHERE COALESCE(le.ts, 0) >= 80)::int AS high_score
            FROM submissions s
            LEFT JOIN LATERAL (
                SELECT
                    es.created_at AS ev_at,
                    es.total_score::double precision AS ts,
                    es.syntax_score::double precision AS syn
                FROM evaluation_sessions es
                WHERE es.submission_id = s.submission_id
                ORDER BY es.created_at DESC NULLS LAST
                LIMIT 1
            ) le ON TRUE
            WHERE s.student_id = %s
            """,
            (student_id,),
        )
        row = cur.fetchone()

    if not row:
        return empty

    return {
        "total_submissions": int(row[0] or 0),
        "pending_eval_count": int(row[1] or 0),
        "compile_error_count": int(row[2] or 0),
        "high_score_count": int(row[3] or 0),
    }


def _compute_student_progress(conn, student_id: int | None, assignments: list[dict]) -> dict:
    assignment_ids = [int(a["assignment_id"]) for a in assignments if a.get("assignment_id") is not None]
    total_assigned = len(set(assignment_ids))

    if not student_id or total_assigned == 0:
        return {
            "total_assigned": total_assigned,
            "submitted_count": 0,
            "pending_count": total_assigned,
            "completion_percent": 0,
            "pending_assignment_ids": set(assignment_ids),
        }

    placeholders = ",".join(["%s"] * len(assignment_ids))
    query = f"""
        SELECT DISTINCT s.assignment_id
        FROM submissions s
        WHERE s.student_id = %s
          AND s.assignment_id IN ({placeholders})
    """

    with conn.cursor() as cur:
        cur.execute(query, tuple([student_id] + assignment_ids))
        submitted_ids = {int(row[0]) for row in cur.fetchall()}

    submitted_count = len(submitted_ids)
    pending_count = max(total_assigned - submitted_count, 0)
    completion_percent = int(round((submitted_count / total_assigned) * 100)) if total_assigned else 0
    completion_percent = min(max(completion_percent, 0), 100)

    return {
        "total_assigned": total_assigned,
        "submitted_count": submitted_count,
        "pending_count": pending_count,
        "completion_percent": completion_percent,
        "pending_assignment_ids": set(assignment_ids) - submitted_ids,
    }


def _fetch_student_submission_history(
    conn,
    student_id: int | None,
    limit: int = 10,
    offset: int = 0,
    class_id: int | None = None,
) -> tuple[list[dict], int]:
    if not student_id:
        return [], 0

    class_filter_sql = " AND (%s IS NULL OR a.class_id = %s)"
    filter_tuple = (student_id, class_id, class_id)

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT COUNT(*)::int
            FROM submissions s
            JOIN assignments a ON a.assignment_id = s.assignment_id
            WHERE s.student_id = %s
            {class_filter_sql}
            """,
            filter_tuple,
        )
        total_count = int(cur.fetchone()[0] or 0)

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT
                s.submission_id,
                a.assignment_id,
                a.title AS assignment_title,
                COALESCE(a.programming_language, 'Python') AS programming_language,
                a.class_id,
                c.class_name,
                s.submitted_at,
                latest_eval.created_at AS evaluated_at,
                COALESCE(latest_eval.total_score, 0)::float AS total_score,
                COALESCE(latest_eval.syntax_score, 0)::float AS syntax_score,
                COALESCE(latest_eval.test_score, 0)::float AS test_score
            FROM submissions s
            JOIN assignments a ON a.assignment_id = s.assignment_id
            JOIN classes c ON c.class_id = a.class_id
            LEFT JOIN LATERAL (
                SELECT
                    es.created_at,
                    es.total_score,
                    es.syntax_score,
                    es.test_score
                FROM evaluation_sessions es
                WHERE es.submission_id = s.submission_id
                ORDER BY es.created_at DESC
                LIMIT 1
            ) latest_eval ON TRUE
            WHERE s.student_id = %s
            {class_filter_sql}
            ORDER BY s.submitted_at DESC NULLS LAST, s.submission_id DESC
            LIMIT %s OFFSET %s
            """,
            tuple([student_id, class_id, class_id, limit, offset]),
        )
        rows = cur.fetchall()

    submissions = []
    for row in rows:
        submission = {
            "submission_id": row[0],
            "assignment_id": row[1],
            "assignment_title": row[2],
            "programming_language": row[3],
            "class_id": int(row[4]) if row[4] is not None else None,
            "class_name": row[5] or "",
            "submitted_at": row[6],
            "evaluated_at": row[7],
            "total_score": float(row[8] or 0),
            "syntax_score": float(row[9] or 0),
            "test_score": float(row[10] or 0),
        }

        submitted_at = submission.get("submitted_at")
        if submitted_at is not None and hasattr(submitted_at, "strftime"):
            submission["submitted_date_display"] = submitted_at.strftime("%d/%m/%Y")
            submission["submitted_time_display"] = submitted_at.strftime("%H:%M:%S")
        else:
            submission["submitted_date_display"] = "--"
            submission["submitted_time_display"] = "--"

        total_score = submission["total_score"]
        syntax_score = submission["syntax_score"]
        evaluated_at = submission.get("evaluated_at")
        score_percent = max(0, min(int(round(total_score)), 100))
        submission["score_percent"] = score_percent
        submission["score_display"] = f"{total_score:.1f}/100"
        if score_percent >= 100:
            submission["score_width_class"] = "w-full"
        elif score_percent >= 90:
            submission["score_width_class"] = "w-11/12"
        elif score_percent >= 75:
            submission["score_width_class"] = "w-3/4"
        elif score_percent >= 50:
            submission["score_width_class"] = "w-1/2"
        elif score_percent >= 25:
            submission["score_width_class"] = "w-1/4"
        elif score_percent > 0:
            submission["score_width_class"] = "w-1/12"
        else:
            submission["score_width_class"] = "w-0"

        if evaluated_at is None:
            submission["status_label"] = "Đang chấm"
            submission["status_icon"] = "hourglass_top"
            submission["status_text_class"] = "text-orange-400"
            submission["status_dot_class"] = "bg-orange-400"
            submission["score_bar_class"] = "bg-orange-400"
        elif total_score == 0 and syntax_score == 0:
            submission["status_label"] = "Lỗi biên dịch"
            submission["status_icon"] = "error_outline"
            submission["status_text_class"] = "text-error"
            submission["status_dot_class"] = "bg-error"
            submission["score_bar_class"] = "bg-error"
        elif total_score >= 80:
            submission["status_label"] = "Thành công"
            submission["status_icon"] = "check_circle"
            submission["status_text_class"] = "text-primary"
            submission["status_dot_class"] = "bg-primary"
            submission["score_bar_class"] = "bg-gradient-to-r from-primary to-primary-container"
        elif total_score >= 50:
            submission["status_label"] = "Cần cải thiện"
            submission["status_icon"] = "warning"
            submission["status_text_class"] = "text-orange-400"
            submission["status_dot_class"] = "bg-orange-400"
            submission["score_bar_class"] = "bg-orange-400"
        else:
            submission["status_label"] = "Chưa đạt"
            submission["status_icon"] = "priority_high"
            submission["status_text_class"] = "text-error"
            submission["status_dot_class"] = "bg-error"
            submission["score_bar_class"] = "bg-error"

        submissions.append(submission)

    return submissions, total_count

@app.get("/")
async def root():
    # Trả về file đăng nhập
    return FileResponse("templates/dangnhap.html")

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
    id_column = "teacher_id" if role == "teacher" else "student_id"
    
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Dùng LOWER() để so sánh không phân biệt hoa/thường
                cur.execute(
                    f"SELECT {id_column}, password_hash, full_name FROM {table} WHERE LOWER(email) = %s",
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

@app.get("/logout")
async def logout():
    """Đăng xuất - xóa các cookies"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="user_id")
    response.delete_cookie(key="role")
    response.delete_cookie(key="full_name")
    response.delete_cookie(key="remember_me")
    return response

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

@app.get("/teacher-dashboard")
async def teacher_page(request: Request):
    """Hiển thị bảng điều khiển giáo viên với tất cả dữ liệu thực từ DB"""
    try:
        with get_db() as conn:
            # Lấy thông tin giáo viên từ cookie
            teacher_id = None
            try:
                teacher_id = int(request.cookies.get("user_id") or "")
            except ValueError:
                teacher_id = None
            
            # Lấy tên giáo viên
            teacher_name = "Giáo viên"
            if teacher_id:
                with conn.cursor() as cur:
                    cur.execute("SELECT full_name FROM teachers WHERE teacher_id = %s", (teacher_id,))
                    row = cur.fetchone()
                    if row:
                        teacher_name = row[0]
            
            has_assignment_targets = _table_exists(conn, "public.assignment_targets")

            # Lấy assignments của giáo viên đang đăng nhập
            with conn.cursor() as cur:
                if has_assignment_targets:
                    cur.execute("""
                        SELECT
                            a.assignment_id,
                            a.title,
                            a.description,
                            a.due_date,
                            a.programming_language,
                            c.class_id,
                            c.class_name,
                            t.full_name AS teacher_name,
                            COUNT(DISTINCT s.submission_id) as total_submissions,
                            AVG(COALESCE(e.total_score, 0))::float as avg_score,
                            latest_sub.latest_submission_id,
                            latest_sub.latest_student_name,
                            latest_sub.latest_total_score,
                            latest_sub.latest_submitted_at,
                            class_stat.class_student_count,
                            target_stat.target_student_count
                        FROM assignments a
                        JOIN classes c ON c.class_id = a.class_id
                        LEFT JOIN teachers t ON t.teacher_id = c.teacher_id
                        LEFT JOIN submissions s ON s.assignment_id = a.assignment_id
                        LEFT JOIN evaluation_sessions e ON e.submission_id = s.submission_id
                        LEFT JOIN LATERAL (
                            SELECT
                                s2.submission_id AS latest_submission_id,
                                st2.full_name AS latest_student_name,
                                COALESCE(es2.total_score, 0)::float AS latest_total_score,
                                s2.submitted_at AS latest_submitted_at
                            FROM submissions s2
                            JOIN students st2 ON st2.student_id = s2.student_id
                            LEFT JOIN LATERAL (
                                SELECT total_score
                                FROM evaluation_sessions
                                WHERE submission_id = s2.submission_id
                                ORDER BY created_at DESC
                                LIMIT 1
                            ) es2 ON TRUE
                            WHERE s2.assignment_id = a.assignment_id
                            ORDER BY s2.submitted_at DESC NULLS LAST, s2.submission_id DESC
                            LIMIT 1
                        ) latest_sub ON TRUE
                        LEFT JOIN LATERAL (
                            SELECT COUNT(*)::int AS class_student_count
                            FROM enrollments e0
                            WHERE e0.class_id = c.class_id
                        ) class_stat ON TRUE
                        LEFT JOIN LATERAL (
                            SELECT COUNT(*)::int AS target_student_count
                            FROM assignment_targets at
                            WHERE at.assignment_id = a.assignment_id
                        ) target_stat ON TRUE
                        WHERE c.teacher_id = %s
                        GROUP BY a.assignment_id, a.title, a.description, a.due_date, a.programming_language,
                                 c.class_id, c.class_name, t.full_name,
                                 latest_sub.latest_submission_id, latest_sub.latest_student_name,
                                 latest_sub.latest_total_score, latest_sub.latest_submitted_at,
                                 class_stat.class_student_count, target_stat.target_student_count
                        ORDER BY a.due_date DESC
                    """, (teacher_id,))
                else:
                    cur.execute("""
                        SELECT
                            a.assignment_id,
                            a.title,
                            a.description,
                            a.due_date,
                            a.programming_language,
                            c.class_id,
                            c.class_name,
                            t.full_name AS teacher_name,
                            COUNT(DISTINCT s.submission_id) as total_submissions,
                            AVG(COALESCE(e.total_score, 0))::float as avg_score,
                            latest_sub.latest_submission_id,
                            latest_sub.latest_student_name,
                            latest_sub.latest_total_score,
                            latest_sub.latest_submitted_at,
                            class_stat.class_student_count,
                            NULL::int AS target_student_count
                        FROM assignments a
                        JOIN classes c ON c.class_id = a.class_id
                        LEFT JOIN teachers t ON t.teacher_id = c.teacher_id
                        LEFT JOIN submissions s ON s.assignment_id = a.assignment_id
                        LEFT JOIN evaluation_sessions e ON e.submission_id = s.submission_id
                        LEFT JOIN LATERAL (
                            SELECT
                                s2.submission_id AS latest_submission_id,
                                st2.full_name AS latest_student_name,
                                COALESCE(es2.total_score, 0)::float AS latest_total_score,
                                s2.submitted_at AS latest_submitted_at
                            FROM submissions s2
                            JOIN students st2 ON st2.student_id = s2.student_id
                            LEFT JOIN LATERAL (
                                SELECT total_score
                                FROM evaluation_sessions
                                WHERE submission_id = s2.submission_id
                                ORDER BY created_at DESC
                                LIMIT 1
                            ) es2 ON TRUE
                            WHERE s2.assignment_id = a.assignment_id
                            ORDER BY s2.submitted_at DESC NULLS LAST, s2.submission_id DESC
                            LIMIT 1
                        ) latest_sub ON TRUE
                        LEFT JOIN LATERAL (
                            SELECT COUNT(*)::int AS class_student_count
                            FROM enrollments e0
                            WHERE e0.class_id = c.class_id
                        ) class_stat ON TRUE
                        WHERE c.teacher_id = %s
                        GROUP BY a.assignment_id, a.title, a.description, a.due_date, a.programming_language,
                                 c.class_id, c.class_name, t.full_name,
                                 latest_sub.latest_submission_id, latest_sub.latest_student_name,
                                 latest_sub.latest_total_score, latest_sub.latest_submitted_at,
                                 class_stat.class_student_count
                        ORDER BY a.due_date DESC
                    """, (teacher_id,))
                rows = cur.fetchall()
                columns = ['assignment_id', 'title', 'description', 'due_date', 'programming_language',
                          'class_id', 'class_name', 'teacher_name', 'total_submissions', 'avg_score',
                          'latest_submission_id', 'latest_student_name', 'latest_total_score', 'latest_submitted_at',
                          'class_student_count', 'target_student_count']
                assignments = [dict(zip(columns, row)) for row in rows]

            # Build targeting status label for dashboard cards.
            for assignment in assignments:
                class_student_count = int(assignment.get('class_student_count') or 0)
                target_student_count = assignment.get('target_student_count')
                target_student_count = int(target_student_count) if target_student_count is not None else 0

                if target_student_count > 0 and class_student_count > 0 and target_student_count < class_student_count:
                    assignment['target_scope_label'] = f"Giao cho {target_student_count} sinh viên"
                    assignment['target_scope_badge_class'] = "bg-amber-100 text-amber-800"
                else:
                    assignment['target_scope_label'] = "Được giao cho toàn lớp"
                    assignment['target_scope_badge_class'] = "bg-emerald-100 text-emerald-800"

            class_filters = []
            seen_classes = set()
            for assignment in assignments:
                class_id = assignment.get('class_id')
                class_name = assignment.get('class_name')
                if class_id in seen_classes:
                    continue
                seen_classes.add(class_id)
                class_filters.append({"class_id": class_id, "class_name": class_name})
            
            # Tính tổng thống kê
            total_submissions = sum(a.get('total_submissions', 0) for a in assignments)
            avg_overall_score = 0
            if assignments:
                scores = [a.get('avg_score', 0) or 0 for a in assignments]
                scored = [s for s in scores if s > 0]
                avg_overall_score = (sum(scored) / len(scored)) if scored else 0
            
            # Lấy thống kê tổng số học sinh
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(DISTINCT e.student_id)
                    FROM enrollments e
                    JOIN classes c ON c.class_id = e.class_id
                    WHERE c.teacher_id = %s
                """, (teacher_id,))
                total_students = cur.fetchone()[0]
            
            # Decorate assignments
            for a in assignments:
                _decorate_assignment(a)

            upcoming_deadlines = _build_upcoming_deadlines(assignments, limit=5)

        return templates.TemplateResponse(
            "tranggiaovien.html",
            {
                "request": request,
                "teacher_name": teacher_name,
                "assignments": assignments,
                "class_filters": class_filters,
                "total_submissions": total_submissions,
                "avg_overall_score": round(avg_overall_score, 1),
                "total_students": total_students,
                "today": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
                "upcoming_deadlines": upcoming_deadlines,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


@app.get("/api/teacher/assignment/{assignment_id}/recent-submissions")
async def teacher_assignment_recent_submissions(request: Request, assignment_id: int, limit: int = 10):
    """Return recent submissions and score details for one assignment on teacher dashboard."""
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")

    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    safe_limit = max(1, min(limit, 30))

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        a.assignment_id,
                        a.title,
                        c.class_id,
                        c.class_name,
                        s.submission_id,
                        st.student_id,
                        st.full_name AS student_name,
                        s.submitted_at,
                        COALESCE(es.total_score, 0)::float AS total_score,
                        COALESCE(es.syntax_score, 0)::float AS syntax_score,
                        COALESCE(es.code_analysis_score, 0)::float AS code_analysis_score,
                        COALESCE(es.requirement_score, 0)::float AS requirement_score,
                        COALESCE(es.structure_score, 0)::float AS structure_score,
                        COALESCE(es.test_score, 0)::float AS test_score,
                        COALESCE(es.llm_score, 0)::float AS llm_score,
                        COALESCE(es.final_feedback, '') AS final_feedback
                    FROM assignments a
                    JOIN classes c ON c.class_id = a.class_id
                    LEFT JOIN submissions s ON s.assignment_id = a.assignment_id
                    LEFT JOIN students st ON st.student_id = s.student_id
                    LEFT JOIN LATERAL (
                        SELECT
                            total_score,
                            syntax_score,
                            code_analysis_score,
                            requirement_score,
                            structure_score,
                            test_score,
                            llm_score,
                            final_feedback
                        FROM evaluation_sessions
                        WHERE submission_id = s.submission_id
                        ORDER BY created_at DESC
                        LIMIT 1
                    ) es ON TRUE
                    WHERE a.assignment_id = %s
                      AND c.teacher_id = %s
                    ORDER BY s.submitted_at DESC NULLS LAST, s.submission_id DESC
                    LIMIT %s
                    """,
                                        (assignment_id, teacher_id, safe_limit),
                )
                rows = cur.fetchall()

        if not rows:
            return {
                "assignment_id": assignment_id,
                "assignment_title": None,
                "submissions": [],
            }

        assignment_title = rows[0][1]
        class_name = rows[0][3]
        submissions = []
        for row in rows:
            submission_id = row[4]
            if submission_id is None:
                continue

            submitted_at = row[7]
            submitted_at_display = None
            if submitted_at is not None and hasattr(submitted_at, "strftime"):
                submitted_at_display = submitted_at.strftime("%d/%m/%Y %H:%M")

            submissions.append(
                {
                    "submission_id": submission_id,
                    "class_id": row[2],
                    "class_name": row[3],
                    "student_id": row[5],
                    "student_name": row[6],
                    "submitted_at": submitted_at_display,
                    "total_score": row[8],
                    "syntax_score": row[9],
                    "code_analysis_score": row[10],
                    "requirement_score": row[11],
                    "structure_score": row[12],
                    "test_score": row[13],
                    "llm_score": row[14],
                    "final_feedback": row[15],
                }
            )

        return {
            "assignment_id": assignment_id,
            "assignment_title": assignment_title,
            "class_name": class_name,
            "submissions": submissions,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách nộp bài: {str(e)}")


@app.get("/teacher/submissions")
async def teacher_submissions_page(request: Request):
    """Teacher page: view all recent submissions with class filter and student search."""
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")

    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    with get_db() as conn:
        teacher_name = _get_teacher_name(conn, teacher_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    s.submission_id,
                    a.assignment_id,
                    a.title AS assignment_title,
                    c.class_id,
                    c.class_name,
                    st.student_id,
                    st.full_name AS student_name,
                    s.submitted_at,
                    COALESCE(es.total_score, 0)::float AS total_score,
                    COALESCE(es.syntax_score, 0)::float AS syntax_score,
                    COALESCE(es.code_analysis_score, 0)::float AS code_analysis_score,
                    COALESCE(es.requirement_score, 0)::float AS requirement_score,
                    COALESCE(es.structure_score, 0)::float AS structure_score,
                    COALESCE(es.test_score, 0)::float AS test_score
                FROM submissions s
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                JOIN students st ON st.student_id = s.student_id
                LEFT JOIN LATERAL (
                    SELECT
                        total_score,
                        syntax_score,
                        code_analysis_score,
                        requirement_score,
                        structure_score,
                        test_score
                    FROM evaluation_sessions
                    WHERE submission_id = s.submission_id
                    ORDER BY created_at DESC
                    LIMIT 1
                ) es ON TRUE
                WHERE c.teacher_id = %s
                ORDER BY s.submitted_at DESC NULLS LAST, s.submission_id DESC
                """,
                (teacher_id,),
            )
            rows = cur.fetchall()

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    a.assignment_id,
                    a.title,
                    a.due_date,
                    c.class_id,
                    c.class_name,
                    (SELECT COUNT(*)::int FROM submissions s WHERE s.assignment_id = a.assignment_id) AS submission_count,
                    (SELECT COUNT(*)::int FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id) AS req_count,
                    (SELECT COUNT(*)::int FROM assignment_testcases atc WHERE atc.assignment_id = a.assignment_id) AS tc_count
                FROM assignments a
                JOIN classes c ON c.class_id = a.class_id
                WHERE c.teacher_id = %s
                ORDER BY a.due_date DESC NULLS LAST, a.assignment_id DESC
                """,
                (teacher_id,),
            )
            assign_rows = cur.fetchall()

    assign_cols = [
        "assignment_id",
        "title",
        "due_date",
        "class_id",
        "class_name",
        "submission_count",
        "req_count",
        "tc_count",
    ]
    teacher_assignments = [dict(zip(assign_cols, row)) for row in assign_rows]
    for a in teacher_assignments:
        dd = a.get("due_date")
        if dd is not None and hasattr(dd, "strftime"):
            a["due_date_display"] = dd.strftime("%d/%m/%Y %H:%M")
        else:
            a["due_date_display"] = "--"

    columns = [
        "submission_id",
        "assignment_id",
        "assignment_title",
        "class_id",
        "class_name",
        "student_id",
        "student_name",
        "submitted_at",
        "total_score",
        "syntax_score",
        "code_analysis_score",
        "requirement_score",
        "structure_score",
        "test_score",
    ]
    submissions = [dict(zip(columns, row)) for row in rows]

    class_filters = []
    seen = set()
    for item in submissions:
        class_id = item.get("class_id")
        class_name = item.get("class_name")
        if class_id in seen:
            continue
        seen.add(class_id)
        class_filters.append({"class_id": class_id, "class_name": class_name})

    for item in submissions:
        submitted_at = item.get("submitted_at")
        if submitted_at is not None and hasattr(submitted_at, "strftime"):
            item["submitted_at_display"] = submitted_at.strftime("%d/%m/%Y %H:%M")
        else:
            item["submitted_at_display"] = "--"

    flash_saved = (request.query_params.get("saved") or "").strip() == "1"
    flash_deleted = (request.query_params.get("deleted") or "").strip() == "1"
    flash_error = (request.query_params.get("error") or "").strip()

    return templates.TemplateResponse(
        "giaovien_all_submissions.html",
        {
            "request": request,
            "teacher_name": teacher_name,
            "submissions": submissions,
            "class_filters": class_filters,
            "teacher_assignments": teacher_assignments,
            "today": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
            "flash_saved": flash_saved,
            "flash_deleted": flash_deleted,
            "flash_error": flash_error,
        },
    )


@app.get("/teacher/assignment/new")
async def teacher_new_assignment_page(request: Request):
    """Render teacher page to create assignment, requirements, testcases, and target students."""
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")

    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    with get_db() as conn:
        teacher_name = _get_teacher_name(conn, teacher_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.class_id, c.class_name, c.semester, c.academic_year,
                       COUNT(e.student_id) AS total_students
                FROM classes c
                LEFT JOIN enrollments e ON e.class_id = c.class_id
                WHERE c.teacher_id = %s
                GROUP BY c.class_id, c.class_name, c.semester, c.academic_year
                ORDER BY c.class_name ASC
                """,
                (teacher_id,),
            )
            class_rows = cur.fetchall()

            cur.execute(
                """
                SELECT e.class_id, s.student_id, s.full_name, s.email
                FROM enrollments e
                JOIN students s ON s.student_id = e.student_id
                JOIN classes c ON c.class_id = e.class_id
                WHERE c.teacher_id = %s
                ORDER BY e.class_id, s.full_name
                """,
                (teacher_id,),
            )
            student_rows = cur.fetchall()

    classes = [
        {
            "class_id": row[0],
            "class_name": row[1],
            "semester": row[2],
            "academic_year": row[3],
            "total_students": int(row[4] or 0),
        }
        for row in class_rows
    ]

    students_by_class = {}
    for class_id, student_id, full_name, email in student_rows:
        key = str(class_id)
        students_by_class.setdefault(key, []).append(
            {
                "student_id": student_id,
                "full_name": full_name,
                "email": email,
            }
        )

    err = (request.query_params.get("error") or "").strip()

    return templates.TemplateResponse(
        "taobaitap_giaovien.html",
        {
            "request": request,
            "teacher_name": teacher_name,
            "classes": classes,
            "students_by_class_json": json.dumps(students_by_class, ensure_ascii=False),
            "form_error": err,
        },
    )


@app.get("/teacher/agents")
async def teacher_agents_page(request: Request):
    """Teacher page: monitor AI agent activity, performance and config overview."""
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")

    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    with get_db() as conn:
        teacher_name = _get_teacher_name(conn, teacher_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    al.agent_name,
                    al.result,
                    al.created_at
                FROM agent_logs al
                JOIN submissions s ON s.submission_id = al.submission_id
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                WHERE c.teacher_id = %s
                ORDER BY al.created_at DESC
                """,
                (teacher_id,),
            )
            log_rows = cur.fetchall()

            cur.execute(
                """
                SELECT
                    AVG(COALESCE(es.syntax_score, 0))::float AS syntax_avg,
                    AVG(COALESCE(es.code_analysis_score, 0))::float AS analysis_avg,
                    AVG(COALESCE(es.requirement_score, 0))::float AS requirement_avg,
                    AVG(COALESCE(es.structure_score, 0))::float AS structure_avg,
                    AVG(COALESCE(es.test_score, 0))::float AS test_avg,
                    AVG(COALESCE(es.llm_score, 0))::float AS llm_avg
                FROM evaluation_sessions es
                JOIN submissions s ON s.submission_id = es.submission_id
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                WHERE c.teacher_id = %s
                """,
                (teacher_id,),
            )
            avg_row = cur.fetchone()

    def _parse_efficiency_percent(agent_name: str, result_text: str | None) -> float | None:
        text = (result_text or "").strip()
        if not text:
            return None

        lowered = text.lower()

        if agent_name == "SyntaxAgent":
            if "pass" in lowered or "no syntax error" in lowered:
                return 100.0
            if "fail" in lowered or "error" in lowered:
                return 0.0

        if agent_name == "TestAgent":
            pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
            if pct_match:
                return max(0.0, min(100.0, float(pct_match.group(1))))

        score_match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*20", text)
        if score_match:
            score = float(score_match.group(1))
            return max(0.0, min(100.0, (score / 20.0) * 100.0))

        req_match = re.search(r"(\d+)\s*/\s*(\d+)", text)
        if agent_name == "RequirementAgent" and req_match:
            met = int(req_match.group(1))
            total = int(req_match.group(2))
            if total > 0:
                return max(0.0, min(100.0, (met / total) * 100.0))

        if any(k in lowered for k in ["pass", "satisfied", "good", "excellent"]):
            return 100.0
        if any(k in lowered for k in ["fail", "error"]):
            return 0.0

        return None

    agent_stats = {}
    for agent_name, result_text, created_at in log_rows:
        stat = agent_stats.setdefault(
            agent_name,
            {"total_runs": 0, "last_run_at": None, "eff_values": []},
        )
        stat["total_runs"] += 1
        if not stat["last_run_at"] or (created_at and created_at > stat["last_run_at"]):
            stat["last_run_at"] = created_at
        eff = _parse_efficiency_percent(agent_name, result_text)
        if eff is not None:
            stat["eff_values"].append(eff)

    agent_rows = []
    for agent_name in sorted(agent_stats.keys()):
        stat = agent_stats[agent_name]
        if stat["eff_values"]:
            efficiency = round(sum(stat["eff_values"]) / len(stat["eff_values"]), 1)
        else:
            efficiency = 0.0
        agent_rows.append((agent_name, stat["total_runs"], efficiency, stat["last_run_at"]))

    score_by_agent = {
        "SyntaxAgent": avg_row[0] if avg_row else 0,
        "CodeAnalysisAgent": avg_row[1] if avg_row else 0,
        "RequirementAgent": avg_row[2] if avg_row else 0,
        "StructureAgent": avg_row[3] if avg_row else 0,
        "TestAgent": avg_row[4] if avg_row else 0,
        "LLMAgent": avg_row[5] if avg_row else 0,
    }

    alias_map = {
        "SyntaxAgent": "Build",
        "CodeAnalysisAgent": "Analysis",
        "RequirementAgent": "Quality",
        "StructureAgent": "Architecture",
        "TestAgent": "Validation",
        "LLMAgent": "Review",
    }

    now_utc = datetime.now(timezone.utc)
    agents = []
    for agent_name, total_runs, efficiency, last_run_at in agent_rows:
        total_runs = int(total_runs or 0)
        efficiency = float(efficiency or 0.0)
        if last_run_at and getattr(last_run_at, "tzinfo", None) is None:
            last_run_at = last_run_at.replace(tzinfo=timezone.utc)

        status = "Online"
        if not last_run_at:
            status = "No data"
        elif (now_utc - last_run_at) > timedelta(days=3):
            status = "Idle"

        agents.append(
            {
                "name": agent_name,
                "category": alias_map.get(agent_name, "General"),
                "status": status,
                "efficiency": efficiency,
                "total_runs": total_runs,
                "last_run_display": last_run_at.strftime("%d/%m/%Y %H:%M") if last_run_at else "--",
                "avg_score": round(float(score_by_agent.get(agent_name, 0) or 0), 1),
                "config": "Model mặc định, timeout 5s",
            }
        )

    total_runs_sum = sum(a[1] for a in agent_rows)
    active_count = sum(1 for a in agents if a["status"] == "Online")
    avg_efficiency = round(sum(a["efficiency"] for a in agents) / len(agents), 1) if agents else 0.0

    return templates.TemplateResponse(
        "quanlyai_giaovien.html",
        {
            "request": request,
            "teacher_name": teacher_name,
            "agents": agents,
            "stats": {
                "total_agents": len(agents),
                "active_agents": active_count,
                "total_runs": total_runs_sum,
                "avg_efficiency": avg_efficiency,
            },
            "today": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        },
    )


@app.get("/teacher/classrooms")
async def teacher_classrooms_page(request: Request):
    """Teacher page: manage classrooms, filter students and inspect score breakdown."""
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")

    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    with get_db() as conn:
        teacher_name = _get_teacher_name(conn, teacher_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.class_id,
                    c.class_name,
                    c.semester,
                    c.academic_year,
                    COUNT(DISTINCT e.student_id)::int AS total_students,
                    COUNT(DISTINCT s.submission_id)::int AS total_submissions,
                    AVG(COALESCE(es.total_score, 0))::float AS avg_score
                FROM classes c
                LEFT JOIN enrollments e ON e.class_id = c.class_id
                LEFT JOIN assignments a ON a.class_id = c.class_id
                LEFT JOIN submissions s ON s.assignment_id = a.assignment_id
                LEFT JOIN LATERAL (
                    SELECT total_score
                    FROM evaluation_sessions
                    WHERE submission_id = s.submission_id
                    ORDER BY created_at DESC
                    LIMIT 1
                ) es ON TRUE
                WHERE c.teacher_id = %s
                GROUP BY c.class_id, c.class_name, c.semester, c.academic_year
                ORDER BY c.class_name ASC
                """,
                (teacher_id,),
            )
            classroom_rows = cur.fetchall()

            cur.execute(
                """
                SELECT
                    c.class_id,
                    c.class_name,
                    st.student_id,
                    st.full_name,
                    st.email,
                    COUNT(DISTINCT s.submission_id)::int AS submission_count,
                    AVG(COALESCE(es.total_score, 0))::float AS avg_total_score,
                    AVG(COALESCE(es.syntax_score, 0))::float AS syntax_avg,
                    AVG(COALESCE(es.code_analysis_score, 0))::float AS analysis_avg,
                    AVG(COALESCE(es.requirement_score, 0))::float AS requirement_avg,
                    AVG(COALESCE(es.structure_score, 0))::float AS structure_avg,
                    AVG(COALESCE(es.test_score, 0))::float AS test_avg,
                    MAX(s.submitted_at) AS latest_submitted_at
                FROM classes c
                JOIN enrollments e ON e.class_id = c.class_id
                JOIN students st ON st.student_id = e.student_id
                LEFT JOIN assignments a ON a.class_id = c.class_id
                LEFT JOIN submissions s ON s.assignment_id = a.assignment_id AND s.student_id = st.student_id
                LEFT JOIN LATERAL (
                    SELECT total_score, syntax_score, code_analysis_score, requirement_score, structure_score, test_score
                    FROM evaluation_sessions
                    WHERE submission_id = s.submission_id
                    ORDER BY created_at DESC
                    LIMIT 1
                ) es ON TRUE
                WHERE c.teacher_id = %s
                GROUP BY c.class_id, c.class_name, st.student_id, st.full_name, st.email
                ORDER BY c.class_name, st.full_name
                """,
                (teacher_id,),
            )
            student_rows = cur.fetchall()

    classrooms = []
    for row in classroom_rows:
        classrooms.append(
            {
                "class_id": row[0],
                "class_name": row[1],
                "semester": row[2],
                "academic_year": row[3],
                "total_students": int(row[4] or 0),
                "total_submissions": int(row[5] or 0),
                "avg_score": round(float(row[6] or 0), 1),
            }
        )

    students = []
    for row in student_rows:
        latest_at = row[12]
        latest_display = latest_at.strftime("%d/%m/%Y %H:%M") if latest_at and hasattr(latest_at, "strftime") else "--"
        students.append(
            {
                "class_id": row[0],
                "class_name": row[1],
                "student_id": row[2],
                "student_name": row[3],
                "email": row[4],
                "submission_count": int(row[5] or 0),
                "avg_total_score": round(float(row[6] or 0), 1),
                "syntax_avg": round(float(row[7] or 0), 1),
                "analysis_avg": round(float(row[8] or 0), 1),
                "requirement_avg": round(float(row[9] or 0), 1),
                "structure_avg": round(float(row[10] or 0), 1),
                "test_avg": round(float(row[11] or 0), 1),
                "latest_submitted_at": latest_display,
            }
        )

    return templates.TemplateResponse(
        "quanlylophoc_giaovien.html",
        {
            "request": request,
            "teacher_name": teacher_name,
            "classrooms": classrooms,
            "students": students,
            "today": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        },
    )


@app.get("/teacher/reports")
async def teacher_reports_page(request: Request):
    """Teacher page: aggregated analytics dashboard for scores and common errors."""
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")

    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    with get_db() as conn:
        teacher_name = _get_teacher_name(conn, teacher_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*)::int,
                    AVG(COALESCE(es.total_score, 0))::float,
                    SUM(CASE WHEN COALESCE(es.total_score, 0) >= 90 THEN 1 ELSE 0 END)::int,
                    SUM(CASE WHEN COALESCE(es.total_score, 0) < 50 THEN 1 ELSE 0 END)::int
                FROM evaluation_sessions es
                JOIN submissions s ON s.submission_id = es.submission_id
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                WHERE c.teacher_id = %s
                """,
                (teacher_id,),
            )
            stat_row = cur.fetchone()

            cur.execute(
                """
                SELECT
                    to_char(date_trunc('month', s.submitted_at), 'MM/YYYY') AS month_label,
                    AVG(COALESCE(es.total_score, 0))::float AS avg_score
                FROM submissions s
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                LEFT JOIN LATERAL (
                    SELECT total_score
                    FROM evaluation_sessions
                    WHERE submission_id = s.submission_id
                    ORDER BY created_at DESC
                    LIMIT 1
                ) es ON TRUE
                WHERE c.teacher_id = %s
                GROUP BY date_trunc('month', s.submitted_at)
                ORDER BY date_trunc('month', s.submitted_at) DESC
                LIMIT 6
                """,
                (teacher_id,),
            )
            trend_rows = list(reversed(cur.fetchall()))

            cur.execute(
                """
                SELECT
                    CASE
                        WHEN lower(result) LIKE '%%syntax%%' THEN 'Lỗi cú pháp'
                        WHEN lower(result) LIKE '%%partial%%' THEN 'Đạt yêu cầu một phần'
                        WHEN lower(result) LIKE '%%fail%%' THEN 'Không đạt test'
                        WHEN lower(result) LIKE '%%error%%' THEN 'Lỗi runtime/logic'
                        ELSE 'Vấn đề khác'
                    END AS error_group,
                    COUNT(*)::int AS total_count
                FROM agent_logs al
                JOIN submissions s ON s.submission_id = al.submission_id
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                WHERE c.teacher_id = %s
                  AND (
                                            lower(al.result) LIKE '%%error%%'
                                            OR lower(al.result) LIKE '%%fail%%'
                                            OR lower(al.result) LIKE '%%partial%%'
                                            OR lower(al.result) LIKE '%%syntax%%'
                  )
                GROUP BY error_group
                ORDER BY total_count DESC
                LIMIT 5
                """,
                (teacher_id,),
            )
            error_rows = cur.fetchall()

            cur.execute(
                """
                SELECT
                    st.full_name,
                    AVG(COALESCE(es.total_score, 0))::float AS avg_score,
                    COUNT(*)::int AS submission_count
                FROM evaluation_sessions es
                JOIN submissions s ON s.submission_id = es.submission_id
                JOIN assignments a ON a.assignment_id = s.assignment_id
                JOIN classes c ON c.class_id = a.class_id
                JOIN students st ON st.student_id = s.student_id
                WHERE c.teacher_id = %s
                GROUP BY st.student_id, st.full_name
                HAVING COUNT(*) >= 1
                ORDER BY avg_score DESC, submission_count DESC
                LIMIT 10
                """,
                (teacher_id,),
            )
            top_rows = cur.fetchall()

    trend_labels = [r[0] for r in trend_rows]
    trend_values = [round(float(r[1] or 0), 1) for r in trend_rows]

    common_errors = [{"name": r[0], "count": int(r[1] or 0)} for r in error_rows]
    top_students = [
        {"name": r[0], "avg_score": round(float(r[1] or 0), 1), "submission_count": int(r[2] or 0)}
        for r in top_rows
    ]

    report_stats = {
        "total_evaluations": int(stat_row[0] or 0) if stat_row else 0,
        "avg_score": round(float(stat_row[1] or 0), 1) if stat_row else 0.0,
        "excellent_count": int(stat_row[2] or 0) if stat_row else 0,
        "at_risk_count": int(stat_row[3] or 0) if stat_row else 0,
    }

    return templates.TemplateResponse(
        "baocaotonghop_giaovien.html",
        {
            "request": request,
            "teacher_name": teacher_name,
            "stats": report_stats,
            "trend_labels_json": json.dumps(trend_labels, ensure_ascii=False),
            "trend_values_json": json.dumps(trend_values),
            "common_errors": common_errors,
            "top_students": top_students,
            "today": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        },
    )


def _parse_due_date_form(raw: str):
    """Chấp nhận datetime-local (YYYY-MM-DDTHH:MM) và một số biến thể."""
    s = (raw or "").strip()
    if not s:
        return None
    if " " in s and "T" not in s:
        s = s.replace(" ", "T", 1)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _format_due_for_datetime_local(dt) -> str:
    """Giá trị cho input type=datetime-local (giờ địa phương)."""
    if dt is None or not hasattr(dt, "strftime"):
        return ""
    try:
        if getattr(dt, "tzinfo", None) is not None:
            local = dt.astimezone()
        else:
            local = dt.replace(tzinfo=timezone.utc).astimezone()
        return local.strftime("%Y-%m-%dT%H:%M")
    except (TypeError, ValueError, OSError):
        return ""


def _resync_assignment_table_serials(cur) -> None:
    """Đưa các SERIAL của bảng assignment về sau MAX(id) — tránh lỗi sau import/restore."""
    cur.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('assignments', 'assignment_id')::regclass,
            (SELECT COALESCE(MAX(assignment_id), 1) FROM assignments)
        )
        """
    )
    cur.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('assignment_requirements', 'requirement_id')::regclass,
            (SELECT COALESCE(MAX(requirement_id), 1) FROM assignment_requirements)
        )
        """
    )
    cur.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('assignment_testcases', 'testcase_id')::regclass,
            (SELECT COALESCE(MAX(testcase_id), 1) FROM assignment_testcases)
        )
        """
    )


def _parse_teacher_assignment_form(form) -> tuple[dict | None, str | None]:
    """Parse multipart form tạo/sửa bài — trả (payload, None) hoặc (None, thông báo lỗi)."""
    try:
        class_id = int(form.get("class_id") or 0)
    except (TypeError, ValueError):
        return None, "Vui lòng chọn lớp hợp lệ."
    if class_id <= 0:
        return None, "Vui lòng chọn lớp."

    clean_title = (str(form.get("title") or "")).strip()
    if not clean_title:
        return None, "Tiêu đề bài tập không được để trống."

    description = (str(form.get("description") or "")).strip()
    programming_language = (str(form.get("programming_language") or "python")).strip().lower()

    parsed_due_date = _parse_due_date_form(str(form.get("due_date") or ""))
    if parsed_due_date is None:
        return None, "Hạn nộp không hợp lệ hoặc đang trống."

    req_texts = [str(x).strip() for x in form.getlist("requirement_texts")]
    req_weights_raw = form.getlist("requirement_weights")
    requirement_rows: list[tuple[str, float]] = []
    for i, rt in enumerate(req_texts):
        if not rt:
            continue
        w = 10.0
        if i < len(req_weights_raw):
            try:
                w = float(req_weights_raw[i] or 10)
            except (TypeError, ValueError):
                w = 10.0
        requirement_rows.append((rt, w))

    if not requirement_rows:
        return None, "Cần ít nhất một requirement có nội dung."

    tc_in = [str(x) for x in form.getlist("testcase_inputs")]
    tc_out = [str(x) for x in form.getlist("testcase_outputs")]
    tc_w_raw = form.getlist("testcase_weights")
    testcase_rows: list[tuple[str, str, float]] = []
    n = max(len(tc_in), len(tc_out))
    for idx in range(n):
        inp = (tc_in[idx] if idx < len(tc_in) else "").strip()
        out = (tc_out[idx] if idx < len(tc_out) else "").strip()
        if not inp or not out:
            continue
        tw = 10.0
        if idx < len(tc_w_raw):
            try:
                tw = float(tc_w_raw[idx] or 10)
            except (TypeError, ValueError):
                tw = 10.0
        testcase_rows.append((inp, out, tw))

    if not testcase_rows:
        return None, "Cần ít nhất một test case có input và expected output."

    selected_raw = form.getlist("selected_students")
    selected_ids: list[int] = []
    for x in selected_raw:
        try:
            selected_ids.append(int(x))
        except (TypeError, ValueError):
            continue

    return {
        "class_id": class_id,
        "clean_title": clean_title,
        "description": description,
        "programming_language": programming_language,
        "parsed_due_date": parsed_due_date,
        "requirement_rows": requirement_rows,
        "testcase_rows": testcase_rows,
        "selected_ids": selected_ids,
    }, None


@app.post("/teacher/assignment/new")
async def teacher_create_assignment(request: Request):
    """Tạo assignment từ multipart/form — parse getlist để tránh lỗi khi chỉ 1 trường lặp lại."""
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")

    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    def _fail(msg: str):
        return RedirectResponse(
            url="/teacher/assignment/new?error=" + quote(msg),
            status_code=303,
        )

    form = await request.form()
    payload, perr = _parse_teacher_assignment_form(form)
    if perr:
        return _fail(perr)
    class_id = payload["class_id"]
    clean_title = payload["clean_title"]
    description = payload["description"]
    programming_language = payload["programming_language"]
    parsed_due_date = payload["parsed_due_date"]
    requirement_rows = payload["requirement_rows"]
    testcase_rows = payload["testcase_rows"]
    selected_ids = payload["selected_ids"]

    with get_db() as conn:
        for attempt in range(2):
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM classes WHERE class_id = %s AND teacher_id = %s",
                        (class_id, teacher_id),
                    )
                    if not cur.fetchone():
                        conn.rollback()
                        return _fail("Bạn không có quyền tạo bài cho lớp này.")

                    cur.execute(
                        """
                        INSERT INTO assignments (class_id, title, description, due_date, programming_language)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING assignment_id
                        """,
                        (
                            class_id,
                            clean_title,
                            description,
                            parsed_due_date,
                            programming_language,
                        ),
                    )
                    assignment_id = cur.fetchone()[0]

                    for req_text, req_weight in requirement_rows:
                        cur.execute(
                            """
                            INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
                            VALUES (%s, %s, %s)
                            """,
                            (assignment_id, req_text, req_weight),
                        )

                    for inp, out, tw in testcase_rows:
                        cur.execute(
                            """
                            INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (assignment_id, inp, out, tw),
                        )

                    if not _table_exists(conn, "public.assignment_targets"):
                        cur.execute(
                            """
                            CREATE TABLE assignment_targets (
                                assignment_id INT REFERENCES assignments(assignment_id) ON DELETE CASCADE,
                                student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
                                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                                PRIMARY KEY (assignment_id, student_id)
                            )
                            """
                        )

                    cur.execute(
                        "SELECT student_id FROM enrollments WHERE class_id = %s",
                        (class_id,),
                    )
                    class_student_ids = {row[0] for row in cur.fetchall()}
                    picked_ids = {sid for sid in selected_ids if sid in class_student_ids}

                    if picked_ids and picked_ids != class_student_ids:
                        for sid in picked_ids:
                            cur.execute(
                                """
                                INSERT INTO assignment_targets (assignment_id, student_id)
                                SELECT %s, %s
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM assignment_targets t
                                    WHERE t.assignment_id = %s AND t.student_id = %s
                                )
                                """,
                                (assignment_id, sid, assignment_id, sid),
                            )

                conn.commit()
                break
            except psycopg2.errors.UniqueViolation as e:
                conn.rollback()
                if attempt == 0:
                    cname = getattr(getattr(e, "diag", None), "constraint_name", None) or ""
                    logger.warning(
                        "[teacher_create_assignment] UniqueViolation (%s); resyncing SERIALs, retry once",
                        cname or e,
                    )
                    try:
                        with conn.cursor() as cur:
                            _resync_assignment_table_serials(cur)
                    except Exception:
                        logger.exception(
                            "[teacher_create_assignment] could not resync SERIALs (run dev-archive/sql/resync_assignments_serial.sql)"
                        )
                        return _fail(
                            "Lỗi trùng khóa CSDL và không thể tự sửa sequence. "
                            "Chạy script dev-archive/sql/resync_assignments_serial.sql trong PostgreSQL rồi thử lại."
                        )
                    continue
                logger.exception("[teacher_create_assignment]")
                msg = (
                    "Lỗi trùng khóa khi lưu CSDL (không phải do sequence assignment_id). "
                    "Xem log server hoặc bật SCHOLARLY_SHOW_DB_ERROR=1 để có chi tiết."
                )
                if os.getenv("SCHOLARLY_SHOW_DB_ERROR", "").strip().lower() in (
                    "1",
                    "true",
                    "yes",
                ):
                    hint = str(e).replace("\r", " ").replace("\n", " ").strip()[:400]
                    if hint:
                        msg = f"{msg} (chi tiết dev: {hint})"
                return _fail(msg)
            except Exception as e:
                conn.rollback()
                logger.exception("[teacher_create_assignment]")
                msg = "Lỗi khi lưu vào CSDL. Kiểm tra kết nối PostgreSQL và log server."
                if os.getenv("SCHOLARLY_SHOW_DB_ERROR", "").strip().lower() in (
                    "1",
                    "true",
                    "yes",
                ):
                    hint = str(e).replace("\r", " ").replace("\n", " ").strip()[:400]
                    if hint:
                        msg = f"{msg} (chi tiết dev: {hint})"
                return _fail(msg)

    return RedirectResponse(url="/teacher-dashboard", status_code=303)


@app.get("/teacher/assignment/{assignment_id}/edit")
async def teacher_edit_assignment_page(request: Request, assignment_id: int):
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")
    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    err = (request.query_params.get("error") or "").strip()

    with get_db() as conn:
        teacher_name = _get_teacher_name(conn, teacher_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.assignment_id, a.class_id, a.title, a.description, a.due_date,
                       a.programming_language, c.class_name
                FROM assignments a
                JOIN classes c ON c.class_id = a.class_id
                WHERE a.assignment_id = %s AND c.teacher_id = %s
                """,
                (assignment_id, teacher_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy bài tập hoặc không có quyền.")
            keys = [
                "assignment_id",
                "class_id",
                "title",
                "description",
                "due_date",
                "programming_language",
                "class_name",
            ]
            assignment = dict(zip(keys, row))

            cur.execute(
                """
                SELECT requirement_id, requirement_text, weight
                FROM assignment_requirements
                WHERE assignment_id = %s
                ORDER BY requirement_id
                """,
                (assignment_id,),
            )
            requirements = [
                {"requirement_id": r[0], "requirement_text": r[1], "weight": float(r[2] or 10)}
                for r in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT testcase_id, input_data, expected_output, score_weight
                FROM assignment_testcases
                WHERE assignment_id = %s
                ORDER BY testcase_id
                """,
                (assignment_id,),
            )
            testcases = [
                {
                    "testcase_id": r[0],
                    "input_data": r[1] or "",
                    "expected_output": r[2] or "",
                    "score_weight": float(r[3] or 10),
                }
                for r in cur.fetchall()
            ]

            targeted: set[int] = set()
            if _table_exists(conn, "public.assignment_targets"):
                cur.execute(
                    "SELECT student_id FROM assignment_targets WHERE assignment_id = %s",
                    (assignment_id,),
                )
                targeted = {int(r[0]) for r in cur.fetchall()}

            cur.execute(
                """
                SELECT c.class_id, c.class_name, c.semester, c.academic_year,
                       COUNT(e.student_id) AS total_students
                FROM classes c
                LEFT JOIN enrollments e ON e.class_id = c.class_id
                WHERE c.teacher_id = %s
                GROUP BY c.class_id, c.class_name, c.semester, c.academic_year
                ORDER BY c.class_name ASC
                """,
                (teacher_id,),
            )
            class_rows = cur.fetchall()

            cur.execute(
                """
                SELECT e.class_id, s.student_id, s.full_name, s.email
                FROM enrollments e
                JOIN students s ON s.student_id = e.student_id
                JOIN classes c ON c.class_id = e.class_id
                WHERE c.teacher_id = %s
                ORDER BY e.class_id, s.full_name
                """,
                (teacher_id,),
            )
            student_rows = cur.fetchall()

    classes = [
        {
            "class_id": r[0],
            "class_name": r[1],
            "semester": r[2],
            "academic_year": r[3],
            "total_students": int(r[4] or 0),
        }
        for r in class_rows
    ]

    students_by_class: dict[str, list] = {}
    for enr_class_id, student_id, full_name, email in student_rows:
        students_by_class.setdefault(str(enr_class_id), []).append(
            {"student_id": student_id, "full_name": full_name, "email": email}
        )

    cid = int(assignment["class_id"])
    class_student_ids = {s["student_id"] for s in students_by_class.get(str(cid), [])}
    if targeted:
        initial_checked_ids = {i for i in targeted if i in class_student_ids}
    else:
        initial_checked_ids = set(class_student_ids)

    due_input = _format_due_for_datetime_local(assignment.get("due_date"))

    return templates.TemplateResponse(
        "suabaitap_giaovien.html",
        {
            "request": request,
            "teacher_name": teacher_name,
            "assignment": assignment,
            "requirements": requirements,
            "testcases": testcases,
            "classes": classes,
            "students_by_class_json": json.dumps(students_by_class, ensure_ascii=False),
            "initial_checked_json": json.dumps(list(initial_checked_ids)),
            "due_date_input": due_input,
            "form_error": err,
        },
    )


@app.post("/teacher/assignment/{assignment_id}/edit")
async def teacher_update_assignment(request: Request, assignment_id: int):
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")
    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    def _fail(msg: str):
        return RedirectResponse(
            url=f"/teacher/assignment/{assignment_id}/edit?error=" + quote(msg),
            status_code=303,
        )

    form = await request.form()
    payload, perr = _parse_teacher_assignment_form(form)
    if perr:
        return _fail(perr)

    class_id = payload["class_id"]
    clean_title = payload["clean_title"]
    description = payload["description"]
    programming_language = payload["programming_language"]
    parsed_due_date = payload["parsed_due_date"]
    requirement_rows = payload["requirement_rows"]
    testcase_rows = payload["testcase_rows"]
    selected_ids = payload["selected_ids"]

    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT a.class_id
                    FROM assignments a
                    JOIN classes c ON c.class_id = a.class_id
                    WHERE a.assignment_id = %s AND c.teacher_id = %s
                    """,
                    (assignment_id, teacher_id),
                )
                row = cur.fetchone()
                if not row:
                    conn.rollback()
                    return _fail("Không tìm thấy bài tập hoặc không có quyền.")
                db_class_id = int(row[0])
                if class_id != db_class_id:
                    conn.rollback()
                    return _fail("Không được đổi lớp của bài tập.")

                cur.execute(
                    """
                    UPDATE assignments
                    SET title = %s, description = %s, due_date = %s, programming_language = %s
                    WHERE assignment_id = %s
                    """,
                    (
                        clean_title,
                        description,
                        parsed_due_date,
                        programming_language,
                        assignment_id,
                    ),
                )

                cur.execute(
                    "DELETE FROM assignment_requirements WHERE assignment_id = %s",
                    (assignment_id,),
                )
                for req_text, req_weight in requirement_rows:
                    cur.execute(
                        """
                        INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
                        VALUES (%s, %s, %s)
                        """,
                        (assignment_id, req_text, req_weight),
                    )

                cur.execute(
                    "DELETE FROM assignment_testcases WHERE assignment_id = %s",
                    (assignment_id,),
                )
                for inp, out, tw in testcase_rows:
                    cur.execute(
                        """
                        INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (assignment_id, inp, out, tw),
                    )

                if _table_exists(conn, "public.assignment_targets"):
                    cur.execute(
                        "DELETE FROM assignment_targets WHERE assignment_id = %s",
                        (assignment_id,),
                    )
                    cur.execute(
                        "SELECT student_id FROM enrollments WHERE class_id = %s",
                        (class_id,),
                    )
                    class_student_ids = {int(r[0]) for r in cur.fetchall()}
                    picked_ids = {int(sid) for sid in selected_ids if int(sid) in class_student_ids}
                    if picked_ids and picked_ids != class_student_ids:
                        for sid in picked_ids:
                            cur.execute(
                                """
                                INSERT INTO assignment_targets (assignment_id, student_id)
                                VALUES (%s, %s)
                                """,
                                (assignment_id, sid),
                            )

            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.exception("[teacher_update_assignment]")
            msg = "Lỗi khi lưu thay đổi. Kiểm tra log server."
            if os.getenv("SCHOLARLY_SHOW_DB_ERROR", "").strip().lower() in (
                "1",
                "true",
                "yes",
            ):
                hint = str(e).replace("\r", " ").replace("\n", " ").strip()[:400]
                if hint:
                    msg = f"{msg} ({hint})"
            return _fail(msg)

    return RedirectResponse(url="/teacher/submissions?saved=1", status_code=303)


@app.post("/teacher/assignment/{assignment_id}/delete")
async def teacher_delete_assignment(request: Request, assignment_id: int):
    role = request.cookies.get("role")
    if role != "teacher":
        raise HTTPException(status_code=401, detail="Chỉ giáo viên mới được truy cập")
    try:
        teacher_id = int(request.cookies.get("user_id") or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM assignments a
                    JOIN classes c ON c.class_id = a.class_id
                    WHERE a.assignment_id = %s AND c.teacher_id = %s
                    """,
                    (assignment_id, teacher_id),
                )
                if not cur.fetchone():
                    conn.rollback()
                    raise HTTPException(status_code=404, detail="Không tìm thấy bài tập.")
                cur.execute("DELETE FROM assignments WHERE assignment_id = %s", (assignment_id,))
            conn.commit()
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            logger.exception("[teacher_delete_assignment]")
            return RedirectResponse(
                url="/teacher/submissions?error=" + quote("Không thể xóa bài tập: " + str(e)[:240]),
                status_code=303,
            )

    return RedirectResponse(url="/teacher/submissions?deleted=1", status_code=303)


@app.get("/student-dashboard")
async def student_page(request: Request):
    role = request.cookies.get("role")
    student_id = None
    if role == "student":
        try:
            student_id = int(request.cookies.get("user_id") or "")
        except ValueError:
            student_id = None

    filter_class_id = _parse_class_id_query(request)

    with get_db() as conn:
        assignments_all = _fetch_assignments(conn, student_id=student_id)
        subject_filters = _subject_filters_from_assignments(assignments_all)
        valid_ids = {f["class_id"] for f in subject_filters}
        if filter_class_id is not None and filter_class_id not in valid_ids:
            filter_class_id = None
        assignments = _filter_assignments_by_class(assignments_all, filter_class_id)
        student_profile = _fetch_student_detailed_profile(conn, student_id=student_id)
        upcoming_deadlines = _build_upcoming_deadlines(assignments, limit=3)
        latest_score = _fetch_latest_student_score(conn, student_id=student_id)
        student_progress = _compute_student_progress(conn, student_id=student_id, assignments=assignments)

    nearest_due_display = "--"
    pending_ids = student_progress.get("pending_assignment_ids", set())
    if assignments:
        for assignment in assignments:
            assignment_id = assignment.get("assignment_id")
            if assignment_id not in pending_ids:
                continue
            due_date_display = assignment.get("due_date_display")
            status_label = assignment.get("status_label")
            if due_date_display and status_label != "Quá hạn":
                nearest_due_display = due_date_display
                break

        if nearest_due_display == "--":
            for assignment in assignments:
                assignment_id = assignment.get("assignment_id")
                if assignment_id not in pending_ids:
                    continue
                due_date_display = assignment.get("due_date_display")
                if due_date_display:
                    nearest_due_display = due_date_display
                    break

    dashboard_insight = _student_dashboard_insight(
        student_profile, student_progress, latest_score
    )

    return templates.TemplateResponse(
        "bangdkSV.html",
        {
            "request": request,
            "assignments": assignments,
            "student_profile": student_profile,
            "upcoming_deadlines": upcoming_deadlines,
            "latest_score": latest_score,
            "student_progress": student_progress,
            "nearest_due_display": nearest_due_display,
            "greeting": _student_time_greeting(),
            "dashboard_insight": dashboard_insight,
            "subject_filters": subject_filters,
            "selected_class_id": filter_class_id,
        },
    )


@app.get("/student-assignments")
async def student_assignments_page(request: Request):
    role = request.cookies.get("role")
    student_id = None
    if role == "student":
        try:
            student_id = int(request.cookies.get("user_id") or "")
        except ValueError:
            student_id = None

    filter_class_id = _parse_class_id_query(request)

    with get_db() as conn:
        assignments_all = _fetch_assignments(conn, student_id=student_id)
        subject_filters = _subject_filters_from_assignments(assignments_all)
        valid_ids = {f["class_id"] for f in subject_filters}
        if filter_class_id is not None and filter_class_id not in valid_ids:
            filter_class_id = None
        assignments = _filter_assignments_by_class(assignments_all, filter_class_id)
        student_profile = _fetch_student_detailed_profile(conn, student_id=student_id)
        student_progress = _compute_student_progress(conn, student_id=student_id, assignments=assignments)

    pending_ids = student_progress.get("pending_assignment_ids", set())
    pending_assignments = [
        a for a in assignments if a.get("assignment_id") in pending_ids
    ]

    overdue_count = sum(1 for a in pending_assignments if a.get("status_label") == "Quá hạn")
    urgent_count = sum(1 for a in pending_assignments if a.get("status_label") == "Cần nộp gấp")

    return templates.TemplateResponse(
        "lichsunopbai_sinhvien.html",
        {
            "request": request,
            "student_profile": student_profile,
            "student_progress": student_progress,
            "pending_assignments": pending_assignments,
            "overdue_count": overdue_count,
            "urgent_count": urgent_count,
            "subject_filters": subject_filters,
            "selected_class_id": filter_class_id,
        },
    )


@app.get("/student-submission-history")
async def student_submission_history_page(request: Request, page: int = 1):
    role = request.cookies.get("role")
    if role != "student":
        raise HTTPException(status_code=401, detail="Chỉ sinh viên mới được truy cập")

    student_id = None
    try:
        student_id = int(request.cookies.get("user_id") or "")
    except ValueError:
        student_id = None

    filter_class_id = _parse_class_id_query(request)

    page_size = 10
    safe_page = max(page, 1)
    offset = (safe_page - 1) * page_size

    with get_db() as conn:
        assignments_all = _fetch_assignments(conn, student_id=student_id)
        subject_filters = _subject_filters_from_assignments(assignments_all)
        valid_ids = {f["class_id"] for f in subject_filters}
        if filter_class_id is not None and filter_class_id not in valid_ids:
            filter_class_id = None

        student_profile = _fetch_student_detailed_profile(conn, student_id=student_id)
        submissions, total_submissions = _fetch_student_submission_history(
            conn,
            student_id=student_id,
            limit=page_size,
            offset=offset,
            class_id=filter_class_id,
        )
        submission_stats = _fetch_student_submission_rollups(conn, student_id=student_id)

    total_pages = (total_submissions + page_size - 1) // page_size if total_submissions else 1
    current_page = min(safe_page, total_pages)
    offset = (current_page - 1) * page_size
    if current_page != safe_page and total_submissions > 0:
        with get_db() as conn:
            submissions, total_submissions = _fetch_student_submission_history(
                conn,
                student_id=student_id,
                limit=page_size,
                offset=offset,
                class_id=filter_class_id,
            )

    successful_submissions = sum(1 for s in submissions if s.get("status_label") == "Thành công")
    success_rate = round((successful_submissions / total_submissions) * 100, 1) if total_submissions else 0
    has_prev = current_page > 1
    has_next = current_page < total_pages
    start_item = (current_page - 1) * page_size + 1 if total_submissions > 0 else 0
    end_item = min(current_page * page_size, total_submissions)

    return templates.TemplateResponse(
        "lichsunopbaicuasinhvien_sinhvien.html",
        {
            "request": request,
            "student_profile": student_profile,
            "submissions": submissions,
            "total_submissions": total_submissions,
            "success_rate": success_rate,
            "current_page": current_page,
            "total_pages": total_pages,
            "has_prev": has_prev,
            "has_next": has_next,
            "prev_page": current_page - 1,
            "next_page": current_page + 1,
            "start_item": start_item,
            "end_item": end_item,
            "submission_stats": submission_stats,
            "subject_filters": subject_filters,
            "selected_class_id": filter_class_id,
        },
    )


@app.get("/student-results")
async def student_results_page(request: Request):
    role = request.cookies.get("role")
    if role != "student":
        raise HTTPException(status_code=401, detail="Chỉ sinh viên mới được truy cập")

    try:
        student_id = int(request.cookies.get("user_id") or "")
    except ValueError:
        student_id = None

    filter_class_id = _parse_class_id_query(request)

    with get_db() as conn:
        assignments_all = _fetch_assignments(conn, student_id=student_id)
        subject_filters = _subject_filters_from_assignments(assignments_all)
        valid_ids = {f["class_id"] for f in subject_filters}
        if filter_class_id is not None and filter_class_id not in valid_ids:
            filter_class_id = None
        student_profile = _fetch_student_detailed_profile(conn, student_id=student_id)
        graded_all = _fetch_student_graded_assignments(conn, student_id=student_id)
        graded_assignments = [
            g for g in graded_all
            if filter_class_id is None or g.get("class_id") == filter_class_id
        ]
        latest_score = _fetch_latest_student_score(conn, student_id=student_id)
        assignments = _filter_assignments_by_class(assignments_all, filter_class_id)
        student_progress = _compute_student_progress(conn, student_id=student_id, assignments=assignments)

    return templates.TemplateResponse(
        "ketquahoctap_sinhvien.html",
        {
            "request": request,
            "student_profile": student_profile,
            "latest_score": latest_score,
            "student_progress": student_progress,
            "graded_assignments": graded_assignments,
            "subject_filters": subject_filters,
            "selected_class_id": filter_class_id,
        },
    )

@app.get("/check-db")
def check_db():
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "Kết nối DB thành công!"}
    except Exception as e:
        return {"status": "Lỗi kết nối DB", "detail": str(e)}


@app.get("/assignment/{assignment_id}")
async def assignment_submission_page(request: Request, assignment_id: int):
    """Hiển thị trang nộp bài với thông tin chi tiết về bài tập"""
    student_profile = None
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Lấy thông tin chi tiết về bài tập
                cur.execute("""
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
                    WHERE a.assignment_id = %s
                """, (assignment_id,))
                row = cur.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Bài tập không tồn tại")

            # Chuyển đổi kết quả thành dictionary
            columns = ['assignment_id', 'title', 'description', 'due_date', 'programming_language',
                       'class_id', 'class_name', 'teacher_name']
            assignment = dict(zip(columns, row))

            requirements = []
            testcases = []
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT requirement_text, weight
                    FROM assignment_requirements
                    WHERE assignment_id = %s
                    ORDER BY requirement_id
                    """,
                    (assignment_id,),
                )
                for rrow in cur.fetchall():
                    requirements.append(
                        {"requirement_text": rrow[0] or "", "weight": float(rrow[1]) if rrow[1] is not None else 10.0}
                    )
                cur.execute(
                    """
                    SELECT input_data, expected_output, score_weight
                    FROM assignment_testcases
                    WHERE assignment_id = %s
                    ORDER BY testcase_id
                    """,
                    (assignment_id,),
                )
                for trow in cur.fetchall():
                    testcases.append(
                        {
                            "input_data": trow[0] if trow[0] is not None else "",
                            "expected_output": trow[1] if trow[1] is not None else "",
                            "score_weight": float(trow[2]) if trow[2] is not None else 10.0,
                        }
                    )

            # Student can open this assignment only if belongs to class/target list.
            if request.cookies.get("role") == "student":
                try:
                    student_id = int(request.cookies.get("user_id") or "")
                except (TypeError, ValueError):
                    student_id = None

                if not student_id:
                    raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ")

                if not _is_student_assigned(conn, assignment_id=assignment_id, student_id=student_id):
                    raise HTTPException(status_code=403, detail="Bạn không thuộc danh sách được giao bài này")

                student_profile = _fetch_student_detailed_profile(conn, student_id=student_id)

        # Định dạng ngày hạn
        due_date = assignment.get("due_date")
        if due_date is not None and hasattr(due_date, "strftime"):
            assignment["due_date_display"] = due_date.strftime("%d/%m/%Y, %H:%M")
        else:
            assignment["due_date_display"] = str(due_date)

        return templates.TemplateResponse(
            "trangnopbai.html",
            {
                "request": request,
                "assignment": assignment,
                "student_profile": student_profile,
                "requirements": requirements,
                "testcases": testcases,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


# Định nghĩa extension file được phép theo từng ngôn ngữ
ALLOWED_EXTENSIONS = {
    'python': ['.py'],
    'java': ['.java'],
    'cpp': ['.cpp', '.cc', '.cxx'],
    'javascript': ['.js']
}


# ==========================================
# HỆ THỐNG CHẤM ĐIỂM THỰC TẾ (REAL EVALUATION SYSTEM)
# ==========================================

class SyntaxAgent:
    """Kiểm tra lỗi cú pháp Python"""
    
    @staticmethod
    def evaluate(code: str) -> tuple[bool, str, float]:
        """
        Kiểm tra cú pháp code Python
        Returns: (is_valid, error_msg, score)
        """
        try:
            ast.parse(code)
            return True, "", 25.0  # Toàn bộ điểm cú pháp
        except SyntaxError as e:
            error_msg = f"Lỗi cú pháp tại dòng {e.lineno}: {e.msg}"
            return False, error_msg, 0.0
        except Exception as e:
            return False, f"Lỗi phân tích code: {str(e)}", 0.0


class RequirementAgent:
    """Kiểm tra xem code có memenuhi các yêu cầu"""
    
    @staticmethod
    def evaluate(code: str, requirements: list) -> tuple[float, list]:
        """
        Kiểm tra xem code có meet requirements từ assignment
        requirements: list of (requirement_text, weight)
        Returns: (score, details_list)
        """
        score = 0.0
        details = []
        # Convert weights to float to avoid Decimal type issues
        total_weight = sum(float(w) for _, w in requirements) if requirements else 0
        
        if not requirements or total_weight == 0:
            # Nếu không có requirements, cho điểm đầu tiên
            return 20.0, ["Không có yêu cầu cụ thể để kiểm tra"]
        
        code_lower = code.lower()
        
        for idx, (requirement_text, weight) in enumerate(requirements):
            requirement_lower = requirement_text.lower()
            weight = float(weight)  # Convert Decimal to float
            found = False
            
            # Tách kiểm tra input, print, +, def rõ ràng
            if "input" in requirement_lower:
                if "input(" in code_lower:
                    score += weight
                    details.append(f"✓ {requirement_text}")
                    found = True
                else:
                    details.append(f"✗ {requirement_text} - Missing input()")
                    
            elif "print" in requirement_lower:
                if "print(" in code_lower:
                    score += weight
                    details.append(f"✓ {requirement_text}")
                    found = True
                else:
                    details.append(f"✗ {requirement_text} - Missing print()")
                    
            elif "+" in requirement_lower or "cộng" in requirement_lower:
                if "+" in code:
                    score += weight
                    details.append(f"✓ {requirement_text}")
                    found = True
                else:
                    details.append(f"✗ {requirement_text} - Missing +")
                    
            elif "def " in requirement_lower or "function" in requirement_lower or "hàm" in requirement_lower:
                if "def " in code_lower:
                    score += weight
                    details.append(f"✓ {requirement_text}")
                    found = True
                else:
                    details.append(f"✗ {requirement_text} - Missing function")
                    
            else:
                # Generic keyword matching
                keywords = [kw.lower() for kw in requirement_text.split() if len(kw) > 2]
                if any(kw in code_lower for kw in keywords):
                    score += weight
                    details.append(f"✓ {requirement_text}")
                    found = True
                else:
                    details.append(f"✗ {requirement_text}")
        
        # Normalize to 0-25
        if total_weight > 0:
            normalized_score = (score / total_weight) * 25
        else:
            normalized_score = 20.0
            
        return min(normalized_score, 25.0), details[:2]  # Chỉ hiển thị 2 chi tiết


class StructureAgent:
    """Đánh giá chất lượng cấu trúc code"""
    
    @staticmethod
    def evaluate(code: str) -> tuple[float, list]:
        """
        Đánh giá cấu trúc code
        Tiêu chí: comments, naming conventions, indentation, readability
        Returns: (score, details)
        """
        score = 5.0  # Base score
        details = []
        max_score = 25.0
        
        # 1. Kiểm tra comments (max 6 điểm)
        num_comments = code.count('#')
        num_lines = len(code.split('\n'))
        if num_lines > 0:
            comment_ratio = num_comments / num_lines
            if comment_ratio >= 0.3:  # 30% lines có comments
                score += 6
                details.append("✓ Comments tốt")
            elif comment_ratio >= 0.1:  # 10% lines
                score += 3
                details.append("✓ Có comments")
            
        # 2. Kiểm tra indentation (max 6 điểm)
        lines = code.split('\n')
        indented_lines = sum(1 for line in lines if line and line[0] in ' \t')
        if indented_lines > 0:
            score += 6
            details.append("✓ Indentation đẹp")
            
        # 3. Kiểm tra tên biến (max 6 điểm)
        # Tìm biến assignment (a=, x=, num=, etc.)
        var_pattern = r'([a-zA-Z_]\w*)\s*='
        variables = re.findall(var_pattern, code)
        
        if variables:
            # Tính % biến có tên tốt (>2 ký tự)
            good_vars = [v for v in variables if len(v) > 1]
            if len(good_vars) >= len(variables) * 0.5 or len([v for v in variables if len(v) > 2]) > 0:
                score += 6
                details.append("✓ Tên biến rõ ràng")
            elif len(good_vars) > 0:
                score += 3
                details.append("✓ Một số tên biến tốt")
        else:
            # Không có assignment = code đơn giản
            score += 2
            
        # 4. Kiểm tra line length (max 3 điểm)
        long_lines = sum(1 for line in lines if len(line) > 120)
        if long_lines == 0 and len(lines) > 0:
            score += 3
            details.append("✓ Độ dài dòng hợp lý")
            
        # 5. Kiểm tra code structure - functions/classes (max 4 điểm)
        if 'def ' in code or 'class ' in code:
            score += 4
            details.append("✓ Có functions/classes")
        
        return min(score, max_score), details[:3]


class TestAgent:
    """Chạy test cases và so sánh output"""
    
    @staticmethod
    def evaluate(code: str, testcases: list) -> tuple[float, list]:
        """
        Chạy code với test cases
        testcases: list of (input_data, expected_output, score_weight) or (input_data, expected_output)
        Returns: (score, details)
        """
        if not testcases:
            return 20.0, ["Không có test cases để kiểm tra"]
        
        passed = 0
        failed = 0
        details = []
        
        def unescape_string(s):
            """Decode escape sequences like \\n to actual newlines"""
            if not s:
                return ""
            # Handle common escape sequences
            try:
                # Use unicode escape decoding for \\n, \\t, etc.
                return bytes(str(s), 'utf-8').decode('unicode_escape')
            except:
                return str(s)
        
        for test_idx, test_case in enumerate(testcases, 1):
            # Handle both tuples (3 items with weight) and (2 items without)
            if len(test_case) >= 2:
                input_data = test_case[0]
                expected_output = test_case[1]
            else:
                continue
            
            try:
                # Unescape input data (convert \\n to actual newline)
                unescaped_input = unescape_string(input_data)
                unescaped_expected = unescape_string(expected_output)
                
                # Chạy code với input - set UTF-8 encoding for Python
                import os
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run(
                    ['python', '-c', code],
                    input=unescaped_input.encode('utf-8') if unescaped_input else b'',
                    capture_output=True,
                    timeout=5,
                    text=False,
                    env=env
                )
                
                actual_output = result.stdout.decode('utf-8', errors='ignore').strip()
                expected = unescaped_expected.strip() if unescaped_expected else ""
                
                # Try exact match first
                if actual_output == expected:
                    passed += 1
                    details.append(f"✓ Test case #{test_idx}: PASS")
                else:
                    # If exact match fails, try extracting just numbers/values from output
                    # This handles cases where input() prompts are printed before output
                    import re
                    
                    # Extract the last line that contains the expected result
                    lines = actual_output.split('\n')
                    
                    # Try to find a line that matches or ends with expected
                    match_found = False
                    for line in reversed(lines):
                        line = line.strip()
                        if line == expected or line.endswith(expected):
                            match_found = True
                            break
                        # Also try extracting just the number if expected is numeric
                        if expected.replace('.', '').replace('-', '').isdigit():
                            # Extract the last number from this line
                            numbers = re.findall(r'-?\d+\.?\d*', line)
                            if numbers and numbers[-1] == expected:
                                match_found = True
                                break
                    
                    if match_found:
                        passed += 1
                        details.append(f"✓ Test case #{test_idx}: PASS")
                    else:
                        failed += 1
                        details.append(f"✗ Test case #{test_idx}: FAIL")
                    
            except subprocess.TimeoutExpired:
                failed += 1
                details.append(f"✗ Test case #{test_idx}: TIMEOUT")
            except Exception as e:
                failed += 1
                details.append(f"✗ Test case #{test_idx}: ERROR")
        
        # Tính điểm dựa trên số test case pass
        if testcases:
            test_score = (passed / len(testcases)) * 25
        else:
            test_score = 0.0
        
        return test_score, details[:3]  # Chỉ hiển thị 3 chi tiết


@app.post("/submit-assignment/{assignment_id}")
async def submit_assignment(
    request: Request,
    assignment_id: int,
    programming_language: str = Form(...),
    source_code: str = Form(...),
    file: UploadFile = File(None)
):
    """
    Xử lý submission bài tập
    - Nếu gửi file: kiểm tra extension file phải đúng định dạng
    - Nếu gửi code text: sử dụng code text
    - Phải có ít nhất một trong hai
    """
    try:
        # Lấy user_id từ cookie
        try:
            student_id = int(request.cookies.get("user_id") or "")
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Phải đăng nhập trước")
        
        # Kiểm tra bài tập tồn tại
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT assignment_id, programming_language FROM assignments WHERE assignment_id = %s",
                    (assignment_id,)
                )
                assignment_row = cur.fetchone()
        
        if not assignment_row:
            raise HTTPException(status_code=404, detail="Bài tập không tồn tại")
        
        # Kiểm tra ngôn ngữ lập trình có hợp lệ không
        if programming_language not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Ngôn ngữ lập trình không hợp lệ")
        
        code_content = None
        
        # Nếu có file được gửi
        if file and file.filename:
            # Kiểm tra extension file
            file_extension = '.' + file.filename.split('.')[-1].lower()
            allowed_exts = ALLOWED_EXTENSIONS[programming_language]
            
            if file_extension not in allowed_exts:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File không đúng định dạng. Cho phép: {', '.join(allowed_exts)} cho {programming_language}"
                )
            
            # Đọc nội dung file
            file_content = await file.read()
            
            # Kiểm tra kích thước file (max 5MB)
            if len(file_content) > 5 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File quá lớn (tối đa 5MB)")
            
            try:
                code_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="File phải là text file hợp lệ")
        
        # Nếu không có file, sử dụng code text
        if not code_content:
            if not source_code or source_code.strip() == "":
                raise HTTPException(status_code=400, detail="Phải gửi file hoặc nhập code")
            code_content = source_code
        
        # Kiểm tra code không rỗng
        if not code_content.strip():
            raise HTTPException(status_code=400, detail="Code không được để trống")
        
        # Lưu submission vào database
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO submissions (assignment_id, student_id, source_code, submitted_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING submission_id
                """, (assignment_id, student_id, code_content))
                submission_id = cur.fetchone()[0]
            conn.commit()
        
        # Chuyển hướng tới trang kết quả
        return RedirectResponse(
            url=f"/submission-result/{submission_id}",
            status_code=303
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý submission: {str(e)}")


@app.get("/submission-result/{submission_id}")
async def submission_result_page(request: Request, submission_id: int):
    """Hiển thị trang kết quả sau khi nộp bài (sinh viên: bài của mình; giáo viên: bài thuộc lớp mình dạy)."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        s.submission_id,
                        s.assignment_id,
                        s.student_id,
                        s.source_code,
                        s.submitted_at,
                        a.title,
                        a.programming_language,
                        st.full_name AS student_name
                    FROM submissions s
                    JOIN assignments a ON a.assignment_id = s.assignment_id
                    JOIN students st ON st.student_id = s.student_id
                    WHERE s.submission_id = %s
                    """,
                    (submission_id,),
                )
                row = cur.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Submission không tồn tại")

            columns = [
                "submission_id",
                "assignment_id",
                "student_id",
                "source_code",
                "submitted_at",
                "title",
                "programming_language",
                "student_name",
            ]
            submission = dict(zip(columns, row))
            viewer_role = _submission_result_viewer_role(
                conn, request, submission["student_id"], submission["assignment_id"]
            )

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        session_id,
                        syntax_score,
                        code_analysis_score,
                        structure_score,
                        requirement_score,
                        test_score,
                        llm_score,
                        total_score,
                        final_feedback,
                        agent_details,
                        created_at
                    FROM evaluation_sessions
                    WHERE submission_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (submission_id,),
                )
                eval_row = cur.fetchone()

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT assignment_id, title, description, due_date, programming_language
                    FROM assignments
                    WHERE assignment_id = %s
                    """,
                    (submission["assignment_id"],),
                )
                assign_row = cur.fetchone()
        
        assignment = None
        if assign_row:
            assign_cols = ['assignment_id', 'title', 'description', 'due_date', 'programming_language']
            assignment = dict(zip(assign_cols, assign_row))
        
        # Format result object cho template
        evaluation = None
        agent_details = None
        
        if eval_row:
            # eval_row: (session_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details, created_at)
            evaluation = {
                'session_id': eval_row[0],
                'syntax_score': float(eval_row[1]) if eval_row[1] else 0,
                'code_analysis_score': float(eval_row[2]) if eval_row[2] else 0,
                'structure_score': float(eval_row[3]) if eval_row[3] else 0,
                'requirement_score': float(eval_row[4]) if eval_row[4] else 0,
                'test_score': float(eval_row[5]) if eval_row[5] else 0,
                'llm_score': float(eval_row[6]) if eval_row[6] else 0,
                'total_score': float(eval_row[7]) if eval_row[7] else 0,
                'final_feedback': eval_row[8],
                'created_at': eval_row[10]
            }
            
            # Parse agent_details JSONB safely.
            # psycopg2 may return JSONB as dict directly (not JSON string).
            agent_details_json = eval_row[9]
            try:
                if not agent_details_json:
                    agent_details = {}
                elif isinstance(agent_details_json, dict):
                    agent_details = agent_details_json
                elif isinstance(agent_details_json, str):
                    agent_details = json.loads(agent_details_json)
                else:
                    # Fallback for unexpected JSONB adapters
                    agent_details = json.loads(str(agent_details_json))
            except Exception:
                agent_details = {}
            
            # Enrich agent_details with calculated fields
            if 'requirement' in agent_details:
                req = agent_details['requirement']
                details = req.get('details', []) or []

                fulfilled = req.get('fulfilled_count', req.get('fulfilled'))
                total = req.get('total_count', req.get('total'))

                # Prefer explicit summary format like "1/4" if present.
                for item in details:
                    if not isinstance(item, str):
                        continue
                    match = re.search(r"(\d+)\s*/\s*(\d+)", item)
                    if match:
                        fulfilled = int(match.group(1))
                        total = int(match.group(2))
                        break

                # Fallback for legacy indicators.
                if fulfilled is None or total is None:
                    met_count = 0
                    cond_count = 0
                    for item in details:
                        if not isinstance(item, str):
                            continue
                        upper_item = item.upper()
                        if ': MET' in upper_item or '✓' in item:
                            met_count += 1
                            cond_count += 1
                        elif ': NOT MET' in upper_item or '✗' in item:
                            cond_count += 1

                    if cond_count > 0:
                        fulfilled = met_count
                        total = cond_count

                # Last fallback keeps existing persisted values when available.
                if fulfilled is None:
                    fulfilled = int(req.get('fulfilled', 0) or 0)
                if total is None:
                    total = int(req.get('total', len(details)) or 0)

                req['fulfilled'] = fulfilled
                req['total'] = total
                req['fulfilled_count'] = fulfilled
                req['total_count'] = total
            
            if 'test' in agent_details:
                passed = agent_details['test'].get('passed_count', 0)
                total_tests = agent_details['test'].get('total_tests', 0)
                if not total_tests:
                    total_tests = len(agent_details['test'].get('test_results', []))
                agent_details['test']['total_tests'] = total_tests
                agent_details['test']['passed_count'] = passed
        
        # Định dạng ngày gửi
        if submission['submitted_at'] and hasattr(submission['submitted_at'], "strftime"):
            submission['submitted_at_display'] = submission['submitted_at'].strftime("%d/%m/%Y, %H:%M:%S")
        
        return templates.TemplateResponse(
            "ketquaSV_dynamic.html",
            {
                "request": request,
                "submission": submission,
                "assignment": assignment,
                "evaluation": evaluation,
                "agent_details": agent_details,
                "viewer_role": viewer_role,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


@app.post("/submit")
async def submit(
    request: Request,
    assignment_id: int = Form(...),
    file: UploadFile = File(None),
    source_code: str = Form(default="")
):
    """
    Xử lý submission bài tập với AI evaluation
    """
    try:
        # Lấy student_id từ cookies
        try:
            student_id = int(request.cookies.get("user_id") or "")
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Phải đăng nhập trước")
        
        # Verify student is assigned to this assignment before processing.
        with get_db() as conn:
            if not _is_student_assigned(conn, assignment_id=assignment_id, student_id=student_id):
                raise HTTPException(status_code=403, detail="Bạn không thuộc danh sách được giao bài này")

        # Tạo thư mục uploads nếu chưa có
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        
        # Lấy requirements và testcases từ database
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(title, ''), COALESCE(description, '')
                    FROM assignments WHERE assignment_id=%s
                    """,
                    (assignment_id,),
                )
                arow = cur.fetchone()
                assignment_context = {
                    "title": (arow[0] or "") if arow else "",
                    "description": (arow[1] or "") if arow else "",
                }
                # Lấy requirements
                cur.execute("""
                    SELECT requirement_text, weight
                    FROM assignment_requirements
                    WHERE assignment_id=%s
                """, (assignment_id,))
                requirements_raw = cur.fetchall()
                # Convert tuples to dictionaries for agents
                requirements = [
                    {
                        "requirement_text": text,
                        "weight": float(weight) if weight else 1.0
                    }
                    for text, weight in requirements_raw
                ]
                print(f"[DEBUG] Requirements loaded: {len(requirements)} items")
                for i, req in enumerate(requirements):
                    print(f"  [{i}] {req['requirement_text'][:50]}... (weight={req['weight']})")
                
                # Lấy testcases
                cur.execute("""
                    SELECT input_data, expected_output, score_weight
                    FROM assignment_testcases
                    WHERE assignment_id=%s
                """, (assignment_id,))
                testcases_raw = cur.fetchall()
                # Convert tuples to dictionaries for agents
                testcases = [
                    {
                        "input_data": inp,
                        "expected_output": out,
                        "score_weight": float(weight) if weight else 1.0
                    }
                    for inp, out, weight in testcases_raw
                ]
                print(f"[DEBUG] Test cases loaded: {len(testcases)} items")
                for i, tc in enumerate(testcases):
                    print(f"  [{i}] Input={repr(tc['input_data'][:30])}... Expected={repr(tc['expected_output'][:30])}... (weight={tc['score_weight']})")
        
        # Xử lý file upload hoặc code text
        code_content = None
        file_name = None
        
        if file and file.filename:
            # Lưu file upload
            file_name = file.filename
            filepath = os.path.join("uploads", file_name)
            
            file_content = await file.read()
            with open(filepath, "wb") as f:
                f.write(file_content)
            
            # Đọc nội dung file
            try:
                code_content = file_content.decode("utf-8")
            except:
                code_content = file_content.decode("latin-1")
        else:
            # Sử dụng code text nếu không có file
            code_content = source_code
            file_name = "submitted_code"
        
        if not code_content or not code_content.strip():
            raise HTTPException(status_code=400, detail="Phải nhập code hoặc gửi file")
        
        # Tạo file tạm thời cho coordinator
        temp_fd, temp_filepath = tempfile.mkstemp(suffix=".py", text=True)
        try:
            # Ghi code vào file tạm
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            print(f"[Coordinator] Evaluating submission {assignment_id} for student {student_id}")
            print(f"[Coordinator] Using temp file: {temp_filepath}")
            print(f"[DEBUG] Code to evaluate ({len(code_content)} bytes)")
            
            try:
                # Chạy coordinator để chấm điểm code
                # coordinator() expects: (filepath, requirements, testcases)
                # where testcases are (input, expected_output, weight)
                print(f"[DEBUG] Calling coordinator with {len(requirements)} requirements, {len(testcases)} testcases")
                result = coordinator(
                    filepath=temp_filepath,
                    requirements=requirements,  # List of (requirement_text, weight)
                    testcases=testcases,  # List of (input_data, expected_output, weight)
                    assignment_context=assignment_context,
                )
                
                print(f"[DEBUG] Coordinator returned result with keys: {result.keys()}")
                print(f"[DEBUG] Result structure:")
                print(f"  - result['total']: {result.get('total', {})}")
                print(f"  - result['syntax']: {result.get('syntax', {}).get('score', 'N/A')}/20")
                print(f"  - result['requirement']: {result.get('requirement', {}).get('score', 'N/A')}/20")
                print(f"  - result['structure']: {result.get('structure', {}).get('score', 'N/A')}/20")
                print(f"  - result['test']: {result.get('test', {}).get('score', 'N/A')}/20")
                print(f"  - result['llm']: {result.get('llm', {}).get('score', 'N/A')}/20")
                
                print(f"[Coordinator] Evaluation complete. Score: {result.get('total', {}).get('total_score', 'ERROR')}/100")
            except Exception as e:
                print(f"[ERROR] Coordinator execution failed: {str(e)}")
                print(f"[ERROR] Exception type: {type(e).__name__}")
                import traceback
                print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
                raise
            
        finally:
            # Xóa file tạm
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
        
        # Lưu submission vào database
        with get_db() as conn:
            with conn.cursor() as cur:
                # Kiểm tra submission cũ có tồn tại không
                cur.execute("""
                    SELECT submission_id FROM submissions
                    WHERE assignment_id=%s AND student_id=%s
                """, (assignment_id, student_id))
                
                existing_submission = cur.fetchone()
                
                if existing_submission:
                    # Update submission cũ (cho phép resubmit)
                    submission_id = existing_submission[0]
                    cur.execute("""
                        UPDATE submissions
                        SET file_name=%s, source_code=%s, submitted_at=CURRENT_TIMESTAMP
                        WHERE submission_id=%s
                    """, (file_name, code_content, submission_id))
                    
                    # Xóa evaluation cũ và agent logs cũ
                    cur.execute("""
                        DELETE FROM agent_logs
                        WHERE submission_id=%s
                    """, (submission_id,))
                    
                    cur.execute("""
                        DELETE FROM evaluation_sessions
                        WHERE submission_id=%s
                    """, (submission_id,))
                else:
                    # Insert submission mới
                    cur.execute("""
                        INSERT INTO submissions
                        (assignment_id, student_id, file_name, source_code, submitted_at)
                        VALUES (%s,%s,%s,%s, CURRENT_TIMESTAMP)
                        RETURNING submission_id
                    """, (assignment_id, student_id, file_name, code_content))
                    
                    submission_id = cur.fetchone()[0]
                
                # Insert evaluation session mới từ result của coordinator
                # Safely extract all agent details with proper defaults
                syntax_data = result.get("syntax", {})
                code_analysis_data = result.get("code_analysis", {})
                requirement_data = result.get("requirement", {})
                structure_data = result.get("structure", {})
                test_data = result.get("test", {})
                llm_data = result.get("llm", {})
                response_data = result.get("response", {})
                
                agent_details = {
                    "syntax": {
                        "success": syntax_data.get("success", False),
                        "score": syntax_data.get("score", 0),
                        "error": syntax_data.get("error", None),
                        "details": syntax_data.get("details", [])
                    },
                    "code_analysis": {
                        "score": code_analysis_data.get("score", 0),
                        "issues": code_analysis_data.get("issues", []),
                        "strengths": code_analysis_data.get("strengths", []),
                        "summary": code_analysis_data.get("summary", ""),
                        "details": code_analysis_data.get("details", {})
                    },
                    "requirement": {
                        "score": requirement_data.get("score", 0),
                        "details": requirement_data.get("details", []),
                        "fulfilled": requirement_data.get("fulfilled_count", requirement_data.get("fulfilled", 0)),
                        "total": requirement_data.get("total_count", requirement_data.get("total", 0)),
                        "fulfilled_count": requirement_data.get("fulfilled_count", requirement_data.get("fulfilled", 0)),
                        "total_count": requirement_data.get("total_count", requirement_data.get("total", 0)),
                        "requirements_met": requirement_data.get("requirements_met", []),
                        "requirements_missing": requirement_data.get("requirements_missing", [])
                    },
                    "structure": {
                        "score": structure_data.get("score", 0),
                        "details": structure_data.get("details", [])
                    },
                    "test": {
                        "score": test_data.get("score", 0),
                        "details": test_data.get("details", []),
                        "passed_count": test_data.get("passed_count", 0),
                        "total_tests": test_data.get("total_tests", 0),
                        "summary": test_data.get("summary", ""),
                        "test_results": test_data.get("test_results", [])
                    },
                    "llm": {
                        "score": llm_data.get("score", 0),
                        "feedback": llm_data.get("feedback", "No feedback available"),
                        "summary": llm_data.get("summary", ""),
                        "teacher_feedback": llm_data.get("teacher_feedback", ""),
                        "must_fix": llm_data.get("must_fix", []),
                        "improvements": llm_data.get("improvements", []),
                        "suggestions": llm_data.get("suggestions", []),
                        "details": llm_data.get("details", [])
                    },
                    "response": {
                        "structured": response_data.get("structured_response", {}),
                        "natural_text": response_data.get("natural_text", "")
                    }
                }
                
                # Extract scores for database
                syntax_score = float(result.get("syntax", {}).get("score", 0))
                code_analysis_score = float(result.get("code_analysis", {}).get("score", 0))
                requirement_score = float(result.get("requirement", {}).get("score", 0))
                structure_score = float(result.get("structure", {}).get("score", 0))
                test_score = float(result.get("test", {}).get("score", 0))
                llm_score = float(result.get("llm", {}).get("score", 0))
                total_score = float(result.get("total", {}).get("total_score", 0))
                
                print(f"[DEBUG] Extracted scores:")
                print(f"  - syntax_score: {syntax_score}")
                print(f"  - code_analysis_score: {code_analysis_score}")
                print(f"  - requirement_score: {requirement_score}")
                print(f"  - structure_score: {structure_score}")
                print(f"  - test_score: {test_score}")
                print(f"  - llm_score: {llm_score}")
                print(f"  - total_score: {total_score}")
                print(f"[DEBUG] Final score to be stored: {total_score}/100")
                
                # Use NLG layer for final natural-language response, fallback to compact summary.
                final_feedback = response_data.get("natural_text", "")
                if not final_feedback:
                    feedback_lines = []

                    syntax_success = result.get("syntax", {}).get("success", False)
                    if syntax_success:
                        feedback_lines.append("✓ Cú pháp Python hợp lệ")
                    else:
                        error_msg = result.get("syntax", {}).get("error", "Unknown error")
                        feedback_lines.append(f"✗ Lỗi cú pháp: {error_msg}")

                    code_analysis_summary = result.get("code_analysis", {}).get("summary", "")
                    if code_analysis_summary:
                        feedback_lines.append(f"Code Quality: {code_analysis_summary}")

                    req_details = result.get("requirement", {}).get("details", [])
                    feedback_lines.extend(req_details[:2])

                    test_details = result.get("test", {}).get("details", [])
                    if test_details:
                        feedback_lines.append(result.get("test", {}).get("summary", "Tests evaluated"))

                    final_feedback = " | ".join(feedback_lines[:5])
                
                cur.execute("""
                    INSERT INTO evaluation_sessions
                    (
                        submission_id,
                        syntax_score,
                        code_analysis_score,
                        structure_score,
                        requirement_score,
                        test_score,
                        llm_score,
                        total_score,
                        final_feedback,
                        agent_details
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    submission_id,
                    syntax_score,
                    code_analysis_score,
                    structure_score,
                    requirement_score,
                    test_score,
                    llm_score,
                    total_score,
                    final_feedback,
                    json.dumps(agent_details, ensure_ascii=False)
                ))
                
                # Insert agent logs
                syntax_status = "✓ PASS" if result.get("syntax", {}).get("success", False) else f"✗ FAIL - {result.get('syntax', {}).get('error', 'Unknown error')}"
                code_analysis_status = f"Score: {result.get('code_analysis', {}).get('score', 0)}/20"
                req_details = result.get("requirement", {}).get("details", [])
                req_passed = len([d for d in req_details if '✓' in d])
                req_total = len(req_details) if req_details else 0
                
                agent_names = ["SyntaxAgent", "CodeAnalysisAgent", "RequirementAgent", "StructureAgent", "TestAgent", "LLMAgent"]
                agent_results = [
                    f"Syntax: {syntax_status}",
                    f"Code Analysis: {code_analysis_status}",
                    f"Requirements met: {req_passed}/{req_total}",
                    f"Structure: {result.get('structure', {}).get('score', 0)}/20",
                    f"Tests: {result.get('test', {}).get('pass_rate', 'N/A')}",
                    f"LLM Score: {result.get('llm', {}).get('score', 0)}/20"
                ]
                
                for agent_name, agent_result in zip(agent_names, agent_results):
                    cur.execute("""
                        INSERT INTO agent_logs (submission_id, agent_name, result)
                        VALUES (%s, %s, %s)
                    """, (submission_id, agent_name, agent_result))
            
            conn.commit()
        
        # Redirect tới trang kết quả
        return RedirectResponse(
            url=f"/submission-result/{submission_id}",
            status_code=303
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi submission: {str(e)}")


@app.get("/debug/users")
def debug_users():
    """Debug endpoint - Xem tất cả users (teachers + students) trong DB"""
    try:
        with get_db() as conn:
            teachers = []
            students = []
            
            with conn.cursor() as cur:
                # Lấy danh sách giáo viên
                cur.execute("SELECT teacher_id, username, email, full_name FROM teachers ORDER BY teacher_id")
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                teachers = [dict(zip(columns, row)) for row in rows]
                
                # Lấy danh sách sinh viên
                cur.execute("SELECT student_id, username, email, full_name FROM students ORDER BY student_id")
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                students = [dict(zip(columns, row)) for row in rows]
        
        return {
            "teachers_count": len(teachers),
            "students_count": len(students),
            "teachers": teachers,
            "students": students
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/debug/submission/{submission_id}")
def debug_submission_score(submission_id: int):
    """Debug endpoint: full scoring breakdown for one submission."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        s.submission_id,
                        s.assignment_id,
                        s.student_id,
                        s.submitted_at,
                        a.title,
                        st.full_name AS student_name,
                        es.session_id,
                        es.syntax_score,
                        es.code_analysis_score,
                        es.requirement_score,
                        es.structure_score,
                        es.test_score,
                        es.llm_score,
                        es.total_score,
                        es.final_feedback,
                        es.agent_details,
                        es.created_at
                    FROM submissions s
                    JOIN assignments a ON a.assignment_id = s.assignment_id
                    JOIN students st ON st.student_id = s.student_id
                    LEFT JOIN evaluation_sessions es ON es.submission_id = s.submission_id
                    WHERE s.submission_id = %s
                    ORDER BY es.created_at DESC NULLS LAST
                    LIMIT 1
                    """,
                    (submission_id,),
                )
                row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Submission không tồn tại")

        columns = [
            "submission_id",
            "assignment_id",
            "student_id",
            "submitted_at",
            "assignment_title",
            "student_name",
            "session_id",
            "syntax_score",
            "code_analysis_score",
            "requirement_score",
            "structure_score",
            "test_score",
            "llm_score",
            "total_score",
            "final_feedback",
            "agent_details",
            "evaluated_at",
        ]
        payload = dict(zip(columns, row))

        # Parse agent_details JSON/text safely
        agent_details_raw = payload.get("agent_details")
        if isinstance(agent_details_raw, dict):
            agent_details = agent_details_raw
        else:
            try:
                agent_details = json.loads(agent_details_raw) if agent_details_raw else {}
            except Exception:
                agent_details = {}

        payload["agent_details"] = agent_details
        payload["scoring_scale"] = {
            "core_agent_range": "0-20",
            "final_total_range": "0-100",
            "formula": "average(core_5_agents) * 5",
            "gates": [
                "Syntax fail => cap 40",
                "Runtime/test execution error => cap 60",
                "100 requires syntax=20 and test=20",
            ],
        }
        return payload

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi debug submission: {str(e)}")


@app.get("/debug/submission/{submission_id}/view")
def debug_submission_view(request: Request, submission_id: int):
    """Debug UI page for one submission breakdown."""
    data = debug_submission_score(submission_id)

    # Present key sections separately for template convenience.
    agent_details = data.get("agent_details", {}) if isinstance(data, dict) else {}
    return templates.TemplateResponse(
        "debug_submission.html",
        {
            "request": request,
            "data": data,
            "agent_details": agent_details,
        },
    )

