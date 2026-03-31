import tkinter as tk
from tkinter import messagebox, ttk
import random
import sqlite3
import os


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz App")
        self.root.geometry("700x500")
        self.root.configure(bg="#e6f0fa")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
                        font=("Arial", 13, "bold"),
                        padding=6,
                        relief="flat",
                        background="#0078D7",
                        foreground="white")
        style.map("TButton",
                  background=[("active", "#005a9e")],
                  relief=[("pressed", "groove")])
        style.configure("TRadiobutton",
                        font=("Arial", 12),
                        background="#e6f0fa")
                
        # Back button style (used for quiz screens)
        style.configure("Back.TButton",
                        font=("Arial", 11, "bold"),
                        foreground="#004c99",
                        background="#e6f0fa",
                        relief="flat")
        style.map("Back.TButton",
                background=[("active", "#e6f0fa"), ("pressed", "#e6f0fa")],
                foreground=[("active", "#00264d"), ("pressed", "#00264d")])


        # app variables
        self.grade = None
        self.subject = None
        self.unit = None
        self.questions = []
        self.current_q = 0
        self.score = 0
        self.answers = {}
        self.selected_option = tk.StringVar()
        self.review_mode = False
        self.quiz_data = self.load_from_db()

        self.main_frame = tk.Frame(self.root, bg="#e6f0fa")
        self.main_frame.pack(fill="both", expand=True)

        self.create_grade_screen()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ------------------------------
    # GRADE SCREEN
    # ------------------------------
    def create_grade_screen(self):

        self.grade = None
        self.subject = None
        self.unit = None

        self.clear_screen()
        header = tk.Label(self.main_frame, text="Select Your Grade",
                          font=("Arial", 24, "bold"), bg="#e6f0fa", fg="#003366")
        header.pack(pady=40)

        frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        frame.pack()
        for grade in self.quiz_data.keys():
            ttk.Button(frame, text=f"Grade {grade}",
                       width=25, command=lambda g=grade: self.create_subject_screen(g), cursor="hand2").pack(pady=10)

        tk.Label(self.main_frame, text="Choose your grade to begin.",
                 font=("Arial", 12, "italic"), bg="#e6f0fa", fg="#666").pack(pady=30)
        self.add_footer()

    # ------------------------------
    # SUBJECT SCREEN
    # ------------------------------
    def create_subject_screen(self, grade):
        self.grade = grade
        self.clear_screen()
        tk.Label(self.main_frame, text=f"Select a Subject (Grade {grade})",
                 font=("Arial", 22, "bold"), bg="#e6f0fa", fg="#003366").pack(pady=40)

        frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        frame.pack()
        for subj in self.quiz_data[grade].keys():
            ttk.Button(frame, text=subj, width=25,
                       command=lambda s=subj: self.create_unit_screen(s), cursor="hand2").pack(pady=10)

        ttk.Button(self.main_frame, text="Back", command=self.create_grade_screen, cursor="hand2").pack(pady=20)
        self.add_footer()

    # ------------------------------
    # UNIT SCREEN
    # ------------------------------
    def create_unit_screen(self, subject):
        self.subject = subject
        self.clear_screen()
        tk.Label(self.main_frame, text=f"{subject} - Select a Unit",
                 font=("Arial", 22, "bold"), bg="#e6f0fa", fg="#003366").pack(pady=40)

        frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        frame.pack()
        for unit in self.quiz_data[self.grade][subject].keys():
            ttk.Button(frame, text=unit, width=40,
                       command=lambda u=unit: self.start_quiz(u), cursor="hand2").pack(pady=10)

        ttk.Button(self.main_frame, text="Back",
                   command=lambda: self.create_subject_screen(self.grade), cursor="hand2").pack(pady=20)
        self.add_footer()

    # ------------------------------
    # QUESTIONS LIMIT SCREEN
    # ------------------------------
    def load_question_limit_screen(self, unit_id):
        """Full-screen question limit selection matching the main UI style."""
        self.clear_screen()
        self.unit_id = unit_id  # store for later use

        # Count available questions for this unit
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "quiz.db")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM questions WHERE unit_id = ?", (unit_id,))
        total_questions = cur.fetchone()[0]
        conn.close()

        if total_questions == 0:
            messagebox.showinfo("No Questions", "This unit has no questions.")
            return

        # --- HEADER ---
        tk.Label(
            self.main_frame,
            text=f"{self.unit}\n\nHow many questions do you want to answer?",
            font=("Arial", 22, "bold"),
            bg="#e6f0fa",
            fg="#003366",
            justify="center"
        ).pack(pady=(60, 20))

        amount_var = tk.StringVar(value="")

        entry_frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        entry_frame.pack(pady=10)

        entry = tk.Entry(
            entry_frame,
            textvariable=amount_var,
            font=("Arial", 14),
            justify="center",
            width=6,
            bd=2,
            relief="groove"
        )
        entry.pack()

        def start_quiz_with_limit():
            text = amount_var.get().strip()
            if not text.isdigit():
                messagebox.showerror("Invalid Input", "Enter a valid number.")
                return

            num = int(text)
            if num < 1:
                messagebox.showerror("Invalid Input", "You must choose at least 1 question.")
                return
            if num > total_questions:
                messagebox.showerror("Invalid Input", f"Maximum is {total_questions}.")
                return

            self.question_limit = num
            self.questions = self.load_limited_questions(unit_id, self.question_limit)

            if not self.questions:
                messagebox.showinfo("No Questions", "This unit has no questions yet.")
                return

            # Reset quiz state
            self.shuffled_sets = {}
            self.current_q = 0
            self.score = 0
            self.answers = {}
            self.review_mode = False

            random.shuffle(self.questions)
            self.load_question_screen()

        # --- BUTTONS ---
        btn_frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        btn_frame.pack(pady=30)

        start_btn = ttk.Button(
            btn_frame,
            text="Start Quiz",
            command=start_quiz_with_limit,
            cursor="hand2"
        )
        start_btn.pack(side="left", padx=10)

        back_btn = ttk.Button(
            btn_frame,
            text="Back",
            command=self.create_unit_screen_back,
            cursor="hand2"
        )
        back_btn.pack(side="left", padx=10)

        tk.Label(self.main_frame, text="Choose the amount of questions.",
        font=("Arial", 14, "italic"), bg="#e6f0fa", fg="#666").pack(pady=30)
        self.add_footer()




    # Footer
    def add_footer(self):
        footer = tk.Label(
            self.main_frame,
            text="Developed By Hamadullah   |   Supervised By Amir Watoo",
            font=("Arial", 10, "italic"),
            bg="#e6f0fa",
            fg="#555"
        )
        footer.pack(side="bottom", pady=10)

    #Jump to Questions
    def jump_to_question(self, idx):
        self.current_q = idx
        self.load_question_screen()
    #Exit confirmation message
    def confirm_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit the quiz?"):
            self.root.destroy()



    # -------------------------------
    # DataBase
    # -------------------------------

    def load_from_db(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "quiz.db")
        print("APP DB:", DB_PATH)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        data = {}

        # Load grades
        cur.execute("SELECT id, name FROM grades ORDER BY sort_order")
        grades = cur.fetchall()

        for grade_id, grade_name in grades:
            data[grade_name] = {}

            # Load subjects for this grade
            cur.execute("SELECT id, name FROM subjects WHERE grade_id = ?", (grade_id,))
            subjects = cur.fetchall()

            for subj_id, subj_name in subjects:
                data[grade_name][subj_name] = {}

                # Load units for this subject
                cur.execute("SELECT id, name FROM units WHERE subject_id = ?", (subj_id,))
                units = cur.fetchall()

                for unit_id, unit_name in units:
                    data[grade_name][subj_name][unit_name] = []

                    # Load questions
                    cur.execute("""
                        SELECT question, option_a, option_b, option_c, option_d, answer
                        FROM questions WHERE unit_id = ?
                    """, (unit_id,))
                    rows = cur.fetchall()

                    for q, a, b, c, d, ans in rows:
                        data[grade_name][subj_name][unit_name].append({
                            "question": q,
                            "options": [a, b, c, d],
                            "answer": ans
                        })

        conn.close()
        return data
    
    # ------------------------------
    # Questions limit
    # ------------------------------

    def load_limited_questions(self, unit_id, limit):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "quiz.db")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT question, option_a, option_b, option_c, option_d, answer
            FROM questions
            WHERE unit_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (unit_id, limit))

        rows = cur.fetchall()
        conn.close()

        questions = []

        for q, a, b, c, d, ans in rows:
            questions.append({
                "question": q,
                "options": [a, b, c, d],
                "answer": ans
            })

        return questions
    
    # ------------------------------
    # UNIT ID
    # ------------------------------
    
    def get_unit_id(self, grade, subject, unit):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "quiz.db")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT units.id
            FROM units
            JOIN subjects ON subjects.id = units.subject_id
            JOIN grades ON grades.id = subjects.grade_id
            WHERE grades.name = ? AND subjects.name = ? AND units.name = ?
        """, (grade, subject, unit))

        row = cur.fetchone()
        conn.close()

        return row[0] if row else None


    # ------------------------------
    # QUIZ FLOW
    # ------------------------------
    def start_quiz(self, unit):
        self.unit = unit

        unit_id = self.get_unit_id(self.grade, self.subject, unit)
        if unit_id is None:
            messagebox.showerror("Error", "Could not find unit ID in database.")
            return

        self.unit_id = unit_id
        self.load_question_limit_screen(self.unit_id)

    # ------------------------------
    #  REMOVE TRACES
    # ------------------------------
    def remove_traces(self):
        if hasattr(self, "next_trace") and self.next_trace:
            try:
                self.selected_option.trace_remove("write", self.next_trace)
            except tk.TclError:
                pass
            self.next_trace = None

        if hasattr(self, "option_trace") and self.option_trace:
            try:
                self.selected_option.trace_remove("write", self.option_trace)
            except tk.TclError:
                pass
            self.option_trace = None
        


    def load_question_screen(self):
        
        self.remove_traces()
        self.selected_option = tk.StringVar()
        self.clear_screen()
        

        # Show back arrow only in normal quiz mode
        if not self.review_mode:
            back_button = ttk.Button(
                self.main_frame,
                text="← Back",
                style="Back.TButton",
                command=self.create_unit_screen_back,
                cursor="hand2"   
            )
            back_button.pack(anchor="nw", padx=10, pady=10)

        q = self.questions[self.current_q]

        # Shuffle options 
        letters = ["A", "B", "C", "D"]

        if not hasattr(self, "shuffled_sets") or len(self.shuffled_sets) == 0:
            self.shuffled_sets = {}
            for i, question in enumerate(self.questions):
                shuffled = random.sample(question["options"], len(question["options"]))
                # Map text to the original DB letter
                reverse_map = {text: letters[question["options"].index(text)] for text in shuffled}
                self.shuffled_sets[i] = {"options": shuffled, "reverse_map": reverse_map}

        shuffled_options = self.shuffled_sets[self.current_q]["options"]

        # --- HEADER ---
        tk.Label(self.main_frame, text=f"Subject: {self.subject}",
                font=("Arial", 14, "italic"), bg="#e6f0fa", fg="#004c99").pack(anchor="ne", padx=20, pady=5)

        num_questions = max(len(self.questions), 1)  # avoid zero
        progress_value = (self.current_q + 1) * 100 / num_questions

        progress = ttk.Progressbar(self.main_frame, value=progress_value,
                                maximum=100, length=500)
        progress.pack(pady=5)

        # --- COLORS ---
        NORMAL_BG = "#f7f9fc"
        SELECT_BG = "#d9e6ff"

        # --- QUESTION HEADER ---
        header_frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        header_frame.pack(fill="x", pady=(10, 0))

        tk.Label(
            header_frame,
            text=f"Question {self.current_q + 1} of {len(self.questions)}",
            font=("Arial", 14, "bold"),
            bg="#e6f0fa",
            fg="#003366"
        ).pack(anchor="center", pady=(5, 10))

        # --- QUESTION CARD ---
        card_shadow = tk.Frame(self.main_frame, bg="#cdd7e0")
        card_shadow.pack(padx=48, pady=(5, 20), fill="x")

        question_frame = tk.Frame(card_shadow, bg="#f7f9fc", bd=2, relief="groove")
        question_frame.pack(padx=2, pady=2, fill="x")

        tk.Label(
            question_frame,
            text=q["question"],
            wraplength=600,
            justify="center",
            font=("Arial", 17, "bold"),
            bg="#f7f9fc",
            fg="#00264d",
            padx=15,
            pady=20
        ).pack(fill="x")


        # --- OPTIONS SECTION ---
        options_frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        options_frame.pack(pady=15)

        option_frames = {}

        # improved colors
        NORMAL_BG = "#f7f9fc"
        HOVER_BG = "#8db2fc"
        SELECT_BG = "#cfe0ff"

        def on_enter(frame):
            if frame["bg"] == NORMAL_BG:
                frame.config(bg=HOVER_BG)

        def on_leave(frame):
            if frame["bg"] == HOVER_BG:
                frame.config(bg=NORMAL_BG)

        def on_select_callback(selected_value=None, option_frames=None):
            sel = selected_value if selected_value else self.selected_option.get()
            if not option_frames:
                return  # safety check
            for f, _ in option_frames.values():
                f.config(bg=NORMAL_BG)
            if getattr(self, "review_mode", False):
                return
            if sel in option_frames:
                frame, _ = option_frames[sel]
                frame.config(bg=SELECT_BG)



        

        for opt in shuffled_options:
            # --- Outer frame with light shadow ---
            opt_frame = tk.Frame(
                options_frame,
                bg=NORMAL_BG,
                highlightbackground="#ccc",
                highlightthickness=1,
                bd=0,
                relief="flat",
                cursor="hand2"
            )
            opt_frame.pack(anchor="center", padx=160, pady=8, fill="x")


            def select_option(v):
                if not self.review_mode:
                    self.selected_option.set(v)
                    on_select_callback(v)

            rb = ttk.Radiobutton(
                opt_frame,
                text=opt,
                variable=self.selected_option,
                value=opt,
                command=lambda v=opt: select_option(v),
                cursor="hand2"
            )
            rb.bind("<FocusIn>", lambda e: e.widget.state(["!focus"]))  # remove ugly dotted border
            rb.pack(anchor="w", padx=10, pady=5, fill="x")

            # --- Hover behavior for entire option ---
            def on_enter(frame=opt_frame, v=opt):
                if not self.review_mode and self.selected_option.get() != v:
                    frame.config(bg="#e4ecff")

            def on_leave(frame=opt_frame, v=opt):
                if not self.review_mode and self.selected_option.get() != v:
                    frame.config(bg=NORMAL_BG)

            opt_frame.bind("<Enter>", lambda e, f=opt_frame, v=opt: on_enter(f, v))
            opt_frame.bind("<Leave>", lambda e, f=opt_frame, v=opt: on_leave(f, v))
            rb.bind("<Enter>", lambda e, f=opt_frame, v=opt: on_enter(f, v))
            rb.bind("<Leave>", lambda e, f=opt_frame, v=opt: on_leave(f, v))


            # --- Click anywhere to select ---
            def click_option(event=None, v=opt, rb_widget=None):
                if not self.review_mode:
                    rb_widget.focus_set()  # 🔹 ensure the focus ring appears
                    self.selected_option.set(v)
                    on_select_callback(v)
                    
            option_frames[opt] = (opt_frame, rb)



        # update highlight if re-entered question
        if hasattr(self, "option_trace"):
            try:
                self.selected_option.trace_remove("write", self.option_trace)
            except Exception:
                pass

        if self.selected_option.get():
            on_select_callback(self.selected_option.get())


        # --- REVIEW MODE 3D look ---
        if getattr(self, "review_mode", False):
            user_ans = self.answers.get(self.current_q)
            correct_ans = q["answer"]

            # Fill the bubble for the user-selected option
            self.selected_option.set(user_ans)

            for opt_text, (frame, rb) in option_frames.items():
                if opt_text == correct_ans:
                    frame.config(bg="#d6f5d6", highlightbackground="#9edb9e", highlightthickness=2)
                    rb.config(text=f"{opt_text}  ✅")
                elif opt_text == user_ans and user_ans != correct_ans:
                    frame.config(bg="#ffd6d6", highlightbackground="#ff9999", highlightthickness=2)
                    rb.config(text=f"{opt_text}  ❌")
                else:
                    frame.config(bg="#f7f9fc", highlightthickness=0)

                # Disable all radiobuttons in review mode
                rb.state(["disabled"])




        # --- NAVIGATION ---
        nav_frame = tk.Frame(self.main_frame, bg="#e6f0fa")
        nav_frame.pack(pady=40)

        if self.review_mode:
            back_button = ttk.Button(
            self.main_frame,
            text="← Back",
            style="Back.TButton",
            command=self.create_unit_screen_back,
            cursor="hand2"
            )
            back_button.pack(anchor="nw", padx=10, pady=10)
            if self.current_q > 0:
                ttk.Button(nav_frame, text="Previous", command=self.prev_question, cursor="hand2" ).pack(side="left", padx=10)
            if self.current_q < len(self.questions) - 1:
                ttk.Button(nav_frame, text="Next", command=self.next_question, cursor="hand2").pack(side="left", padx=10)
            else:
                ttk.Button(nav_frame, text="Finish Review", command=self.show_result, cursor="hand2" ).pack(side="left", padx=10)
        else:
            self.next_btn = ttk.Button(nav_frame, text="Next", command=self.next_question, cursor="hand2")
            self.next_btn.pack(side="left", padx=10)
            self.next_btn.state(["disabled"])

            self.option_trace = self.selected_option.trace_add(
                "write",
                lambda *args, opt_frames=option_frames: on_select_callback(option_frames=opt_frames)
            )

            # --- Define enable_next first ---
            def enable_next(*args):
                if not self.review_mode and self.selected_option.get() and self.next_btn.winfo_exists():
                    self.next_btn.state(["!disabled"])
                else:
                    self.next_btn.state(["disabled"])

            self.next_trace = self.selected_option.trace_add("write", enable_next)

            enable_next()

        # --- NAVIGATION PANEL (for review mode) ---
        if self.review_mode:
            nav_panel = tk.Frame(self.main_frame, bg="#e6f0fa")
            nav_panel.pack(pady=10)

            for i in range(len(self.questions)):
                btn = ttk.Button(nav_panel, text=str(i + 1), width=3,
                                command=lambda idx=i: self.jump_to_question(idx), cursor="hand2")
                # Disable only the current question
                if i == self.current_q:
                    btn.state(["disabled"])
                else:
                    btn.state(["!disabled"])
                btn.pack(side="left", padx=3)
        self.add_footer()



    def create_unit_screen_back(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to exit the quiz?")
        if confirm:
            self.root.after(0, lambda: self.create_unit_screen(self.subject))

    def next_question(self):
        # If in review mode, just move to next question
        if self.review_mode:
            if self.current_q < len(self.questions) - 1:
                self.current_q += 1
                self.load_question_screen()
            return

        selected = self.selected_option.get()
        if not selected:
            messagebox.showwarning("Warning", "Please select an answer before proceeding.")
            return
        self.answers[self.current_q] = self.selected_option.get()


        if self.current_q == len(self.questions) - 1:
            self.calculate_score()
            self.root.after(0, self.show_result)
        else:
            self.current_q += 1
            self.load_question_screen()

    def prev_question(self):
        if self.current_q > 0:
            self.current_q -= 1
            self.load_question_screen()

    def calculate_score(self):
        self.score = sum(1 for i, q in enumerate(self.questions) if self.answers.get(i) == q["answer"])

    # ------------------------------
    # RESULT + REVIEW
    # ------------------------------
    def show_result(self):
        self.clear_screen()
        self.review_mode = False
        tk.Label(self.main_frame, text="Quiz Completed!",
                 font=("Arial", 22, "bold"), bg="#e6f0fa", fg="#003366").pack(pady=40)
        tk.Label(self.main_frame, text=f"Grade: {self.grade}", font=("Arial", 14), bg="#e6f0fa").pack()
        tk.Label(self.main_frame, text=f"Subject: {self.subject}", font=("Arial", 14), bg="#e6f0fa").pack()
        tk.Label(self.main_frame, text=f"{self.unit}", font=("Arial", 14, "italic"), bg="#e6f0fa").pack(pady=5)

        score_color = "#28a745" if self.score > len(self.questions) / 2 else "#d9534f"
        tk.Label(self.main_frame, text=f"Your Score: {self.score}/{len(self.questions)}",
                 font=("Arial", 18, "bold"), bg="#e6f0fa", fg=score_color).pack(pady=20)

        ttk.Button(self.main_frame, text="Review Answers", command=self.start_review, cursor="hand2").pack(pady=10)
        ttk.Button(self.main_frame, text="Back to Units", command=lambda: self.create_unit_screen(self.subject), cursor="hand2").pack(pady=10)
        ttk.Button(self.main_frame, text="Exit", command=self.confirm_exit, cursor="hand2").pack(pady=10)

        percent = (self.score / len(self.questions)) * 100
        if percent >= 80:
            msg = "Excellent performance!"
        elif percent >= 60:
            msg = "Good job, keep practicing!"
        else:
            msg = "Needs improvement — review the material again."

        tk.Label(self.main_frame, text=f"Percentage: {percent:.1f}%", 
                font=("Arial", 14, "bold"), bg="#e6f0fa", fg="#004c99").pack()
        tk.Label(self.main_frame, text=msg, 
                font=("Arial", 12, "italic"), bg="#e6f0fa", fg="#333").pack(pady=10)
        self.add_footer()


    def start_review(self):
        self.current_q = 0
        self.review_mode = True
        self.load_question_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()


