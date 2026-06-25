import os
from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs("static/uploads", exist_ok=True)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        password TEXT,
        role TEXT,
        grade TEXT,
        stream TEXT,
        subject TEXT
    )
    """)

    # MESSAGES TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT,
        receiver_id TEXT,
        message TEXT,
        is_read INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # ANNOUNCEMENTS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        date TEXT
    )
    """)

    # GRADES TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        subject TEXT,
        test INTEGER,
        assignment INTEGER,
        final_exam INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        birth_date TEXT,
        gender TEXT,
        previous_school TEXT,
        address TEXT,
        email TEXT,
        phone TEXT,
        parent_name TEXT,
        parent_phone TEXT,
        grade TEXT,
        stream TEXT,
        transcript_file TEXT,
        document_file TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # SAMPLE USERS
    try:
        c.execute("""
        INSERT INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("A001",
         "Admin",
         generate_password_hash("admin"),
         "admin",
         None,
         None,
         None))

        c.execute("""
        INSERT INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("T001",
         "Teacher One",
         generate_password_hash("1234"),
         "teacher",
         "11",
         None,
         "Physics"))

        c.execute("""
        INSERT INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("S001",
         "Student One",
         generate_password_hash("1234"),
         "student",
         "11",
         "Natural",
         None))

    except:
        pass

    # SAMPLE GRADES


    try:
        c.execute(
            "SELECT 1 FROM grades WHERE student_id = ? AND subject = ?",
            ("S001", "Physics")
        )
        
        if not c.fetchone():
            c.execute(
                "INSERT INTO grades (student_id, subject, test, assignment, final_exam) VALUES (?, ?, ?, ?, ?)",
                ("S001", "Physics", 75, 80, 70)
            )
    except:
        pass

    # SAMPLE ANNOUNCEMENT
    try:
        c.execute(
            "SELECT 1 FROM announcements WHERE title = ?",
            ("Welcome",)
        )
        
        if not c.fetchone():
            c.execute(
                "INSERT INTO announcements (title, message, date) VALUES (?, ?, ?)",
                ("Welcome", "School system is now live!", "2026-01-01")
            )
    except:
        pass
    
     #School email sample
    try:
        c.execute("""
        INSERT INTO settings
        VALUES (?, ?)
        """, ("school_email", "olroxe9@gmail.com"))
    except:
        pass

    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

# -------- LOGIN ROUTES --------

@app.route("/login/student", methods=["GET", "POST"])
def login_student():
    if request.method == "POST":
        user_id = request.form["id"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=? AND role='student'", (user_id,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = user[0]
            session["role"] = user[3]
            flash("Login successful!", "success")
            return redirect("/dashboard/student")
        else:
            flash("Invalid student ID or password", "error")
            return redirect("/login/student")   

    return render_template("login_student.html")


@app.route("/login/teacher", methods=["GET", "POST"])
def login_teacher():
    if request.method == "POST":
        user_id = request.form["id"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=? AND role='teacher'", (user_id,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = user[0]
            session["role"] = user[3]
            flash("Login successful!", "success")
            return redirect("/dashboard/teacher")
        else:
            flash("Invalid teacher ID or password", "error")
            return redirect("/login/teacher")

    return render_template("login_teacher.html")


@app.route("/login/admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        user_id = request.form["id"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=? AND role='admin'", (user_id,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = user[0]
            session["role"] = user[3]
            flash("Login successful!", "success")
            return redirect("/dashboard/admin")
        else:
            flash("Invalid admin ID or password", "error")
            return redirect("/login/admin")

    return render_template("login_admin.html")


@app.route("/submit_application", methods=["POST"])
def submit_application():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    full_name = request.form["full_name"]
    birth_date = request.form["birth_date"]
    gender = request.form["gender"]
    previous_school = request.form["previous_school"]
    address = request.form["address"]
    email = request.form["email"]
    phone = request.form["phone"]

    parent_name = request.form["parent_name"]
    parent_phone = request.form["parent_phone"]

    grade = request.form["grade"]
    stream = request.form["stream"]

    transcript = request.files["transcript_file"]
    document = request.files["document_file"]

    transcript_name = transcript.filename
    document_name = document.filename

    transcript.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            transcript_name
        )
    )

    if document_name:
        document.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                document_name
            )
        )

    c.execute("""
    INSERT INTO applications
    (
        full_name,
        birth_date,
        gender,
        previous_school,
        address,
        email,
        phone,
        parent_name,
        parent_phone,
        grade,
        stream,
        transcript_file,
        document_file
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        full_name,
        birth_date,
        gender,
        previous_school,
        address,
        email,
        phone,
        parent_name,
        parent_phone,
        grade,
        stream,
        transcript_name,
        document_name
    ))
        
    conn.commit()
    conn.close()

    flash("Application submitted successfully! Awaiting review.", "success")
    return redirect("/registration")


