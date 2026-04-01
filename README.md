# College Quiz App

A feature-rich, interactive GUI-based quiz application built with Python for college coursework.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## About the Project
This is a complete GUI-based Quiz Application developed as a college project. The application allows students to take subject-wise quizzes by selecting their grade, subject, unit, and the number of questions they want to attempt.

It uses a combination of SQLite database and CSV file for storing and managing questions. After answering the questions, users can review their answers to see which ones were correct or incorrect.

As an aspiring Blockchain Developer, this project helped me strengthen my Python skills — especially in building GUI applications, working with databases, and structuring multi-file projects.

## Key Features
- Multi-step selection: Grade → Subject → Unit → Number of Questions
- Modern GUI Interface built with Tkinter
- Dynamic question loading from SQLite database + CSV
- Randomized questions for better variety
- Real-time answer submission with immediate feedback
- Review System: View all questions with correct/incorrect answers at the end
- Score calculation and final result display
- Separate scripts for database setup and data insertion

## Tech Stack
- Python 3
- Tkinter – Graphical User Interface
- SQLite3 – Database management
- CSV – Initial question data source
- Random – Question shuffling
- OS – File handling between modules

## Project Structure
 ```bash
 college-quiz-app/
 ├── Test_project.py          # Main GUI application (Run this file)
 ├── insert_data.py           # Script to insert questions into the database
 ├── setup_database.py        # Creates and sets up the SQLite database
 ├── questions.csv            # Source file containing questions
 └── README.md

```
## How to Run the Project

1. Clone or download the repository.
2. Open terminal/command prompt in the project folder.
3. Run setup (only once):
   ```bash
   python setup_database.py
   python insert_data.py
4. Start the quiz:
   ```bash
   python Test_project.py

## What I Learned
- Building a complete GUI app with Tkinter
- Working with SQLite database (create, insert, query)
- Reading CSV data and connecting multiple files
- Structuring a multi-file Python project
- Managing step-by-step user flow
- Adding review and feedback features

This project improved my Python skills significantly and gave me confidence for future blockchain projects.

## Connect With Me
- GitHub: https://github.com/Hamad-pk
- Email: hamad.emp@gmail.com
- Open to feedback, suggestions, and Web3/Blockchain internship opportunities

---

Aspiring Blockchain Developer | Lahore, Pakistan
