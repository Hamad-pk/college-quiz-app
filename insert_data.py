import sqlite3
import os
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "quiz.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
cur.execute("DELETE FROM grades WHERE name IN ('9th','10th','11th', '12th')")



def get_id(query, params):
    cur.execute(query, params)
    row = cur.fetchone()
    return row[0] if row else None

# ---------- REUSABLE HELPERS ----------

def add_subject(grade_id, name):
    cur.execute("INSERT OR IGNORE INTO subjects (grade_id, name) VALUES (?, ?)", (grade_id, name))
    return get_id("SELECT id FROM subjects WHERE grade_id=? AND name=?", (grade_id, name))

def add_unit(subject_id, name):
    cur.execute("INSERT OR IGNORE INTO units (subject_id, name) VALUES (?, ?)", (subject_id, name))
    return get_id("SELECT id FROM units WHERE subject_id=? AND name=?", (subject_id, name))

def add_question(unit_id, q, a, b, c, d, correct):
    cur.execute("""
        INSERT OR IGNORE INTO questions
        (unit_id, question, option_a, option_b, option_c, option_d, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, q, a, b, c, d, correct))

def add_grade(name, sort_order):
    cur.execute("INSERT OR IGNORE INTO grades (name, sort_order) VALUES (?, ?)", (name, sort_order))
    return get_id("SELECT id FROM grades WHERE name=?", (name,))


# ---- INSERT GRADES ----
grades = [("9th",1),("10th",2),("11th",3),("12th",4)]
for name,order in grades:
    cur.execute("INSERT OR IGNORE INTO grades (name, sort_order) VALUES (?, ?)", (name, order))

# ---- CSV Importer -----
with open("questions.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        grade_id = get_id("SELECT id FROM grades WHERE name=?", (row["Grade"],))
        if not grade_id:
            cur.execute("INSERT INTO grades (name) VALUES (?)", (row["Grade"],))
            grade_id = get_id("SELECT id FROM grades WHERE name=?", (row["Grade"],))
        
        subject_id = add_subject(grade_id, row["Subject"])
        unit_id = add_unit(subject_id, row["Unit"])
        add_question(unit_id, row["Question"], row["Option_A"], row["Option_B"],
                     row["Option_C"], row["Option_D"], row["Answer"])


conn.commit()
conn.close()
print("Data inserted successfully.")