# -------- DASHBOARDS --------

@app.route("/dashboard/student")
def student_dashboard():
    if "user" not in session:
        return redirect("/")

    student_id = session["user"]


    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get student info
    c.execute("SELECT * FROM users WHERE id=?", (student_id,))
    student = c.fetchone()

    # Get grades
    c.execute("SELECT subject, test, assignment, final_exam FROM grades WHERE student_id=?", (student_id,))
    grades = c.fetchall()

    overall_average = 0

    if grades:
        total = 0

        for g in grades:
            total += (g[1] + g[2] + g[3]) / 3

        overall_average = round(
            total / len(grades),
            1
        )

    # Get announcements
    c.execute("SELECT title, message, date FROM announcements ORDER BY id DESC")
    announcements = c.fetchall()

    # Get all teachers
    c.execute("""
    SELECT id, name, subject
    FROM users
    WHERE role='teacher'
    """)

    teachers = c.fetchall()

    conn.close()

    return render_template(
    "student_dashboard.html",
    student=student,
    grades=grades,
    announcements=announcements,
    teachers=teachers,
    overall_average=overall_average
)

@app.route("/dashboard/teacher")
def teacher_dashboard():
    if "user" not in session or session["role"] != "teacher":
        return redirect("/")

    teacher_id = session["user"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get teacher info
    c.execute("SELECT * FROM users WHERE id=?", (teacher_id,))
    teacher = c.fetchone()

    print("Teacher record:", teacher)

    subject = teacher[6]
    grade = teacher[4]

    # Get students matching subject/grade
    c.execute(
        """
        SELECT *
        FROM users
        WHERE role='student'
        AND grade=?
        """,
        (grade,)
    )
    
    students = c.fetchall()
    student_count = len(students)
    c.execute("""
    SELECT COUNT(*)
    FROM messages
    WHERE sender_id=?
    OR receiver_id=?
    """,
    (teacher_id, teacher_id))

    message_count = c.fetchone()[0]

    c.execute("""
    SELECT COUNT(*)
    FROM grades
    """)

    grade_count = c.fetchone()[0]

    conn.close()

    return render_template(
    "teacher_dashboard.html",
    teacher=teacher,
    students=students,
    student_count=student_count,
    message_count=message_count,
    grade_count=grade_count
)

@app.route("/dashboard/admin", methods=["GET", "POST"])
def admin_dashboard():

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Users
    search = request.args.get("search", "")
    role = request.args.get("role", "")
    grade = request.args.get("grade", "")
    stream = request.args.get("stream", "")

    query = """
    SELECT *
    FROM users
    WHERE 1=1
    """

    params = []

    if search:
        query += """
        AND (
            id LIKE ?
            OR name LIKE ?
        )
        """

        params.extend([
            f"%{search}%",
            f"%{search}%"
        ])

    if role:
        query += " AND role=?"
        params.append(role)

    if grade:
        query += " AND grade=?"
        params.append(grade)

    if stream:
        query += " AND stream=?"
        params.append(stream)

    c.execute(query, params)
    users = c.fetchall()

    c.execute("""
    SELECT *
    FROM announcements
    ORDER BY id DESC
    """)

    announcements = c.fetchall()

    # Student count
    c.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    student_count = c.fetchone()[0]

    # Teacher count
    c.execute("SELECT COUNT(*) FROM users WHERE role='teacher'")
    teacher_count = c.fetchone()[0]

    # Announcement count
    c.execute("SELECT COUNT(*) FROM announcements")
    announcement_count = c.fetchone()[0]

    # Message count
    c.execute("SELECT COUNT(*) FROM messages")
    message_count = c.fetchone()[0]

    c.execute("""
    SELECT *
    FROM applications
    ORDER BY id DESC
    """)

    applications = c.fetchall()

    c.execute("""
    SELECT value
    FROM settings
    WHERE key='school_email'
    """)

    result = c.fetchone()

    school_email = result[0] if result else ""

    conn.close()

    return render_template(
    "admin_panel.html",
    users=users,
    announcements=announcements,
    applications=applications,
    student_count=student_count,
    teacher_count=teacher_count,
    announcement_count=announcement_count,
    message_count=message_count,
    school_email=school_email
)



# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/courses")
def courses():
    return render_template("courses.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/update_school_email", methods=["POST"])
def update_school_email():
    if "user" not in session or session["role"] != "admin":
        return redirect("/")
    email = request.form["school_email"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
    UPDATE settings
    SET value=?
    WHERE key='school_email'
    """, (email,))
    conn.commit()
    conn.close()
    return redirect("/dashboard/admin")

@app.route("/accept_application/<int:id>")
def accept_application(id):

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    UPDATE applications
    SET status='Waiting'
    WHERE id=?
    """, (id,))

    conn.commit()

    c.execute(
        "SELECT id, status FROM applications WHERE id=?",
        (id,)
    )

    print("AFTER UPDATE:", c.fetchone())

    conn.close()

    return redirect("/dashboard/admin")

@app.route("/reject_application/<int:id>")
def reject_application(id):

    print("REJECT CLICKED:", id)

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    UPDATE applications
    SET status='Rejected'
    WHERE id=?
    """,
    (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard/admin")

@app.route("/view_application/<int:id>")
def view_application(id):

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM applications
    WHERE id=?
    """, (id,))
    application = c.fetchone()

    c.execute("""
    SELECT value
    FROM settings
    WHERE key='school_email'
    """)
    result = c.fetchone()
    if result:
        school_email = result[0]
    else:
        school_email = ""

    conn.close()

    return render_template(
        "view_application.html",
        application=application,
        school_email=school_email
    )

