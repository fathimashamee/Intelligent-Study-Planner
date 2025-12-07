"""
Intelligent Study Planner — Corrected with Timetable
"""

import json
import datetime
from pathlib import Path
import math

# Optional ML import — fallback if sklearn unavailable
try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

# ------------------------------- Paths & Defaults -------------------------------
BASE = Path(__file__).parent
CONFIG_DIR = BASE / "config"
DATA_DIR = BASE / "data"
CONFIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

DIFF_FILE = CONFIG_DIR / "difficulty.json"
MSG_FILE = CONFIG_DIR / "messages.json"
ML_FILE = CONFIG_DIR / "ml_data.json"
SET_FILE = CONFIG_DIR / "settings.json"
SUBJECTS_FILE = DATA_DIR / "subjects.json"

DEFAULT_DIFF = {"low": 1, "medium": 2, "high": 3}
DEFAULT_MSGS = {
    "welcome": "🤖 Intelligent Study Planner (Beginner)",
    "invalid_cmd": "❌ Unknown command!",
    "cmd_hint": "Try: add subject / plan / schedule / reschedule / timetable / reset / exit",
    "invalid_diff": "❌ Difficulty must be low / medium / high",
    "added": "✔ Added subject '{name}'",
    "invalid_format_add": "❌ Use: add subject <name> <difficulty> <deadline> <marks>",
    "invalid_format_res": "❌ Use: reschedule <subject> <YYYY-MM-DD>",
    "invalid_date": "❌ Date must be YYYY-MM-DD",
    "not_found": "❌ Subject '{name}' not found!",
}
DEFAULT_ML = {"X": [[1, 80], [2, 70], [3, 60], [3, 40], [2, 50], [1, 90]], "y": [1, 2, 3, 4, 3, 1]}
DEFAULT_SETTINGS = {
    "reminder_days": 2,
    "reschedule_strategy": "round_robin",  # or 'push_forward'
    "plan_min_hours": 1
}


def ensure_default(path: Path, default_obj):
    if not path.exists():
        with path.open("w", encoding="utf-8") as f:
            json.dump(default_obj, f, indent=2)


for file, default in [(DIFF_FILE, DEFAULT_DIFF), (MSG_FILE, DEFAULT_MSGS),
                      (ML_FILE, DEFAULT_ML), (SET_FILE, DEFAULT_SETTINGS), (SUBJECTS_FILE, [])]:
    ensure_default(file, default)

# ------------------------------- Load Configs -------------------------------
def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


difficulty_map = load_json(DIFF_FILE)
messages = load_json(MSG_FILE)
ml_data = load_json(ML_FILE)
settings = load_json(SET_FILE)


# ------------------------------- Subjects -------------------------------
def load_subjects():
    raw = load_json(SUBJECTS_FILE)
    fixed = []
    for s in raw:
        item = s.copy()
        try:
            item["deadline"] = datetime.datetime.strptime(item["deadline"], "%Y-%m-%d").date()
        except Exception:
            item["deadline"] = datetime.date.today()
        fixed.append(item)
    return fixed


def save_subjects(subs):
    serializable = []
    for s in subs:
        item = s.copy()
        d = item.get("deadline")
        if isinstance(d, (datetime.date, datetime.datetime)):
            item["deadline"] = d.strftime("%Y-%m-%d")
        serializable.append(item)
    with SUBJECTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


subjects = load_subjects()


# ------------------------------- Date Helpers -------------------------------
def parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def days_between(a: datetime.date, b: datetime.date) -> int:
    return (b - a).days


# ------------------------------- ML Model -------------------------------
model = None
if SKLEARN_AVAILABLE:
    try:
        X = np.array(ml_data["X"])
        y = np.array(ml_data["y"])
        model = LinearRegression().fit(X, y)
    except Exception:
        model = None


def predict_study_hours(diff: int, marks: int) -> int:
    if model:
        try:
            pred = model.predict([[diff, marks]])[0]
            return max(settings.get("plan_min_hours", 1), int(round(pred)))
        except Exception:
            pass
    base = settings.get("plan_min_hours", 1)
    diff_factor = diff
    marks_factor = max(0, 100 - marks) / 50
    return max(1, base + math.ceil(diff_factor * (1 + marks_factor)))


