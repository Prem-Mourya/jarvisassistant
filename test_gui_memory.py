import tkinter as tk
import time
import os
import psutil

def check_memory():
    process = psutil.Process(os.getpid())
    print(f"Memory Usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    root.after(1000, check_memory)

root = tk.Tk()
root.title("Memory Test")
label = tk.Label(root, text="Testing Tkinter Memory Usage")
label.pack(padx=20, pady=20)

# Check memory after 1 second
root.after(1000, check_memory)

# Auto close after 3 seconds for automation
root.after(3000, root.destroy)

root.mainloop()