@app.route("/enroll_student/<int:id>")
def enroll_student(id):
    if "user" not in session or session["role"] != "admin":
        return redirect("/")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM applications WHERE id=?",
        (id,)
    )

    application = c.fetchone()

    if application is None:
        conn.close()
        return "Application not found"

    # Generate new Student ID
    c.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    count = c.fetchone()[0] + 1

    student_id = f"S{str(count).zfill(3)}"

    password = generate_password_hash("1234")

    c.execute("""
        INSERT INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        application[1],      # full name
        password,
        "student",
        application[10],     # grade
        application[11],     # stream
        None
    ))

    c.execute("""
        UPDATE applications
        SET status='Enrolled'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(f"/view_application/{id}")

@app.route("/edit_grades/<student_id>", methods=["GET", "POST"])
def edit_grades(student_id):

    if "user" not in session or session["role"] != "teacher":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    teacher_id = session["user"]

    c.execute(
        "SELECT * FROM users WHERE id=?",
        (teacher_id,)
    )

    current_teacher = c.fetchone()

    teacher_subject = current_teacher[6]

    if request.method == "POST":

        subject = teacher_subject
        test = request.form["test"]
        assignment = request.form["assignment"]
        final_exam = request.form["final_exam"]

        c.execute("""
        SELECT id
        FROM grades
        WHERE student_id=? AND subject=?
        """,
        (student_id, subject))

        existing = c.fetchone()

        if existing:

            c.execute("""
            UPDATE grades
            SET test=?,
                assignment=?,
                final_exam=?
            WHERE student_id=? AND subject=?
            """,
            (
                test,
                assignment,
                final_exam,
                student_id,
                subject
            ))

        else:

            c.execute("""
            INSERT INTO grades
            (
                student_id,
                subject,
                test,
                assignment,
                final_exam
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student_id,
                subject,
                test,
                assignment,
                final_exam
            ))

        conn.commit()

    c.execute(
        "SELECT * FROM users WHERE id=?",
        (student_id,)
    )

    student = c.fetchone()

    c.execute("""
    SELECT subject,
           test,
           assignment,
           final_exam
    FROM grades
    WHERE student_id=?
    """,
    (student_id,)
    )

    grades = c.fetchall()

    conn.close()

    return render_template(
        "edit_grades.html",
        student=student,
        grades=grades,
        teacher_subject=teacher_subject
    )

@app.route("/add_student", methods=["POST"])
def add_student():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    name = request.form["name"]
    grade = request.form["grade"]

    if grade in ["11", "12"]:
        stream = request.form["stream"]
    else:
        stream = None

    password = generate_password_hash(request.form["password"])

    # Generate ID
    c.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    count = c.fetchone()[0] + 1
    student_id = f"S{str(count).zfill(3)}"

    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
              (student_id, name, password, "student", grade, stream, None))

    conn.commit()
    conn.close()

    return redirect("/dashboard/admin")

@app.route("/add_teacher", methods=["POST"])
def add_teacher():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    name = request.form["name"]
    subject = request.form["subject"]
    grade = request.form["grade"]
    stream = request.form["stream"]
    password = generate_password_hash(request.form["password"])

    c.execute("SELECT COUNT(*) FROM users WHERE role='teacher'")
    count = c.fetchone()[0] + 1
    teacher_id = f"T{str(count).zfill(3)}"

    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
              (teacher_id, name, password, "teacher", grade, stream, subject))

    conn.commit()
    conn.close()

    return redirect("/dashboard/admin")

@app.route("/add_announcement", methods=["POST"])
def add_announcement():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    title = request.form["title"]
    message = request.form["message"]

    c.execute("INSERT INTO announcements (title, message, date) VALUES (?, ?, date('now'))",
              (title, message))

    conn.commit()
    conn.close()

    return redirect("/dashboard/admin")

@app.route("/delete_user/<user_id>")
def delete_user(user_id):

    if user_id == "A001":
        return redirect("/dashboard/admin")

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard/admin")

@app.route("/edit_announcement/<int:id>",
           methods=["GET", "POST"])
def edit_announcement(id):

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        message = request.form["message"]

        c.execute("""
        UPDATE announcements
        SET title=?,
            message=?
        WHERE id=?
        """,
        (title, message, id))

        conn.commit()

        conn.close()

        return redirect("/dashboard/admin")

    c.execute(
        "SELECT * FROM announcements WHERE id=?",
        (id,)
    )

    announcement = c.fetchone()

    conn.close()

    return render_template(
        "edit_announcement.html",
        announcement=announcement
    )

@app.route("/delete_announcement/<int:id>")
def delete_announcement(id):

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "DELETE FROM announcements WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard/admin")

@app.route("/reset_password/<user_id>")
def reset_password(user_id):

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    new_password = generate_password_hash("1234")

    c.execute("""
    UPDATE users
    SET password=?
    WHERE id=?
    """,
    (new_password, user_id))

    conn.commit()
    conn.close()

    return redirect("/dashboard/admin")

@app.route("/edit_user/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        grade = request.form["grade"]

        if grade in ["11", "12"]:
            stream = request.form["stream"]
        else:
            stream = None

        password = generate_password_hash(request.form["password"])
        subject = request.form["subject"]

        c.execute("""
        UPDATE users
        SET name=?,
            grade=?,
            stream=?,
            subject=?
        WHERE id=?
        """,
        (name, grade, stream, subject, user_id))

        conn.commit()
        conn.close()

        return redirect("/dashboard/admin")

    c.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    )

    user = c.fetchone()

    conn.close()

    return render_template(
        "edit_user.html",
        user=user
    )

@app.route("/chat/<student_id>", methods=["GET", "POST"])
def chat(student_id):
    if "user" not in session:
        return redirect("/")

    current_user = session["user"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Send message
    if request.method == "POST":
        msg = request.form["message"]

        c.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)",
                  (current_user, student_id, msg))
        conn.commit()

    # Get messages
    c.execute("""
    SELECT sender_id, message, timestamp FROM messages
    WHERE (sender_id=? AND receiver_id=?)
       OR (sender_id=? AND receiver_id=?)
    ORDER BY timestamp
    """, (current_user, student_id, student_id, current_user))

    messages = c.fetchall()

    conn.close()

    return render_template("chat.html", messages=messages, student_id=student_id)


#grade route

@app.route("/grade/<student_id>", methods=["GET", "POST"])
def add_grade(student_id):

    if "user" not in session or session["role"] != "teacher":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get student info
    c.execute("SELECT * FROM users WHERE id=?", (student_id,))
    student = c.fetchone()

    # Teacher info
    teacher_id = session["user"]

    c.execute("SELECT * FROM users WHERE id=?", (teacher_id,))
    teacher = c.fetchone()

    subject = teacher[6]

    # Save grade
    if request.method == "POST":

        test = request.form["test"]
        assignment = request.form["assignment"]
        final_exam = request.form["final_exam"]

        # Check if subject already exists
        c.execute("""
        SELECT * FROM grades
        WHERE student_id=? AND subject=?
        """, (student_id, subject))

        existing = c.fetchone()

        if existing:
            # UPDATE
            c.execute("""
            UPDATE grades
            SET test=?, assignment=?, final_exam=?
            WHERE student_id=? AND subject=?
            """, (test, assignment, final_exam, student_id, subject))

        else:
            # INSERT
            c.execute("""
            INSERT INTO grades
            (student_id, subject, test, assignment, final_exam)
            VALUES (?, ?, ?, ?, ?)
            """, (student_id, subject, test, assignment, final_exam))

        conn.commit()

    # Get current grades
    c.execute("""
    SELECT * FROM grades
    WHERE student_id=? AND subject=?
    """, (student_id, subject))

    grade = c.fetchone()

    conn.close()

    return render_template(
        "grade_entry.html",
        student=student,
        subject=subject,
        grade=grade
    )


@app.route("/login")
def login_portal():
    return render_template("login.html")


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)