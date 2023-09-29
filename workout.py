# This app saves your workout data and graphs it for you
# Still in development

import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring
from tkinter import simpledialog, messagebox
from tkcalendar import DateEntry
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dateutil import parser
from collections import defaultdict
import matplotlib.dates as mdates


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
            "Jogging": "miles",
            "Pushups": "repetitions",
        }


# The dropdown box that lists workout types
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
                f"Enter the unit for '{new_exercise}' (e.g., miles, repetitions):",
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


# The chart
def show_chart():
    # Popout window that graphs the workouts by type
    chart_window = tk.Toplevel(app)
    chart_window.title("Chart")
    chart_window.geometry("600x500")

    # Select the exercise type + notice
    chart_type_label = tk.Label(chart_window, text="Select Exercise Type:")
    chart_type_label.pack()
    notice = tk.Label(
        chart_window, text="(Chart only works for workout types with 2 or more entries)"
    )
    notice.pack()

    # Dropdown box for exercise type selection
    chart_type_var = tk.StringVar()
    chart_type_menu = ttk.Combobox(
        chart_window,
        textvariable=chart_type_var,
        values=list(options.keys()),
        state="readonly",
    )
    chart_type_menu.pack(pady=(0, 10))
    chart_type_menu.set("Jogging")

    # Load and add workouts by type
    exercise_data = defaultdict(list)
    for workout in workout_data:
        date = parser.parse(workout["date"])
        exercise_type = workout["exercise_type"]
        amount = float(workout["amount"])
        exercise_data[exercise_type].append((date, amount))

    fig, ax = plt.subplots(figsize=(6, 4))

    # Plot/update chart
    def update_chart():
        selected_type = chart_type_var.get()
        ax.clear()
        if selected_type in exercise_data:
            data_points = exercise_data[selected_type]
            dates, amounts = zip(*data_points)
            plt.plot(dates, amounts, label=selected_type)

        # Will add years soon, must first figure out everything design-wise
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        # The text of the graph like axis labels and legends
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")
        ax.set_title(f"Your {selected_type} Over Time")
        ax.legend(loc="upper left")

        canvas.draw()

    # Button to update chart after changing types
    update_chart_button = tk.Button(
        chart_window, text="Update Chart", command=update_chart
    )
    update_chart_button.pack()

    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    update_chart()


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
def save_workout_data(workout_data):
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
