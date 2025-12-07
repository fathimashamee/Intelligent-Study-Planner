# Intelligent Study Planner with Timetable

## Overview
The **Intelligent Study Planner** is an AI-assisted application designed to help students efficiently plan their study schedule based on subject difficulty, deadlines, and past performance. It provides a personalized study timetable, predicts required study hours using a simple machine learning model, detects deadline clashes, and offers reminders for upcoming deadlines.

This project was developed as a **Mini Project** for the course, with submission date: **30th November 2025**.

---

## Features

- **Add Subjects:** Users can add subjects with difficulty level, deadline, and expected marks.
- **Predict Study Hours:** Uses a rule-based approach and an optional ML model (Linear Regression) to suggest daily study hours.
- **Clash Detection:** Detects overlapping deadlines and suggests automatic adjustments to avoid conflicts.
- **Rescheduling:** Users can manually reschedule subjects if needed.
- **Study Plan Generation:** Creates a daily study plan based on subject priority, difficulty, and urgency.
- **Timetable Generation:** Generates a multi-day timetable with configurable study hours, breaks, and subject rotation preferences.
- **Reminders:** Notifies users of upcoming deadlines within a configurable reminder window.
- **Reset Functionality:** Allows clearing all subjects to start planning afresh.

---

## Technology Stack

- **Programming Language:** Python 3.x
- **Libraries:** 
  - `json` (for data storage)
  - `datetime` (for date calculations)
  - `pathlib` (for file handling)
  - `math` (for calculations)
  - `numpy` and `scikit-learn` (optional, for ML-based predictions)
- **Version Control:** Git & GitHub

---

## Project Structure

Intelligent-Study-Planner/
│
├── config/ # Configuration files (difficulty, messages, settings)
│ ├── difficulty.json
│ ├── messages.json
│ ├── ml_data.json
│ └── settings.json
│
├── data/ # User subject data
│ └── subjects.json
│
├── intelligent_study_planner.py # Main Python program
├── README.md
└── .gitignore


---

## Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/YourUsername/Intelligent-Study-Planner.git
cd Intelligent-Study-Planner

Install Dependencies

If using ML features:
pip install numpy scikit-learn

Run the Application
python intelligent_study_planner.py


Usage
Once running, the application provides a command-line interface with the following commands:
| Command                                                         | Description                                    |
| --------------------------------------------------------------- | ---------------------------------------------- |
| `add subject <name> <difficulty> <deadline YYYY-MM-DD> <marks>` | Add a new subject                              |
| `plan`                                                          | Generate study plan with predicted daily hours |
| `schedule`                                                      | Show detailed study schedule                   |
| `reschedule <subject> <YYYY-MM-DD>`                             | Reschedule a subject                           |
| `timetable`                                                     | Generate multi-day timetable                   |
| `reset`                                                         | Clear all subjects and start fresh             |
| `exit`                                                          | Exit the program                               |


Example
> add subject Math high 2025-12-10 75
✔ Added subject 'Math'

> plan
📚 Study Plan Generated!

> schedule
------------ Study Schedule ------------
Subject: Math
  Study Hours/Day : 4 hours
  Days Left       : 3
  Deadline        : 2025-12-10
----------------------------------------
⚠️ Reminder: 'Math' deadline is in 3 day(s)!

Contribution

This project is developed for educational purposes. Contributions are welcome via pull requests with proper documentation and testing.

License

This project is released under the MIT License.



