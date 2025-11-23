import sqlite3

# Database Setup

conn = sqlite3.connect("students.db")
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

# Add Student

def add_student():
    print("\n--- Add Student ---")
    name = input("Enter name: ")
    roll = int(input("Enter roll number: "))
    branch = input("Enter branch: ")
    marks = float(input("Enter marks: "))

    try:
        cursor.execute("INSERT INTO students (name, roll, branch, marks) VALUES (?, ?, ?, ?)",
                       (name, roll, branch, marks))
        conn.commit()
        print("Student added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Roll number must be unique.")

# View Students

def view_students():
    print("\n--- Student Records ---")
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    if not data:
        print("No records found.")
        return

    for row in data:
        print(f"ID: {row[0]}, Name: {row[1]}, Roll: {row[2]}, Branch: {row[3]}, Marks: {row[4]}")

# Update Student

def update_student():
    print("\n--- Update Student ---")
    roll = int(input("Enter roll number to update: "))

    cursor.execute("SELECT * FROM students WHERE roll=?", (roll,))
    record = cursor.fetchone()

    if record:
        print("1. Update Name")
        print("2. Update Branch")
        print("3. Update Marks")
        choice = int(input("Choose field to update: "))

        if choice == 1:
            new_name = input("Enter new name: ")
            cursor.execute("UPDATE students SET name=? WHERE roll=?", (new_name, roll))

        elif choice == 2:
            new_branch = input("Enter new branch: ")
            cursor.execute("UPDATE students SET branch=? WHERE roll=?", (new_branch, roll))

        elif choice == 3:
            new_marks = float(input("Enter new marks: "))
            cursor.execute("UPDATE students SET marks=? WHERE roll=?", (new_marks, roll))

        conn.commit()
        print("Record updated successfully!")
    else:
        print("No student found with this roll number.")

# Delete Student

def delete_student():
    print("\n--- Delete Student ---")
    roll = int(input("Enter roll number to delete: "))

    cursor.execute("SELECT * FROM students WHERE roll=?", (roll,))
    record = cursor.fetchone()

    if record:
        cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
        conn.commit()
        print("Student deleted successfully!")
    else:
        print("No student found with this roll number.")

# Generate Report

def generate_report():
    print("\n--- Student Marks Report ---")
    cursor.execute("SELECT name, roll, marks FROM students ORDER BY marks DESC")
    data = cursor.fetchall()

    if not data:
        print("No records found.")
        return

    print("\nTop Performers:")
    for row in data:
        print(f"Name: {row[0]}, Roll: {row[1]}, Marks: {row[2]}")

# Main Menu

while True:
    
    print("\n==============================")
    print("  Student Management System")
    print("==============================")
    print("1. Add Student")
    print("2. View Students")
    print("3. Update Student")
    print("4. Delete Student")
    print("5. Generate Report")
    print("6. Exit")

    option = int(input("Enter your choice: "))

    if option == 1:
        add_student()
    elif option == 2:
        view_students()
    elif option == 3:
        update_student()
    elif option == 4:
        delete_student()
    elif option == 5:
        generate_report()
    elif option == 6:
        print("Exiting...")
        break
    else:
        print("Invalid choice! Try again.")
