#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import httpx
import sys

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
API_KEY = "dev-premium-api-key-2026"

class CRUDClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=base_url,
            headers={"X-API-Key": api_key},
            timeout=10.0
        )

    def request(self, method, url, **kwargs):
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            detail = e.response.json().get("detail", e.response.text)
            messagebox.showerror("Server Error", f"Server responded with error:\n{detail}")
            raise e
        except httpx.RequestError as e:
            messagebox.showerror("Connection Error", f"Could not connect to the server at {self.base_url}.\nIs the server running?")
            raise e

class TaskDialog(simpledialog.Dialog):
    def __init__(self, parent, title, task_data=None, list_choices=None):
        self.task_data = task_data or {}
        self.list_choices = list_choices or []  # List of dicts: {"id": int, "name": str}
        super().__init__(parent, title)

    def body(self, master):
        master.configure(background="#1a1a1e")
        
        # Style label
        lbl_style = {"bg": "#1a1a1e", "fg": "#ffffff", "font": ("Arial", 10, "bold")}
        entry_style = {"bg": "#2a2a30", "fg": "#ffffff", "insertbackground": "#ffffff", "relief": "flat", "bd": 5}
        
        tk.Label(master, text="Title:", **lbl_style).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.ent_title = tk.Entry(master, width=35, **entry_style)
        self.ent_title.insert(0, self.task_data.get("title", ""))
        self.ent_title.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(master, text="Description:", **lbl_style).grid(row=1, column=0, sticky="nw", pady=5, padx=5)
        self.txt_desc = tk.Text(master, width=35, height=5, bg="#2a2a30", fg="#ffffff", insertbackground="#ffffff", relief="flat", bd=5)
        self.txt_desc.insert("1.0", self.task_data.get("description", "") or "")
        self.txt_desc.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(master, text="Status:", **lbl_style).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.var_status = tk.StringVar(value=self.task_data.get("status", "open"))
        self.cb_status = ttk.Combobox(master, textvariable=self.var_status, values=["open", "closed"], state="readonly", width=15)
        self.cb_status.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        tk.Label(master, text="List:", **lbl_style).grid(row=3, column=0, sticky="w", pady=5, padx=5)
        
        # Build dropdown values
        self.list_ids = [None] + [l["id"] for l in self.list_choices]
        list_display = ["None"] + [f"[{l['id']}] {l['name']}" for l in self.list_choices]
        
        current_list_id = self.task_data.get("list_id")
        default_index = 0
        if current_list_id in self.list_ids:
            default_index = self.list_ids.index(current_list_id)

        self.cb_list = ttk.Combobox(master, values=list_display, state="readonly", width=25)
        self.cb_list.current(default_index)
        self.cb_list.grid(row=3, column=1, sticky="w", pady=5, padx=5)

        return self.ent_title  # initial focus

    def apply(self):
        self.result = {
            "title": self.ent_title.get().strip(),
            "description": self.txt_desc.get("1.0", "end").strip() or None,
            "status": self.var_status.get(),
            "list_id": self.list_ids[self.cb_list.current()]
        }

