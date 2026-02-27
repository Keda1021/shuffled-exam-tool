import customtkinter as ctk
from tkinter import messagebox
import json
import os
import random

# Core UI Configuration
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue")

class ExamMasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Exam Master v0.0.1")
        self.geometry("1000x750")
        
        self.data_file = "database_exam.json"
        self.database = self.load_data()
        
        self.remaining_seconds = 0
        self.timer_running = False

        # Grid Layout: Sidebar and Main Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.show_dashboard()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.database, f, ensure_ascii=False, indent=4)

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        logo = ctk.CTkLabel(self.sidebar, text="EXAM MASTER", font=ctk.CTkFont(size=22, weight="bold"))
        logo.pack(pady=30)

        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Subjects", command=self.gui_select_subject).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Create New", command=self.gui_create_flow).pack(pady=10, padx=20)

    def clear_content(self):
        self.timer_running = False 
        if hasattr(self, 'main_view'): self.main_view.destroy()
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_dashboard(self):
        self.clear_content()
        ctk.CTkLabel(self.main_view, text="Welcome!", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(120, 10))
        ctk.CTkLabel(self.main_view, text=f"Subjects managed: {len(self.database)}").pack()

    # --- SUBJECT & EXAM SELECTION ---
    def gui_select_subject(self):
        self.clear_content()
        ctk.CTkLabel(self.main_view, text="CHOOSE A SUBJECT", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        for sub in self.database.keys():
            ctk.CTkButton(self.main_view, text=sub, height=50, fg_color="#34495e",
                         command=lambda s=sub: self.gui_select_exam(s)).pack(pady=10, fill="x", padx=150)

    def gui_select_exam(self, sub):
        self.clear_content()
        ctk.CTkButton(self.main_view, text="← Back to Subjects", width=160, fg_color="#7f8c8d", 
                      command=self.gui_select_subject).pack(anchor="w", pady=10)
        
        scroll = ctk.CTkScrollableFrame(self.main_view, height=450)
        scroll.pack(fill="both", expand=True, padx=20)

        for exam in self.database[sub].keys():
            f = ctk.CTkFrame(scroll)
            f.pack(pady=8, fill="x", padx=5)
            ctk.CTkLabel(f, text=exam).pack(side="left", padx=20, pady=15)
            ctk.CTkButton(f, text="Start Test", command=lambda e=exam: self.gui_exam_detail(sub, e)).pack(side="right", padx=15)

    # --- EXAM DETAIL WITH TIMER & SHUFFLE ---
    def gui_exam_detail(self, sub, exam_name):
        self.clear_content()
        questions = self.database[sub][exam_name]
        
        header = ctk.CTkFrame(self.main_view, fg_color="transparent")
        header.pack(fill="x", pady=10)

        ctk.CTkButton(header, text="← Exit", width=80, fg_color="#7f8c8d", 
                      command=lambda: self.gui_select_exam(sub)).pack(side="left")
        
        self.lbl_timer = ctk.CTkLabel(header, text="Time Left: 00:00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#e74c3c")
        self.lbl_timer.pack(side="right", padx=20)

        scroll_exam = ctk.CTkScrollableFrame(self.main_view)
        scroll_exam.pack(fill="both", expand=True, pady=10)

        working_qs = [dict(q, original_idx=i) for i, q in enumerate(questions)]
        user_vars = {}

        def render_exam():
            for widget in scroll_exam.winfo_children(): widget.destroy()
            for i, q_data in enumerate(working_qs):
                f = ctk.CTkFrame(scroll_exam, corner_radius=12, border_width=1)
                f.pack(fill="x", pady=12, padx=15)
                ctk.CTkLabel(f, text=f"Q{i+1}: {q_data['q']}", wraplength=650, justify="left", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=15)
                
                var = ctk.StringVar(value="")
                user_vars[q_data['original_idx']] = {"var": var, "correct": q_data['correct'], "q": q_data['q']}
                
                shuffled_ans = q_data['all_ans'].copy()
                random.shuffle(shuffled_ans)
                for ans in shuffled_ans:
                    ctk.CTkRadioButton(f, text=ans, variable=var, value=ans).pack(anchor="w", padx=50, pady=6)

        # Timer starts: 1 min per question
        self.remaining_seconds = len(questions) * 60 
        self.timer_running = True
        self.update_timer()

        footer = ctk.CTkFrame(self.main_view, fg_color="transparent")
        footer.pack(fill="x", pady=15)
        
        ctk.CTkButton(footer, text="SHUFFLE", fg_color="#d35400", command=lambda: [random.shuffle(working_qs), render_exam()], height=45).pack(side="left", padx=30)
        
        def submit():
            self.timer_running = False
            wrongs = [f"Q: {v['q']}\nCorrect: {v['correct']}" for v in user_vars.values() if v['var'].get() != v['correct']]
            if not wrongs:
                messagebox.showinfo("Result", "Perfect Score!")
            else:
                self.show_wrong_popup(wrongs)

        ctk.CTkButton(footer, text="SUBMIT", fg_color="#27ae60", command=submit, height=45).pack(side="right", padx=30)
        render_exam()

    def update_timer(self):
        if self.timer_running and self.remaining_seconds >= 0:
            mins, secs = divmod(self.remaining_seconds, 60)
            self.lbl_timer.configure(text=f"Time Left: {mins:02d}:{secs:02d}")
            if self.remaining_seconds == 0:
                messagebox.showwarning("Time's Up", "Please submit your results.")
            else:
                self.remaining_seconds -= 1
                self.after(1000, self.update_timer)

    def show_wrong_popup(self, wrongs):
        win = ctk.CTkToplevel(self)
        win.title("Incorrect Answers")
        win.geometry("600x450")
        win.attributes("-topmost", True)
        txt = ctk.CTkTextbox(win, width=580, height=430)
        txt.pack(padx=10, pady=10)
        txt.insert("0.0", "WRONG ANSWERS:\n\n" + "\n\n".join(wrongs))
        txt.configure(state="disabled")

    # --- CREATE FLOW ---
    def gui_create_flow(self):
        self.clear_content()
        ctk.CTkLabel(self.main_view, text="ADD NEW SUBJECT/EXAM", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=40)
        f = ctk.CTkFrame(self.main_view, width=450); f.pack(pady=10)
        sub_e = ctk.CTkEntry(f, placeholder_text="Subject...", height=40); sub_e.pack(pady=10, padx=20, fill="x")
        exam_e = ctk.CTkEntry(f, placeholder_text="Exam...", height=40); exam_e.pack(pady=10, padx=20, fill="x")

        def start():
            s, e = sub_e.get(), exam_e.get()
            if s and e:
                if s not in self.database: self.database[s] = {}
                if e not in self.database[s]: self.database[s][e] = []
                self.gui_input_questions(s, e)

        ctk.CTkButton(self.main_view, text="Add Questions", command=start).pack(pady=20)

    def gui_input_questions(self, sub, exam):
        self.clear_content()
        q_txt = ctk.CTkTextbox(self.main_view, height=100); q_txt.pack(fill="x", padx=30, pady=5)
        a_txt = ctk.CTkTextbox(self.main_view, height=150); a_txt.pack(fill="x", padx=30, pady=5)
        a_txt.insert("0.0", "Line 1: CORRECT Answer\nOther Lines: Incorrect Answers")

        def save():
            q, ans = q_txt.get("0.0", "end").strip(), [l.strip() for l in a_txt.get("0.0", "end").split('\n') if l.strip()]
            if q and len(ans) >= 2:
                self.database[sub][exam].append({"q": q, "correct": ans[0], "all_ans": ans})
                self.save_data()
                q_txt.delete("0.0", "end"); a_txt.delete("0.0", "end")

        ctk.CTkButton(self.main_view, text="Save Question", fg_color="#2ecc71", command=save).pack(pady=10)
        ctk.CTkButton(self.main_view, text="Finish", command=self.show_dashboard).pack()

if __name__ == "__main__":
    app = ExamMasterApp()
    app.mainloop()