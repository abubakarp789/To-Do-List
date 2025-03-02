import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class AdvancedTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")
        self.root.geometry("400x500")
        
        # File paths
        self.data_dir = os.path.join(os.path.expanduser("~"), ".todo_app")
        self.tasks_file = os.path.join(self.data_dir, "tasks.json")
        self.categories_file = os.path.join(self.data_dir, "categories.json")
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Task storage
        self.tasks = []
        
        # Update color scheme for better UI
        self.bg_color = "#f0f2f5"  # Lighter background
        self.sidebar_color = "#ffffff"  # White sidebar
        self.primary_color = "#1a73e8"  # Google blue
        self.text_color = "#202124"  # Dark text
        self.light_text = "#5f6368"  # Google gray
        self.accent_color = "#ea4335"  # Google red
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Add window padding
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Set initial category to Home
        self.current_category = {"name": "Home"}
        
        # Create main layout with improved styling
        self.create_main_layout()
        self.create_menu()
        self.load_data()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Update initial UI
        self.update_task_list()
        self.update_category_counts()
        self.update_greeting()
        
        # Set up auto-save on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_main_layout(self):
        # Main container with shadow effect
        self.main_container = tk.Frame(
            self.root,
            bg=self.bg_color,
            highlightbackground="#e0e0e0",
            highlightthickness=1
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Sidebar with improved styling
        self.sidebar_frame = tk.Frame(
            self.main_container,
            width=280,
            bg=self.sidebar_color,
            relief="flat"
        )
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar_frame.pack_propagate(False)
        
        # Content area with card-like appearance
        self.content_frame = tk.Frame(
            self.main_container,
            bg=self.bg_color,
            relief="flat"
        )
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create improved sidebar and content
        self.create_sidebar()
        self.create_content_area()

    def create_category_button(self, category):
        # Create hoverable category button
        category_frame = tk.Frame(
            self.categories_frame,
            bg=self.sidebar_color,
            height=40,
            cursor="hand2"
        )
        category_frame.pack(fill=tk.X, pady=2)
        category_frame.pack_propagate(False)
        
        # Add hover effect
        def on_enter(e):
            category_frame.configure(bg="#f8f9fa")
            
        def on_leave(e):
            category_frame.configure(bg=self.sidebar_color)
        
        category_frame.bind("<Enter>", on_enter)
        category_frame.bind("<Leave>", on_leave)
        
        # Category content with improved styling
        icon_label = tk.Label(
            category_frame,
            text=category["icon"],
            font=("Segoe UI", 14),
            bg=category_frame.cget("bg"),
            fg=category["color"] if category["color"] != "#FFFFFF" else self.text_color,
            width=2
        )
        icon_label.pack(side=tk.LEFT, padx=(15, 5))
        
        name_label = tk.Label(
            category_frame,
            text=category["name"],
            font=("Segoe UI", 11),
            bg=category_frame.cget("bg"),
            fg=self.text_color,
            anchor="w"
        )
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        count_label = tk.Label(
            category_frame,
            text=str(category["count"]),
            font=("Segoe UI", 11),
            bg=category_frame.cget("bg"),
            fg=self.light_text,
            width=3
        )
        count_label.pack(side=tk.RIGHT, padx=15)
        
        # Bind click events
        for widget in [category_frame, icon_label, name_label, count_label]:
            widget.bind("<Button-1>", lambda e, cat=category: self.select_category(cat))

    def create_task_item(self, parent, task):
        # Create modern task card
        task_frame = tk.Frame(
            parent,
            bg=self.bg_color,
            relief="flat",
            highlightbackground="#e0e0e0",
            highlightthickness=1
        )
        task_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Add hover effect
        def on_enter(e):
            task_frame.configure(bg="#f8f9fa")
            
        def on_leave(e):
            task_frame.configure(bg=self.bg_color)
        
        task_frame.bind("<Enter>", on_enter)
        task_frame.bind("<Leave>", on_leave)
        
        # Checkbox with custom style
        checkbox_var = tk.BooleanVar(value=task.get("completed", False))
        checkbox = ttk.Checkbutton(
            task_frame,
            variable=checkbox_var,
            command=lambda t=task: self.toggle_task_completion(t),
            style="Custom.TCheckbutton"
        )
        checkbox.pack(side=tk.LEFT, padx=10)
        
        # Task content
        content_frame = tk.Frame(task_frame, bg=task_frame.cget("bg"))
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=8)
        
        # Title with strike-through if completed
        title_text = task.get("title", "Untitled Task")
        if task.get("completed", False):
            title_text = "✓ " + title_text
        
        title_label = tk.Label(
            content_frame,
            text=title_text,
            font=("Segoe UI", 11, "overstrike" if task.get("completed", False) else "normal"),
            bg=content_frame.cget("bg"),
            fg=self.light_text if task.get("completed", False) else self.text_color,
            anchor="w"
        )
        title_label.pack(fill=tk.X)
        
        # Task details
        details_frame = tk.Frame(content_frame, bg=content_frame.cget("bg"))
        details_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Time slot
        if task.get("time_slot"):
            tk.Label(
                details_frame,
                text="🕒 " + task["time_slot"],
                font=("Segoe UI", 9),
                bg=details_frame.cget("bg"),
                fg=self.light_text
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Category
        if task.get("category"):
            category = next((c for c in self.categories if c["name"] == task["category"]), None)
            if category:
                tk.Label(
                    details_frame,
                    text=f"{category['icon']} {category['name']}",
                    font=("Segoe UI", 9),
                    bg=details_frame.cget("bg"),
                    fg=self.light_text
                ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Action buttons
        action_frame = tk.Frame(task_frame, bg=task_frame.cget("bg"))
        action_frame.pack(side=tk.RIGHT, padx=10)
        
        # Edit button
        edit_btn = tk.Label(
            action_frame,
            text="✏️",
            font=("Segoe UI", 12),
            bg=action_frame.cget("bg"),
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        edit_btn.bind("<Button-1>", lambda e, t=task: self.view_task_details(t))
        
        # Delete button
        delete_btn = tk.Label(
            action_frame,
            text="🗑️",
            font=("Segoe UI", 12),
            bg=action_frame.cget("bg"),
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        delete_btn.bind("<Button-1>", lambda e, t=task: self.delete_task(t))

    def add_task(self):
        task = self.task_var.get().strip()
        if task:
            # Create task in dictionary format
            new_task = {
                "title": task,
                "category": "Home",
                "completed": False
            }
            self.tasks.append(new_task)
            self.update_task_list()
            self.update_category_counts()
            self.save_data()  # Save after adding task
        else:
            messagebox.showwarning("Invalid Input", "Please enter a task!")

    def remove_task(self):
        try:
            selection = self.task_listbox.curselection()
            if selection:
                index = selection[0]
                self.task_listbox.delete(index)
                self.tasks.pop(index)
                self.save_data()  # Save after removing task
            else:
                messagebox.showwarning("No Selection", "Please select a task to remove!")
        except:
            messagebox.showerror("Error", "An error occurred while removing the task!")

    def create_sidebar(self):
        # Private label
        self.private_label = tk.Label(
            self.sidebar_frame, 
            text="Private", 
            font=("Segoe UI", 16, "bold"),
            bg=self.sidebar_color,
            fg=self.text_color,
            anchor="w"
        )
        self.private_label.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Categories frame
        self.categories_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color)
        self.categories_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Initialize categories if not already done
        if not hasattr(self, 'categories'):
            self.categories = [
                {"name": "Home", "icon": "🏠", "color": "#FFFFFF", "count": 0},
                {"name": "Completed", "icon": "☑", "color": "#FFFFFF", "count": 0},
                {"name": "Personal", "icon": "🟣", "color": "#c586ff", "count": 0},
                {"name": "Work", "icon": "🟦", "color": "#5ac8fa", "count": 0},
                {"name": "Diet", "icon": "👍", "color": "#ffcc00", "count": 0}
            ]
        
        # Add category buttons
        for category in self.categories:
            self.create_category_button(category)
        
        # Add "Create new list" button
        create_list_btn = tk.Frame(
            self.sidebar_frame, 
            bg=self.sidebar_color,
            height=35,
            cursor="hand2"
        )
        create_list_btn.pack(fill=tk.X, padx=10, pady=5)
        
        create_list_label = tk.Label(
            create_list_btn,
            text="+ Create new list",
            font=("Segoe UI", 10),
            bg=self.sidebar_color,
            fg=self.text_color,
            cursor="hand2"
        )
        create_list_label.pack(side=tk.LEFT, padx=15)
        create_list_label.bind("<Button-1>", self.create_new_category)

    def create_content_area(self):
        # Header frame
        self.header_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Greeting text
        self.greeting_label = tk.Label(
            self.header_frame,
            text="Hey there! 👋",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.greeting_label.pack(side=tk.LEFT, padx=10)
        
        # Add task button
        self.add_task_btn = tk.Label(
            self.header_frame,
            text="+ Add Task",
            font=("Segoe UI", 11),
            bg=self.primary_color,
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.add_task_btn.pack(side=tk.RIGHT, padx=10)
        self.add_task_btn.bind("<Button-1>", lambda e: self.show_add_task_dialog())
        
        # Tasks container
        self.tasks_container = tk.Frame(self.content_frame, bg=self.bg_color)
        self.tasks_container.pack(fill=tk.BOTH, expand=True, padx=10)

    def create_new_category(self, event=None):
        from tkinter import simpledialog
        name = simpledialog.askstring("New Category", "Enter category name:")
        if name:
            icon = simpledialog.askstring("Category Icon", "Enter an emoji icon (e.g., 🏠, 📚):")
            if not icon:
                icon = "📋"  # Default icon
            
            new_category = {
                "name": name,
                "icon": icon,
                "color": "#FFFFFF",
                "count": 0
            }
            
            self.categories.append(new_category)
            self.create_category_button(new_category)
            self.save_categories()  # Save after creating new category

    def show_add_task_dialog(self):
        # Create a top-level window for the dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        
        # Task title entry
        tk.Label(
            dialog,
            text="Task Title:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(padx=20, pady=(20, 5), anchor="w")
        
        title_entry = tk.Entry(dialog, font=("Segoe UI", 11), width=40)
        title_entry.pack(padx=20, pady=(0, 15))
        
        # Category selection
        tk.Label(
            dialog,
            text="Category:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(padx=20, pady=(0, 5), anchor="w")
        
        category_var = tk.StringVar(value=self.categories[0]["name"])
        category_menu = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=[cat["name"] for cat in self.categories],
            state="readonly",
            font=("Segoe UI", 11)
        )
        category_menu.pack(padx=20, pady=(0, 15))
        
        def add_task():
            title = title_entry.get().strip()
            if title:
                new_task = {
                    "title": title,
                    "category": category_var.get(),
                    "completed": False
                }
                self.tasks.append(new_task)
                self.update_task_list()
                self.update_category_counts()
                self.save_data()  # Save after adding task
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Input", "Please enter a task title!")
        
        # Add button
        tk.Button(
            dialog,
            text="Add Task",
            font=("Segoe UI", 11),
            bg=self.primary_color,
            fg="white",
            command=add_task,
            padx=20,
            pady=5,
            relief="flat",
            cursor="hand2"
        ).pack(pady=20)

    def update_task_list(self):
        """Update the task list display"""
        # Clear existing tasks
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
        
        # Filter tasks based on selected category
        display_tasks = []
        if hasattr(self, 'current_category'):
            if self.current_category["name"] == "Home":
                # Show all tasks for Home category
                display_tasks = self.tasks
            elif self.current_category["name"] == "Completed":
                # Show only completed tasks
                display_tasks = [t for t in self.tasks if t.get("completed", False)]
            else:
                # Show tasks for specific category
                display_tasks = [t for t in self.tasks if t.get("category") == self.current_category["name"]]
        else:
            # If no category selected, show all tasks
            display_tasks = self.tasks
        
        # Add "No tasks" message if list is empty
        if not display_tasks:
            no_tasks_label = tk.Label(
                self.tasks_container,
                text="No tasks to display",
                font=("Segoe UI", 12),
                bg=self.bg_color,
                fg=self.light_text
            )
            no_tasks_label.pack(pady=20)
            return
        
        # Create task items
        for task in display_tasks:
            self.create_task_item(self.tasks_container, task)

    def update_category_counts(self):
        for category in self.categories:
            if category["name"] == "Home":
                category["count"] = len(self.tasks)
            elif category["name"] == "Completed":
                category["count"] = len([t for t in self.tasks if t.get("completed", False)])
            else:
                category["count"] = len([t for t in self.tasks if t.get("category") == category["name"]])
        
        # Refresh sidebar
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        for category in self.categories:
            self.create_category_button(category)

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.show_add_task_dialog())
        self.root.bind("<Control-l>", lambda e: self.create_new_category())
        self.root.bind("<Control-s>", lambda e: self.save_data())

    def load_data(self):
        """Load tasks and categories from files"""
        try:
            # Load tasks
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r') as f:
                    loaded_tasks = json.load(f)
                    # Convert any string tasks to dictionary format
                    self.tasks = []
                    for task in loaded_tasks:
                        if isinstance(task, str):
                            # Convert string task to dictionary format
                            self.tasks.append({
                                "title": task,
                                "category": "Home",
                                "completed": False
                            })
                        else:
                            self.tasks.append(task)
                    print(f"Loaded {len(self.tasks)} tasks from {self.tasks_file}")
            else:
                self.tasks = []
                print("No tasks file found, starting with empty tasks list")
            
            # Load categories
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r') as f:
                    self.categories = json.load(f)
                print(f"Loaded {len(self.categories)} categories from {self.categories_file}")
            else:
                # Default categories if file doesn't exist
                self.categories = [
                    {"name": "Home", "icon": "🏠", "color": "#FFFFFF", "count": 0},
                    {"name": "Completed", "icon": "☑", "color": "#FFFFFF", "count": 0},
                    {"name": "Personal", "icon": "🟣", "color": "#c586ff", "count": 0},
                    {"name": "Work", "icon": "🟦", "color": "#5ac8fa", "count": 0},
                    {"name": "Diet", "icon": "👍", "color": "#ffcc00", "count": 0}
                ]
                print("No categories file found, using default categories")
        except Exception as e:
            messagebox.showerror("Error Loading Data", f"Failed to load data: {str(e)}")
            # Fall back to empty data
            self.tasks = []
            self.categories = [
                {"name": "Home", "icon": "🏠", "color": "#FFFFFF", "count": 0},
                {"name": "Completed", "icon": "☑", "color": "#FFFFFF", "count": 0},
                {"name": "Personal", "icon": "🟣", "color": "#c586ff", "count": 0},
                {"name": "Work", "icon": "🟦", "color": "#5ac8fa", "count": 0},
                {"name": "Diet", "icon": "👍", "color": "#ffcc00", "count": 0}
            ]

    def save_data(self, event=None):
        """Save tasks to file"""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
            print(f"Saved {len(self.tasks)} tasks to {self.tasks_file}")
            return True
        except Exception as e:
            messagebox.showerror("Error Saving Data", f"Failed to save tasks: {str(e)}")
            return False

    def save_categories(self):
        """Save categories to file"""
        try:
            with open(self.categories_file, 'w') as f:
                json.dump(self.categories, f, indent=2)
            print(f"Saved {len(self.categories)} categories to {self.categories_file}")
            return True
        except Exception as e:
            messagebox.showerror("Error Saving Data", f"Failed to save categories: {str(e)}")
            return False

    def on_close(self):
        """Handle application closing"""
        # Save data before closing
        if self.save_data() and self.save_categories():
            self.root.destroy()

    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Task", command=self.show_add_task_dialog, accelerator="Ctrl+N")
        file_menu.add_command(label="Save", command=self.save_data, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export Tasks", command=self.export_tasks)
        file_menu.add_command(label="Import Tasks", command=self.import_tasks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="New Category", command=self.create_new_category, accelerator="Ctrl+L")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear All Tasks", command=self.clear_all_tasks)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="All Tasks", command=lambda: self.select_category({"name": "Home"}))
        view_menu.add_command(label="Completed Tasks", command=lambda: self.select_category({"name": "Completed"}))
        menubar.add_cascade(label="View", menu=view_menu)
        
        self.root.config(menu=menubar)

    def export_tasks(self):
        """Export tasks to a user-specified file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Tasks"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.tasks, f, indent=2)
                messagebox.showinfo("Export Successful", f"Tasks exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export tasks: {str(e)}")

    def import_tasks(self):
        """Import tasks from a user-specified file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Tasks"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_tasks = json.load(f)
                
                if messagebox.askyesno("Import Tasks", "Replace existing tasks or merge with them?\nYes = Replace, No = Merge"):
                    self.tasks = imported_tasks
                else:
                    self.tasks.extend(imported_tasks)
                
                self.update_task_list()
                self.update_category_counts()
                self.save_data()
                messagebox.showinfo("Import Successful", f"Successfully imported tasks from {file_path}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import tasks: {str(e)}")

    def select_category(self, category):
        """Handle category selection"""
        self.current_category = category
        self.update_task_list()

    def clear_all_tasks(self):
        """Clear all tasks after confirmation"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all tasks? This action cannot be undone."):
            self.tasks = []
            self.update_task_list()
            self.update_category_counts()
            self.save_data()  # Save after clearing tasks
            messagebox.showinfo("Tasks Cleared", "All tasks have been cleared and changes saved.")

    def toggle_task_completion(self, task):
        """Toggle task completion status"""
        task["completed"] = not task.get("completed", False)
        self.update_task_list()
        self.update_category_counts()
        self.save_data()  # Save after toggling completion

    def delete_task(self, task):
        """Delete a task"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            self.tasks.remove(task)
            self.update_task_list()
            self.update_category_counts()
            self.save_data()  # Save after deleting task

    def view_task_details(self, task):
        """View and edit task details"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Task Details")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        
        # Task title entry
        tk.Label(
            dialog,
            text="Task Title:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(padx=20, pady=(20, 5), anchor="w")
        
        title_var = tk.StringVar(value=task.get("title", ""))
        title_entry = tk.Entry(dialog, font=("Segoe UI", 11), width=40, textvariable=title_var)
        title_entry.pack(padx=20, pady=(0, 15))
        
        # Category selection
        tk.Label(
            dialog,
            text="Category:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(padx=20, pady=(0, 5), anchor="w")
        
        category_var = tk.StringVar(value=task.get("category", self.categories[0]["name"]))
        category_menu = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=[cat["name"] for cat in self.categories],
            state="readonly",
            font=("Segoe UI", 11)
        )
        category_menu.pack(padx=20, pady=(0, 15))
        
        # Completed checkbox
        completed_var = tk.BooleanVar(value=task.get("completed", False))
        completed_cb = ttk.Checkbutton(
            dialog,
            text="Completed",
            variable=completed_var,
            style="Custom.TCheckbutton"
        )
        completed_cb.pack(padx=20, pady=(0, 15))
        
        def save_changes():
            task["title"] = title_var.get()
            task["category"] = category_var.get()
            task["completed"] = completed_var.get()
            self.update_task_list()
            self.update_category_counts()
            self.save_data()  # Save after updating task
            dialog.destroy()
        
        # Save button
        tk.Button(
            dialog,
            text="Save Changes",
            font=("Segoe UI", 11),
            bg=self.primary_color,
            fg="white",
            command=save_changes,
            padx=20,
            pady=5,
            relief="flat",
            cursor="hand2"
        ).pack(pady=20)

    def update_greeting(self):
        """Update greeting based on time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Good morning! 🌞"
        elif 12 <= hour < 18:
            greeting = "Good afternoon! 🌤️"
        else:
            greeting = "Good evening! 🌙"
            
        self.greeting_label.configure(text=greeting)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configure custom styles
    style = ttk.Style()
    style.configure("Custom.TCheckbutton", background="#f0f2f5", foreground="#202124")
    
    app = AdvancedTodoApp(root)
    root.mainloop()



