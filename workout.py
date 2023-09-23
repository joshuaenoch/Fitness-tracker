import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring
from tkinter import simpledialog, messagebox
from tkcalendar import DateEntry
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


app = tk.Tk()
app.title("Fitness Tracker")

# App size
app.geometry("485x300")
app.resizable(True, True)

# Type submission
type_label = tk.Label(app, text="Exercise Type:")
type_label.grid(row=0, column=1, pady=(20, 0))


# Load exercise types from JSON file
def load_exercise_types():
    try:
        with open("exercise_types.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "Running": "minutes",
            "Pushups": "repetitions",
        }


options = load_exercise_types()

type_entry = ttk.Combobox(app, values=list(options.keys()), state="readonly")
type_entry.grid(row=1, column=1, padx=20)

# Amount submission
duration_label = tk.Label(app, text="Amount:")
duration_label.grid(row=3, column=1)
duration_entry = tk.Entry(app)
duration_entry.grid(row=4, column=1, pady=(0, 10))

# Date submission
date_label = tk.Label(app, text="Date:")
date_label.grid(row=5, column=1)
date_entry = DateEntry(app, date_pattern="yyyy-mm-dd")
date_entry.grid(row=6, column=1)


# Type configuration
def open_settings():
    settings_window = tk.Toplevel(app)
    settings_window.title("Exercise Type Settings")

    # Show types
    exercise_listbox = tk.Listbox(settings_window, selectmode=tk.SINGLE)
    for exercise, unit in options.items():
        exercise_listbox.insert(tk.END, f"{exercise} ({unit})")
    exercise_listbox.pack()

    # Add types
    def add_type():
        new_exercise = askstring("Add Exercise Type", "Enter a new exercise type:")
        if new_exercise:
            unit = askstring(
                "Unit",
                f"Enter the unit for '{new_exercise}' (e.g., minutes, repetitions):",
            )
            if unit:
                options[new_exercise] = unit
                type_entry["values"] = list(options.keys())
                exercise_listbox.insert(tk.END, f"{new_exercise} ({unit})")
                save_exercise_types(options)  # Save updated exercise types

    # Remove types
    def remove_type():
        selected_index = exercise_listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            selected_item = exercise_listbox.get(selected_index)
            exercise, unit = selected_item.split(" (")
            exercise = exercise.strip()
            result = messagebox.askyesno(
                "Confirm Deletion", f"Are you sure you want to remove '{exercise}'?"
            )
            if result:
                del options[exercise]
                type_entry["values"] = list(options.keys())
                exercise_listbox.delete(selected_index)
                save_exercise_types(options)  # Save updated exercise types

    # Edit types
    def edit_type():
        selected_index = exercise_listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            selected_item = exercise_listbox.get(selected_index)
            current_exercise, current_unit = selected_item.split(" (")
            current_exercise = current_exercise.strip()
            current_unit = current_unit.rstrip(")")  # Remove extra ")"
            new_exercise = askstring(
                "Edit Exercise Type",
                f"Edit exercise type (current type: {current_exercise}):",
                initialvalue=current_exercise,
            )
            if new_exercise:
                new_unit = askstring(
                    "Edit Unit",
                    f"Edit the unit for '{new_exercise}' (current unit: {current_unit}):",
                    initialvalue=current_unit,
                )
                if new_unit:
                    options[new_exercise] = new_unit
                    del options[current_exercise]
                    exercise_listbox.delete(selected_index)
                    exercise_listbox.insert(tk.END, f"{new_exercise} ({new_unit})")
                    type_entry["values"] = list(options.keys())
                    save_exercise_types(options)

    # Buttons for type configuration
    add_button = tk.Button(settings_window, text="Add Exercise Type", command=add_type)
    add_button.pack()
    remove_button = tk.Button(
        settings_window, text="Remove Exercise Type", command=remove_type
    )
    remove_button.pack()
    edit_button = tk.Button(
        settings_window, text="Edit Exercise Type", command=edit_type
    )
    edit_button.pack()


