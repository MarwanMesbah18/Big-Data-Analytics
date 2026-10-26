"""Optional GUI: pick a task, press Run, see the output.
It just runs the three task scripts and shows what they print."""
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

ROOT = os.path.dirname(os.path.abspath(__file__))

# Task name shown in the dropdown -> script to run
TASKS = {
    "Word Count": "word-count/word_count.py",
    "Top-K Words": "top-k-words/top_k.py",
    "Inverted Index": "inverted-index/inverted_index.py",
}


def run_task():
    script = os.path.join(ROOT, TASKS[task_box.get()])
    command = [sys.executable, script]
    if task_box.get() == "Top-K Words":
        command.append(k_entry.get())  # K is passed as the argument
    result = subprocess.run(command, capture_output=True, text=True)
    output.delete("1.0", tk.END)
    output.insert(tk.END, result.stdout + result.stderr)


window = tk.Tk()
window.title("MapReduce Tasks")

top = ttk.Frame(window, padding=8)
top.pack(fill="x")

ttk.Label(top, text="Task:").pack(side="left")
task_box = ttk.Combobox(top, values=list(TASKS), state="readonly", width=16)
task_box.current(0)
task_box.pack(side="left", padx=4)

ttk.Label(top, text="K (Top-K only):").pack(side="left")
k_entry = ttk.Entry(top, width=4)
k_entry.insert(0, "10")
k_entry.pack(side="left", padx=4)

ttk.Button(top, text="Run", command=run_task).pack(side="left", padx=4)

output = tk.Text(window, width=70, height=30)
output.pack(fill="both", expand=True, padx=8, pady=8)

window.mainloop()