# ------------------------------- Clash Detection -------------------------------
def detect_clashes(subs):
    dates = [s["deadline"] for s in subs]
    return len(dates) != len(set(dates))


def rearrange_schedule(subs):
    """Conflict-free unique deadlines."""
    used = set()
    for s in sorted(subs, key=lambda x: x['deadline']):
        d = s['deadline']
        while d in used:
            d += datetime.timedelta(days=1)
        s['deadline'] = d
        used.add(d)


def handle_clashes():
    date_map = {}
    for s in subjects:
        d = s["deadline"]
        date_map.setdefault(d, []).append(s["name"])
    conflicts = {d: names for d, names in date_map.items() if len(names) > 1}
    if not conflicts:
        return
    print("\n⚠️ Deadline clash detected:")
    for d, names in conflicts.items():
        print(f"  {d}: {', '.join(names)}")
    choice = input("\nAuto-adjust based on settings? (yes/no): ").strip().lower()
    if choice == "yes":
        rearrange_schedule(subjects)
        save_subjects(subjects)
        print("✔ Deadlines rearranged conflict-free!\n")
    else:
        print("✔ Keeping original deadlines.\n")


# ------------------------------- Commands -------------------------------
def add_subject_command(cmd: str):
    parts = cmd.split()
    if len(parts) != 6:
        print(messages["invalid_format_add"])
        return
    _, _, name, diff_str, deadline_str, marks_str = parts
    if diff_str.lower() not in difficulty_map:
        print(messages["invalid_diff"])
        return
    try:
        deadline = parse_date(deadline_str)
    except Exception:
        print(messages["invalid_date"])
        return
    try:
        marks = int(marks_str)
    except Exception:
        print("❌ Marks must be an integer")
        return
    subject = {
        "name": name,
        "difficulty": difficulty_map[diff_str.lower()],
        "deadline": deadline,
        "marks": marks
    }
    subjects.append(subject)
    save_subjects(subjects)
    print(messages["added"].format(name=name))
    if detect_clashes(subjects):
        handle_clashes()


def generate_plan():
    if not subjects:
        print("⚠️ No subjects added.")
        return None
    today = datetime.date.today()
    schedule = {}
    for s in subjects:
        diff = s["difficulty"]
        marks = s["marks"]
        deadline = s["deadline"]
        schedule[s["name"]] = {
            "daily_hours": predict_study_hours(diff, marks),
            "days_left": max(1, days_between(today, deadline)),
            "deadline": deadline
        }
    print("\n📚 Study Plan Generated!")
    return schedule


def show_schedule(schedule_dict):
    print("\n------------ Study Schedule ------------")
    for subject, info in schedule_dict.items():
        print(f"\nSubject: {subject}")
        print(f"  Study Hours/Day : {info['daily_hours']} hours")
        print(f"  Days Left       : {info['days_left']}")
        print(f"  Deadline        : {info['deadline'].strftime('%Y-%m-%d')}")
    print("----------------------------------------")
    show_reminders()


def show_reminders():
    today = datetime.date.today()
    rem_days = settings.get("reminder_days", 2)
    for s in subjects:
        d = s["deadline"]
        days_left = days_between(today, d)
        if days_left <= rem_days:
            print(f"⚠️ Reminder: '{s['name']}' deadline is in {days_left} day(s)!")


def reschedule_subject(cmd: str):
    parts = cmd.split()
    if len(parts) != 3:
        print(messages["invalid_format_res"])
        return
    _, name, new_date_str = parts
    try:
        new_date = parse_date(new_date_str)
    except Exception:
        print(messages["invalid_date"])
        return
    for s in subjects:
        if s["name"] == name:
            s["deadline"] = new_date
            save_subjects(subjects)
            print(f"✔ Rescheduled '{name}' to {new_date.strftime('%Y-%m-%d')}")
            return
    print(messages["not_found"].format(name=name))


def reset_command():
    subjects.clear()
    save_subjects(subjects)
    print("🔄 All subjects cleared. Starting fresh.")


