import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

DB_FILE = "students_gui.db"

# DATABASE SETUP

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll INTEGER NOT NULL UNIQUE,
        branch TEXT NOT NULL,
        marks REAL NOT NULL
    )
''')
conn.commit()

# DATABASE FUNCTIONS

def insert_student(name, roll, branch, marks):
    try:
        cursor.execute("INSERT INTO students (name, roll, branch, marks) VALUES (?, ?, ?, ?)",
                       (name, roll, branch, marks))
        conn.commit()
        return True, "Student added."
    except sqlite3.IntegrityError:
        return False, "Roll number must be unique."
    except Exception as e:
        return False, str(e)

def fetch_all_students():
    cursor.execute("SELECT id, name, roll, branch, marks FROM students ORDER BY roll")
    return cursor.fetchall()

def update_student_db(roll, name=None, branch=None, marks=None):
    cursor.execute("SELECT id FROM students WHERE roll=?", (roll,))
    row = cursor.fetchone()
    if not row:
        return False, "Student not found."

    updates = []
    params = []

    if name is not None:
        updates.append("name=?"); params.append(name)
    if branch is not None:
        updates.append("branch=?"); params.append(branch)
    if marks is not None:
        updates.append("marks=?"); params.append(marks)

    params.append(roll)
    sql = f"UPDATE students SET {', '.join(updates)} WHERE roll=?"

    cursor.execute(sql, tuple(params))
    conn.commit()
    return True, "Student updated."

def delete_student_db(roll):
    cursor.execute("SELECT id FROM students WHERE roll=?", (roll,))
    if not cursor.fetchone():
        return False, "Student not found."

    cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
    conn.commit()
    return True, "Student deleted."

def fetch_top_performers(limit=5):
    cursor.execute("SELECT name, roll, marks FROM students ORDER BY marks DESC LIMIT ?", (limit,))
    return cursor.fetchall()

# LOGIN WINDOW

def show_login(root):
    login_win = tk.Toplevel()
    login_win.title("Login")
    login_win.geometry("300x200")
    login_win.resizable(False, False)

    tk.Label(login_win, text="Login to Continue", font=("Arial", 12, "bold")).pack(pady=10)

    tk.Label(login_win, text="Username:").pack()
    username_entry = tk.Entry(login_win)
    username_entry.pack()

    tk.Label(login_win, text="Password:").pack()
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack()

    def check_login():
        username = username_entry.get()
        password = password_entry.get()

        # FIXED CREDENTIALS (simple project)

        if username == "admin" and password == "12345":
            messagebox.showinfo("Login Successful", "Welcome Admin!")
            login_win.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    tk.Button(login_win, text="Login", command=check_login).pack(pady=10)
    login_win.grab_set()  # block access until login

# MAIN GUI APP

class StudentApp:
    def __init__(self, root):
        self.root = root
        root.title("Student Management System (GUI)")
        root.geometry("800x550")
        root.resizable(False, False)

        # ---------------- ENTRY FORM ----------------

        frm = ttk.LabelFrame(root, text="Student Details")
        frm.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm, text="Name:").grid(row=0, column=0, padx=6, pady=6)
        self.name_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=6)

        ttk.Label(frm, text="Roll:").grid(row=0, column=2, padx=6, pady=6)
        self.roll_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.roll_var, width=12).grid(row=0, column=3, padx=6)

        ttk.Label(frm, text="Branch:").grid(row=1, column=0, padx=6)
        self.branch_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.branch_var, width=25).grid(row=1, column=1, padx=6)

        ttk.Label(frm, text="Marks:").grid(row=1, column=2, padx=6)
        self.marks_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.marks_var, width=12).grid(row=1, column=3, padx=6)

        # Buttons Row 

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Add Student", command=self.add_student).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_selected).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).grid(row=0, column=3, padx=6)

        # ---------------- TABLE VIEW ----------------

        list_frame = ttk.LabelFrame(root, text="Students")
        list_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = ("id", "name", "roll", "branch", "marks")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)

        self.tree.heading("id", text="ID"); self.tree.column("id", width=40)
        self.tree.heading("name", text="Name"); self.tree.column("name", width=200)
        self.tree.heading("roll", text="Roll"); self.tree.column("roll", width=80)
        self.tree.heading("branch", text="Branch"); self.tree.column("branch", width=120)
        self.tree.heading("marks", text="Marks"); self.tree.column("marks", width=80)

        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ---------------- BOTTOM BUTTONS ----------------

        low = ttk.Frame(root)
        low.pack(fill="x", padx=10, pady=10)

        ttk.Button(low, text="Refresh", command=self.load_students).pack(side="left", padx=6)
        ttk.Button(low, text="Export CSV", command=self.export_csv).pack(side="left", padx=6)
        ttk.Button(low, text="Top Performers", command=self.top_performers).pack(side="left", padx=6)
        ttk.Button(low, text="Exit", command=root.destroy).pack(side="right", padx=6)

        self.load_students()

    # ---------- CRUD FUNCTIONS ----------
    
    def add_student(self):
        name = self.name_var.get().strip()
        roll = self.roll_var.get().strip()
        branch = self.branch_var.get().strip()
        marks = self.marks_var.get().strip()

        if not name or not roll or not branch or not marks:
            messagebox.showwarning("Error", "All fields required.")
            return

        try:
            roll = int(roll)
            marks = float(marks)
        except:
            messagebox.showwarning("Error", "Roll must be integer, marks numeric.")
            return

        ok, msg = insert_student(name, roll, branch, marks)
        if ok:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.load_students()
        else:
            messagebox.showerror("Error", msg)

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        vals = self.tree.item(selected[0], "values")

        self.name_var.set(vals[1])
        self.roll_var.set(vals[2])
        self.branch_var.set(vals[3])
        self.marks_var.set(vals[4])

    def update_selected(self):
        try:
            roll = int(self.roll_var.get())
            name = self.name_var.get()
            branch = self.branch_var.get()
            marks = float(self.marks_var.get())
        except:
            messagebox.showerror("Error", "Invalid input.")
            return

        ok, msg = update_student_db(roll, name=name, branch=branch, marks=marks)
        if ok:
            messagebox.showinfo("Updated", msg)
            self.load_students()
            self.clear_form()
        else:
            messagebox.showerror("Error", msg)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a row first.")
            return

        roll = self.tree.item(selected[0], "values")[2]
        if messagebox.askyesno("Confirm", f"Delete student with Roll {roll}?"):
            ok, msg = delete_student_db(roll)
            if ok:
                messagebox.showinfo("Deleted", msg)
                self.load_students()
                self.clear_form()
            else:
                messagebox.showerror("Error", msg)

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for r in fetch_all_students():
            self.tree.insert("", "end", values=r)

    def clear_form(self):
        self.name_var.set("")
        self.roll_var.set("")
        self.branch_var.set("")
        self.marks_var.set("")

    def export_csv(self):
        rows = fetch_all_students()
        if not rows:
            messagebox.showinfo("No Data", "No students to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV", "*.csv")],
                                                 initialfile="students_export.csv")
        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Roll", "Branch", "Marks"])
            writer.writerows(rows)

        messagebox.showinfo("Exported", "CSV exported successfully!")

    def top_performers(self):
        top = fetch_top_performers()
        if not top:
            messagebox.showinfo("No Data", "No students found.")
            return

        text = "Top Performers:\n\n"
        for t in top:
            text += f"{t[0]} | Roll: {t[1]} | Marks: {t[2]}\n"

        messagebox.showinfo("Top Performers", text)

# RUN APP WITH LOGIN

if __name__ == "__main__":
    
    root = tk.Tk()
    root.withdraw()  

    show_login(root)  
    root.deiconify()  

    app = StudentApp(root)
    root.mainloop()

    conn.close()
