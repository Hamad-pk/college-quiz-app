import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "quiz.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

# ---- GRADES ----
cur.execute("""
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    sort_order INTEGER UNIQUE       
)
""")

# ---- SUBJECTS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
    UNIQUE(grade_id, name)
)
""")

# ---- UNITS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(subject_id, name)
)
""")

# ---- QUESTIONS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
    UNIQUE(unit_id, question)
)
""")


# ---- INDEXES ----
cur.execute("CREATE INDEX IF NOT EXISTS idx_subjects_grade ON subjects(grade_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_units_subject ON units(subject_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_questions_unit ON questions(unit_id);")

conn.commit()
conn.close()
print("Database created successfully.")