class ListDialog(simpledialog.Dialog):
    def __init__(self, parent, title, list_data=None):
        self.list_data = list_data or {}
        super().__init__(parent, title)

    def body(self, master):
        master.configure(background="#1a1a1e")
        lbl_style = {"bg": "#1a1a1e", "fg": "#ffffff", "font": ("Arial", 10, "bold")}
        entry_style = {"bg": "#2a2a30", "fg": "#ffffff", "insertbackground": "#ffffff", "relief": "flat", "bd": 5}
        
        tk.Label(master, text="Name:", **lbl_style).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.ent_name = tk.Entry(master, width=35, **entry_style)
        self.ent_name.insert(0, self.list_data.get("name", ""))
        self.ent_name.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(master, text="Description:", **lbl_style).grid(row=1, column=0, sticky="nw", pady=5, padx=5)
        self.txt_desc = tk.Text(master, width=35, height=5, bg="#2a2a30", fg="#ffffff", insertbackground="#ffffff", relief="flat", bd=5)
        self.txt_desc.insert("1.0", self.list_data.get("description", "") or "")
        self.txt_desc.grid(row=1, column=1, pady=5, padx=5)

        return self.ent_name

    def apply(self):
        self.result = {
            "name": self.ent_name.get().strip(),
            "description": self.txt_desc.get("1.0", "end").strip() or None
        }

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FastAPI CRUD Manager")
        self.geometry("1100x650")
        self.configure(background="#121214")
        
        # Connect client
        self.api = CRUDClient(DEFAULT_BASE_URL, API_KEY)
        
        # Configure Premium dark styling
        self.setup_styles()
        
        # Build UI layout
        self.build_ui()
        
        # Initial load
        self.refresh_all()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Dark styling variables
        bg_dark = "#121214"
        bg_panel = "#1a1a1e"
        accent = "#6366f1"
        accent_hover = "#4f46e5"
        fg_white = "#ffffff"
        fg_gray = "#a1a1aa"
        
        style.configure(".", background=bg_panel, foreground=fg_white, fieldbackground="#2a2a30")
        style.configure("TFrame", background=bg_dark)
        style.configure("Sidebar.TFrame", background=bg_panel)
        
        # Custom Button styling
        style.configure("Accent.TButton", background=accent, foreground=fg_white, bordercolor="flat", font=("Arial", 10, "bold"), padding=6)
        style.map("Accent.TButton", background=[("active", accent_hover)])

        style.configure("Standard.TButton", background="#3f3f46", foreground=fg_white, font=("Arial", 9), padding=5)
        style.map("Standard.TButton", background=[("active", "#52525b")])

        style.configure("Danger.TButton", background="#ef4444", foreground=fg_white, font=("Arial", 9, "bold"), padding=5)
        style.map("Danger.TButton", background=[("active", "#dc2626")])
        
        # Treeview styling
        style.configure("Treeview", background="#1a1a1e", foreground=fg_white, fieldbackground="#1a1a1e", rowheight=25, font=("Arial", 9))
        style.map("Treeview", background=[("selected", accent)], foreground=[("selected", fg_white)])
        style.configure("Treeview.Heading", background="#2a2a30", foreground=fg_white, font=("Arial", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[("active", "#3f3f46")])

    def build_ui(self):
        # 1. Sidebar - List Management
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", padding=10)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)
        
        lbl_lists = tk.Label(sidebar, text="LISTS", bg="#1a1a1e", fg="#6366f1", font=("Arial", 11, "bold"))
        lbl_lists.pack(anchor="w", pady=(0, 10))
        
        # List Treeview
        self.list_tree = ttk.Treeview(sidebar, columns=("name"), show="tree", height=15)
        self.list_tree.pack(fill="both", expand=True, pady=5)
        self.list_tree.bind("<<TreeviewSelect>>", self.on_list_select)
        
        # Sidebar buttons
        sb_buttons = ttk.Frame(sidebar)
        sb_buttons.pack(fill="x", pady=5)
        
        btn_add_lst = ttk.Button(sb_buttons, text="New List", style="Accent.TButton", command=self.create_list)
        btn_add_lst.pack(side="left", expand=True, fill="x", padx=2)
        
        btn_del_lst = ttk.Button(sb_buttons, text="Delete", style="Danger.TButton", command=self.delete_list)
        btn_del_lst.pack(side="left", expand=True, fill="x", padx=2)

        btn_edit_lst = ttk.Button(sidebar, text="Edit List Details", style="Standard.TButton", command=self.edit_list)
        btn_edit_lst.pack(fill="x", pady=2)

        btn_clear_filter = ttk.Button(sidebar, text="Show All Tasks", style="Standard.TButton", command=self.clear_list_filter)
        btn_clear_filter.pack(fill="x", pady=(10, 0))

        # 2. Main Content Area - Tasks Grid & Operations
        main_area = ttk.Frame(self, padding=10)
        main_area.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Header with filters
        header = ttk.Frame(main_area)
        header.pack(fill="x", pady=(0, 10))

        lbl_tasks = tk.Label(header, text="TASKS", bg="#121214", fg="#ffffff", font=("Arial", 14, "bold"))
        lbl_tasks.pack(side="left")

        # Filters frame
        filters_frame = ttk.Frame(header)
        filters_frame.pack(side="right")
        
        tk.Label(filters_frame, text="Status Filter:", bg="#121214", fg="#a1a1aa").pack(side="left", padx=5)
        self.var_filter_status = tk.StringVar(value="All")
        self.cb_filter_status = ttk.Combobox(filters_frame, textvariable=self.var_filter_status, values=["All", "open", "closed"], state="readonly", width=10)
        self.cb_filter_status.pack(side="left", padx=5)
        self.cb_filter_status.bind("<<ComboboxSelected>>", lambda e: self.load_tasks())

        # Tasks Treeview
        columns = ("id", "title", "status", "list_id", "links")
        self.task_tree = ttk.Treeview(main_area, columns=columns, show="headings", height=12)
        self.task_tree.pack(fill="both", expand=True)

        self.task_tree.heading("id", text="ID")
        self.task_tree.heading("title", text="Title")
        self.task_tree.heading("status", text="Status")
        self.task_tree.heading("list_id", text="List ID")
        self.task_tree.heading("links", text="Linked Task IDs")

        self.task_tree.column("id", width=50, anchor="center")
        self.task_tree.column("title", width=250, anchor="w")
        self.task_tree.column("status", width=100, anchor="center")
        self.task_tree.column("list_id", width=80, anchor="center")
        self.task_tree.column("links", width=120, anchor="w")
        
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.task_tree.bind("<Double-1>", lambda e: self.edit_task())

        # Task Action Buttons
        actions_frame = ttk.Frame(main_area)
        actions_frame.pack(fill="x", pady=10)

        btn_add_tsk = ttk.Button(actions_frame, text="New Task", style="Accent.TButton", command=self.create_task)
        btn_add_tsk.pack(side="left", padx=5)

        btn_edit_tsk = ttk.Button(actions_frame, text="Edit Task", style="Standard.TButton", command=self.edit_task)
        btn_edit_tsk.pack(side="left", padx=5)

        btn_del_tsk = ttk.Button(actions_frame, text="Delete Task", style="Danger.TButton", command=self.delete_task)
        btn_del_tsk.pack(side="left", padx=5)

        btn_refresh = ttk.Button(actions_frame, text="Refresh", style="Standard.TButton", command=self.refresh_all)
        btn_refresh.pack(side="right", padx=5)

        # 3. Details Pane - Selected Task & Link/Assign Actions
        self.details_pane = ttk.LabelFrame(main_area, text="Task Details & Advanced Relations", padding=10)
        self.details_pane.pack(fill="x", pady=(10, 0))
        
        # Details layout
        self.lbl_details_title = tk.Label(self.details_pane, text="Select a task to view details.", bg="#1a1a1e", fg="#ffffff", font=("Arial", 11, "bold"), anchor="w")
        self.lbl_details_title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)

        self.lbl_details_desc = tk.Label(self.details_pane, text="", bg="#1a1a1e", fg="#a1a1aa", anchor="w", justify="left", wraplength=500)
        self.lbl_details_desc.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # Linking controls
        link_frame = ttk.Frame(self.details_pane)
        link_frame.grid(row=2, column=0, sticky="w", pady=10, padx=5)
        
        tk.Label(link_frame, text="Link to Task ID:", bg="#1a1a1e", fg="#ffffff").pack(side="left", padx=2)
        self.ent_link_id = tk.Entry(link_frame, width=6, bg="#2a2a30", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.ent_link_id.pack(side="left", padx=5)

        btn_link = ttk.Button(link_frame, text="Link", style="Standard.TButton", command=self.link_tasks)
        btn_link.pack(side="left", padx=2)

        btn_unlink = ttk.Button(link_frame, text="Unlink", style="Standard.TButton", command=self.unlink_tasks)
        btn_unlink.pack(side="left", padx=2)

        # Assign controls
        assign_frame = ttk.Frame(self.details_pane)
        assign_frame.grid(row=2, column=1, sticky="e", pady=10, padx=5)

        tk.Label(assign_frame, text="Assign to List ID:", bg="#1a1a1e", fg="#ffffff").pack(side="left", padx=2)
        self.ent_list_id = tk.Entry(assign_frame, width=6, bg="#2a2a30", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.ent_list_id.pack(side="left", padx=5)

        btn_assign = ttk.Button(assign_frame, text="Assign", style="Standard.TButton", command=self.assign_task)
        btn_assign.pack(side="left", padx=2)

        btn_unassign = ttk.Button(assign_frame, text="Unassign", style="Standard.TButton", command=self.unassign_task)
        btn_unassign.pack(side="left", padx=2)

    # --- Loading & Selecting Handlers ---

    def refresh_all(self):
        self.load_lists()
        self.load_tasks()
        self.clear_details()

    def load_lists(self):
        try:
            lists = self.api.request("GET", "/lists")
            # Cache lists for dropdown selection
            self.lists_cache = [{"id": l["id"], "name": l["name"]} for l in lists]
            
            # Populate sidebar tree
            self.list_tree.delete(*self.list_tree.get_children())
            for l in lists:
                desc_suffix = f" ({len(l.get('tasks', []))} tasks)"
                self.list_tree.insert("", "end", iid=str(l["id"]), text=f" {l['name']}{desc_suffix}")
        except Exception:
            pass

    def load_tasks(self):
        params = {}
        
        # Apply Status filter
        status = self.var_filter_status.get()
        if status != "All":
            params["status"] = status
            
        # Apply List selection filter
        selected_list_ids = self.list_tree.selection()
        if selected_list_ids:
            params["list_id"] = int(selected_list_ids[0])
            
        try:
            tasks = self.api.request("GET", "/tasks", params=params)
            
            # Populate tasks grid
            self.task_tree.delete(*self.task_tree.get_children())
            for t in tasks:
                links_str = ", ".join(str(link["id"]) for link in t.get("links", [])) or "None"
                self.task_tree.insert(
                    "", 
                    "end", 
                    iid=str(t["id"]), 
                    values=(t["id"], t["title"], t["status"], t["list_id"] or "None", links_str)
                )
        except Exception:
            pass

    def on_list_select(self, event):
        self.load_tasks()

    def clear_list_filter(self):
        self.list_tree.selection_remove(self.list_tree.selection())
        self.load_tasks()

    def on_task_select(self, event):
        selected = self.task_tree.selection()
        if not selected:
            self.clear_details()
            return
            
        task_id = int(selected[0])
        try:
            task = self.api.request("GET", f"/tasks/{task_id}")
            self.lbl_details_title.config(text=f"[{task['id']}] {task['title']} ({task['status']})")
            
            desc = task['description'] or "No description provided."
            self.lbl_details_desc.config(text=f"Description: {desc}")
            
            # Pre-fill link/list inputs
            self.ent_link_id.delete(0, tk.END)
            self.ent_list_id.delete(0, tk.END)
            if task.get("list_id"):
                self.ent_list_id.insert(0, str(task["list_id"]))
        except Exception:
            self.clear_details()

    def clear_details(self):
        self.lbl_details_title.config(text="Select a task to view details.")
        self.lbl_details_desc.config(text="")
        self.ent_link_id.delete(0, tk.END)
        self.ent_list_id.delete(0, tk.END)


    # --- Task Event Handlers ---

    def create_task(self):
        dialog = TaskDialog(self, "Create Task", list_choices=self.lists_cache)
        if hasattr(dialog, "result") and dialog.result:
            try:
                self.api.request("POST", "/tasks", json=dialog.result)
                self.refresh_all()
                messagebox.showinfo("Success", "Task created successfully.")
            except Exception:
                pass

    def edit_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a task to edit.")
            return
            
        task_id = int(selected[0])
        try:
            # Fetch full task including description
            task = self.api.request("GET", f"/tasks/{task_id}")
            
            dialog = TaskDialog(self, "Edit Task", task_data=task, list_choices=self.lists_cache)
            if hasattr(dialog, "result") and dialog.result:
                self.api.request("PUT", f"/tasks/{task_id}", json=dialog.result)
                self.refresh_all()
                messagebox.showinfo("Success", "Task updated successfully.")
        except Exception:
            pass

    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a task to delete.")
            return
            
        task_id = int(selected[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task {task_id}?"):
            try:
                self.api.request("DELETE", f"/tasks/{task_id}")
                self.refresh_all()
                messagebox.showinfo("Success", "Task deleted successfully.")
            except Exception:
                pass


    # --- List Event Handlers ---

    def create_list(self):
        dialog = ListDialog(self, "Create List")
        if hasattr(dialog, "result") and dialog.result:
            try:
                self.api.request("POST", "/lists", json=dialog.result)
                self.refresh_all()
                messagebox.showinfo("Success", "List created successfully.")
            except Exception:
                pass

    def edit_list(self):
        selected = self.list_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a list from the sidebar to edit.")
            return
            
        list_id = int(selected[0])
        try:
            lst = self.api.request("GET", f"/lists/{list_id}")
            dialog = ListDialog(self, "Edit List", list_data=lst)
            if hasattr(dialog, "result") and dialog.result:
                self.api.request("PUT", f"/lists/{list_id}", json=dialog.result)
                self.refresh_all()
                messagebox.showinfo("Success", "List updated successfully.")
        except Exception:
            pass

    def delete_list(self):
        selected = self.list_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a list to delete.")
            return
            
        list_id = int(selected[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete list {list_id}? Related tasks will be unassigned but NOT deleted."):
            try:
                self.api.request("DELETE", f"/lists/{list_id}")
                self.refresh_all()
                messagebox.showinfo("Success", "List deleted successfully.")
            except Exception:
                pass


    # --- Task Linking & Assigning Handlers ---

    def link_tasks(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a primary task from the grid.")
            return
            
        task_id = int(selected[0])
        other_str = self.ent_link_id.get().strip()
        if not other_str.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a valid numeric Task ID to link to.")
            return
            
        try:
            self.api.request("POST", f"/tasks/{task_id}/link/{int(other_str)}")
            self.refresh_all()
            messagebox.showinfo("Success", f"Task {task_id} successfully linked to Task {other_str}.")
        except Exception:
            pass

    def unlink_tasks(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a primary task from the grid.")
            return
            
        task_id = int(selected[0])
        other_str = self.ent_link_id.get().strip()
        if not other_str.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a valid numeric Task ID to unlink.")
            return
            
        try:
            self.api.request("POST", f"/tasks/{task_id}/unlink/{int(other_str)}")
            self.refresh_all()
            messagebox.showinfo("Success", f"Task {task_id} successfully unlinked from Task {other_str}.")
        except Exception:
            pass

    def assign_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a task from the grid.")
            return
            
        task_id = int(selected[0])
        list_str = self.ent_list_id.get().strip()
        if not list_str.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a valid numeric List ID.")
            return
            
        try:
            self.api.request("POST", f"/tasks/{task_id}/assign/{int(list_str)}")
            self.refresh_all()
            messagebox.showinfo("Success", f"Task {task_id} successfully assigned to List {list_str}.")
        except Exception:
            pass

    def unassign_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a task from the grid.")
            return
            
        task_id = int(selected[0])
        try:
            self.api.request("POST", f"/tasks/{task_id}/unassign")
            self.refresh_all()
            messagebox.showinfo("Success", f"Task {task_id} successfully removed from its list.")
        except Exception:
            pass

if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()