# Function to save exercise types to a JSON file
def save_exercise_types(exercise_types):
    with open("exercise_types.json", "w") as file:
        json.dump(exercise_types, file)


# Type configuration button
settings_button = tk.Button(app, text="Settings", command=open_settings)
settings_button.grid(row=2, column=1, pady=(0, 10))


def show_chart():
    chart_window = tk.Toplevel(app)
    chart_window.title("Chart")
    chart_window.geometry("430x300")

    fig, ax = plt.subplots(figsize=(2, 1))
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas_widget = canvas.get_tk_widget()

    def update_chart_view():
        ax.clear()
        exercise_data = {}
        for workout in workout_data:
            date = workout["date"]
            exercise_type = workout["exercise_type"]
            amount = workout["amount"]
            unit = workout["unit"]
            if date not in exercise_data:
                exercise_data[date] = {}
            exercise_data[date][exercise_type] = exercise_data[date].get(
                exercise_type, 0
            ) + float(amount)

        for exercise_type, data in exercise_data.items():
            dates = list(data.keys())
            values = [data[date] for date in dates]
            ax.plot(dates, values, marker="o", label=exercise_type)

        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")
        ax.legend()

        canvas.get_tk_widget().configure(
            width=chart_window.winfo_width(), height=chart_window.winfo_height()
        )
        canvas.draw()

    update_chart_view()

    canvas_widget.pack(fill=tk.BOTH, expand=True)


# Button to activate the chart
chart_view_button = tk.Button(app, text="See Chart", command=show_chart)
chart_view_button.grid(row=0, column=2)

# Display the workouts saved
workout_listbox = tk.Listbox(app, height=10, width=45)
workout_listbox.grid(row=1, column=2, rowspan=7, sticky="nsew")


# Load data (upon opening)
def load_workout_data():
    try:
        with open("workouts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


workout_data = load_workout_data()


# Display previous data
for workout in workout_data:
    date = workout["date"]
    exercise_type = workout["exercise_type"]
    amount = workout["amount"]
    unit = workout["unit"]
    workout_display = f" {date} - {exercise_type} - {amount} {unit}\n"
    workout_listbox.insert(tk.END, workout_display)


# Remove selected workout
def remove_workout():
    selected_index = workout_listbox.curselection()
    if selected_index:
        selected_index = int(selected_index[0])
        workout_listbox.delete(selected_index)
        del workout_data[selected_index]
        save_workout_data(workout_data)


# Save data (upon adding workout)
def save_workout_data(self):
    with open("workouts.json", "w") as file:
        json.dump(workout_data, file)


# Add workouts
def add_workout():
    # Default values
    amount = "Unknown"
    date = "No date set"

    # Input values
    exercise_type = type_entry.get()
    if not exercise_type:
        # User must input exercise type
        messagebox.showerror("Error", "Please select a workout type.")
        return
    unit = options.get(exercise_type, "amount")
    user_amount = duration_entry.get()
    if user_amount:
        amount = user_amount
    user_date = date_entry.get()
    if user_date:
        date = user_date
    workout_data.append(
        {"date": date, "exercise_type": exercise_type, "amount": amount, "unit": unit}
    )
    workout_display = f" {date} - {exercise_type} - {amount} {unit}\n"
    workout_listbox.insert(tk.END, workout_display)
    save_workout_data(workout_data)

    # Resetting the prompt fields
    type_entry.set("")
    duration_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)


# Add and remove workout buttons
add_workout_button = tk.Button(app, text="Add Workout", command=add_workout)
add_workout_button.grid(row=7, column=1)
remove_workout_button = tk.Button(app, text="Remove Workout", command=remove_workout)
remove_workout_button.grid(row=8, column=2, pady=15)

final_message = tk.Label(app, text="More updates to come!")
final_message.grid(row=10, column=1, columnspan=2)


# Kill the process on closing
def on_closing():
    app.quit()


app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()