# ------------------------------- Timetable -------------------------------
def generate_timetable(subjects, plan):
    if not subjects or not plan:
        print("⚠️ No subjects to schedule!")
        return
    start_hour = int(input("Start hour (24h, e.g., 7 for 7:00am): "))
    end_hour = int(input("End hour (24h, e.g., 22 for 10:00pm): "))
    block_hours = float(input("Study block duration in hours: "))
    break_minutes = int(input("Break duration in minutes: "))
    print("\nChoose subject order preference:")
    print("A. Fixed priority order")
    print("B. Rotate subjects each day")
    print("C. Urgency-based (closer deadlines first)")
    order_pref = input("Choose (A/B/C): ").strip().upper()

    timetable = {}
    today = datetime.date.today()
    last_day = max(s['deadline'] for s in subjects)
    total_days = (last_day - today).days + 1

    fixed_order = [s['name'] for s in subjects]

    for day_offset in range(total_days):
        day_date = today + datetime.timedelta(days=day_offset)
        active_subjects = [s for s in subjects if s['deadline'] >= day_date]
        if not active_subjects:
            continue

        # Order subjects
        if order_pref == 'A':
            day_order = [s['name'] for s in active_subjects if s['name'] in fixed_order]
        elif order_pref == 'B':
            day_order = [s['name'] for i, s in enumerate(active_subjects)]
            day_order = day_order[day_offset % len(day_order):] + day_order[:day_offset % len(day_order)]
        elif order_pref == 'C':
            day_order = sorted(active_subjects, key=lambda x: x['deadline'])
            day_order = [s['name'] for s in day_order]
        else:
            day_order = [s['name'] for s in active_subjects]

        hours_left = {s['name']: plan[s['name']]['daily_hours'] for s in active_subjects}
        current_time = datetime.datetime.combine(day_date, datetime.time(start_hour, 0))
        end_time = datetime.datetime.combine(day_date, datetime.time(end_hour, 0))
        day_schedule = []

        while current_time + datetime.timedelta(hours=block_hours) <= end_time and any(hours_left.values()):
            for sub_name in day_order:
                if hours_left[sub_name] <= 0:
                    continue
                block_end = current_time + datetime.timedelta(hours=min(block_hours, hours_left[sub_name]))
                day_schedule.append(f"{current_time.strftime('%H:%M')} - {block_end.strftime('%H:%M')} : {sub_name}")
                hours_left[sub_name] -= min(block_hours, hours_left[sub_name])
                current_time = block_end + datetime.timedelta(minutes=break_minutes)
                if current_time + datetime.timedelta(hours=block_hours) > end_time:
                    break
            if all(h <= 0 for h in hours_left.values()):
                break

        timetable[day_date] = day_schedule

    print("\n📅 Multi-Day Timetable:\n")
    for day, blocks in timetable.items():
        print(f"📆 {day}")
        for b in blocks:
            print(b)
        print()


# ------------------------------- Main Loop -------------------------------
def main():
    print(messages.get("welcome", "Study Planner"))
    print("\nCommands: add subject <name> <difficulty> <deadline YYYY-MM-DD> <marks>, plan, schedule, reschedule <subject> <YYYY-MM-DD>, timetable, reset, exit\n")

    while True:
        try:
            cmd = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGood luck to your studies! 👋")
            break
        if not cmd:
            continue
        low = cmd.lower()

        if low.startswith("add subject"):
            add_subject_command(cmd)
        elif low == "plan":
            plan = generate_plan()
        elif low == "schedule":
            if detect_clashes(subjects):
                handle_clashes()
            plan = generate_plan()
            if plan:
                show_schedule(plan)
        elif low.startswith("reschedule"):
            reschedule_subject(cmd)
        elif low == "reset":
            reset_command()
        elif low == "timetable":
            plan = generate_plan()
            if plan:
                generate_timetable(subjects, plan)
        elif low == "exit":
            print("\nGood luck to your studies! 👋")
            break
        else:
            print(messages.get("invalid_cmd", "❌ Unknown command!"))
            print(messages.get("cmd_hint", "Try: add subject / plan / schedule / reschedule / timetable / reset / exit"))


if __name__ == "__main__":
    main()
