#!/usr/bin/env python3
import argparse
import sys
import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"

def get_client(base_url):
    return httpx.Client(base_url=base_url, timeout=10.0)

def print_table(headers, rows):
    """Utility to print a beautiful, clean CLI table."""
    if not rows:
        print("No data available.")
        return
        
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
            
    # Print header separator
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(sep)
    
    # Print headers
    header_str = "|" + "|".join(f" {str(headers[idx]).ljust(widths[idx])} " for idx in range(len(headers))) + "|"
    print(header_str)
    print(sep)
    
    # Print rows
    for row in rows:
        row_str = "|" + "|".join(f" {str(row[idx]).ljust(widths[idx])} " for idx in range(len(row))) + "|"
        print(row_str)
        
    print(sep)

def format_task(task):
    links_str = ", ".join(str(link["id"]) for link in task.get("links", [])) or "None"
    return [
        task.get("id"),
        task.get("title"),
        task.get("status"),
        task.get("list_id") or "None",
        links_str,
        task.get("description") or ""
    ]

def format_list(lst):
    tasks_count = len(lst.get("tasks", []))
    return [
        lst.get("id"),
        lst.get("name"),
        tasks_count,
        lst.get("description") or ""
    ]


# --- Task Command Handlers ---

def handle_task_list(args):
    client = get_client(args.url)
    params = {}
    if args.status:
        params["status"] = args.status
    if args.list_id is not None:
        params["list_id"] = args.list_id
        
    try:
        response = client.get("/tasks", params=params)
        response.raise_for_status()
        tasks = response.json()
        
        headers = ["ID", "Title", "Status", "List ID", "Linked Task IDs", "Description"]
        rows = [format_task(t) for t in tasks]
        print(f"\n--- Tasks (Count: {len(tasks)}) ---")
        print_table(headers, rows)
    except httpx.HTTPError as e:
        print(f"Error fetching tasks: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def handle_task_get(args):
    client = get_client(args.url)
    try:
        response = client.get(f"/tasks/{args.id}")
        response.raise_for_status()
        task = response.json()
        
        print("\n--- Task Details ---")
        print(f"ID:          {task.get('id')}")
        print(f"Title:       {task.get('title')}")
        print(f"Status:      {task.get('status')}")
        print(f"List ID:     {task.get('list_id') or 'None'}")
        print(f"Description: {task.get('description') or 'None'}")
        
        links = task.get("links", [])
        if links:
            print("Linked Tasks:")
            for l in links:
                print(f"  - [{l.get('id')}] {l.get('title')} ({l.get('status')})")
        else:
            print("Linked Tasks: None")
        print()
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_task_create(args):
    client = get_client(args.url)
    payload = {"title": args.title}
    if args.desc:
        payload["description"] = args.desc
    if args.status:
        payload["status"] = args.status
    if args.list_id is not None:
        payload["list_id"] = args.list_id
        
    try:
        response = client.post("/tasks", json=payload)
        response.raise_for_status()
        task = response.json()
        print(f"Task created successfully (ID: {task['id']})")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            print(f"Server Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def handle_task_update(args):
    client = get_client(args.url)
    payload = {}
    if args.title:
        payload["title"] = args.title
    if args.desc:
        payload["description"] = args.desc
    if args.status:
        payload["status"] = args.status
    if args.list_id is not None:
        # We can pass 0 or a flag to clear it, but let's check if the server supports unassign.
        # To assign, we use assign/list_id. To clear, we can use the unassign route!
        payload["list_id"] = args.list_id
        
    try:
        response = client.put(f"/tasks/{args.id}", json=payload)
        response.raise_for_status()
        task = response.json()
        print(f"Task {args.id} updated successfully.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            print(f"Server Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def handle_task_delete(args):
    client = get_client(args.url)
    try:
        response = client.delete(f"/tasks/{args.id}")
        response.raise_for_status()
        print(f"Task {args.id} deleted successfully.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_task_link(args):
    client = get_client(args.url)
    try:
        response = client.post(f"/tasks/{args.id}/link/{args.other_id}")
        response.raise_for_status()
        print(f"Symmetrically linked task {args.id} and task {args.other_id}.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            print(f"Server Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def handle_task_unlink(args):
    client = get_client(args.url)
    try:
        response = client.post(f"/tasks/{args.id}/unlink/{args.other_id}")
        response.raise_for_status()
        print(f"Symmetrically unlinked task {args.id} and task {args.other_id}.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_task_assign(args):
    client = get_client(args.url)
    try:
        response = client.post(f"/tasks/{args.id}/assign/{args.list_id}")
        response.raise_for_status()
        print(f"Task {args.id} assigned to list {args.list_id}.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            print(f"Server Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def handle_task_unassign(args):
    client = get_client(args.url)
    try:
        response = client.post(f"/tasks/{args.id}/unassign")
        response.raise_for_status()
        print(f"Task {args.id} removed from list.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# --- List Command Handlers ---

def handle_list_list(args):
    client = get_client(args.url)
    try:
        response = client.get("/lists")
        response.raise_for_status()
        lists = response.json()
        
        headers = ["ID", "Name", "Tasks Count", "Description"]
        rows = [format_list(l) for l in lists]
        print(f"\n--- Lists (Count: {len(lists)}) ---")
        print_table(headers, rows)
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_list_get(args):
    client = get_client(args.url)
    try:
        response = client.get(f"/lists/{args.id}")
        response.raise_for_status()
        lst = response.json()
        
        print("\n--- List Details ---")
        print(f"ID:          {lst.get('id')}")
        print(f"Name:        {lst.get('name')}")
        print(f"Description: {lst.get('description') or 'None'}")
        
        tasks = lst.get("tasks", [])
        if tasks:
            print("Assigned Tasks:")
            for t in tasks:
                print(f"  - [{t.get('id')}] {t.get('title')} ({t.get('status')})")
        else:
            print("Assigned Tasks: None")
        print()
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_list_create(args):
    client = get_client(args.url)
    payload = {"name": args.name}
    if args.desc:
        payload["description"] = args.desc
        
    try:
        response = client.post("/lists", json=payload)
        response.raise_for_status()
        lst = response.json()
        print(f"List created successfully (ID: {lst['id']})")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_list_update(args):
    client = get_client(args.url)
    payload = {}
    if args.name:
        payload["name"] = args.name
    if args.desc:
        payload["description"] = args.desc
        
    try:
        response = client.put(f"/lists/{args.id}", json=payload)
        response.raise_for_status()
        print(f"List {args.id} updated successfully.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_list_delete(args):
    client = get_client(args.url)
    try:
        response = client.delete(f"/lists/{args.id}")
        response.raise_for_status()
        print(f"List {args.id} deleted successfully.")
    except httpx.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# --- CLI Parser Design ---

def main():
    parser = argparse.ArgumentParser(
        description="Tasks & Lists CLI - Premium Command Line Client to interact with the CRUD server."
    )
    parser.add_argument(
        "--url", 
        default=DEFAULT_BASE_URL, 
        help=f"Base URL of the running FastAPI server (default: {DEFAULT_BASE_URL})"
    )
    
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)
    
    # ------------------ Tasks Subparser ------------------
    task_parser = subparsers.add_parser("tasks", help="Manage Tasks")
    task_sub = task_parser.add_subparsers(title="Task Actions", dest="action", required=True)
    
    # tasks list
    t_list = task_sub.add_parser("list", help="List all tasks")
    t_list.add_argument("--status", choices=["open", "closed"], help="Filter by task status")
    t_list.add_argument("--list-id", type=int, help="Filter by list ID")
    t_list.set_defaults(func=handle_task_list)
    
    # tasks get
    t_get = task_sub.add_parser("get", help="Get a single task by ID")
    t_get.add_argument("id", type=int, help="ID of the task")
    t_get.set_defaults(func=handle_task_get)
    
    # tasks create
    t_create = task_sub.add_parser("create", help="Create a new task")
    t_create.add_argument("title", help="Title of the task")
    t_create.add_argument("--desc", help="Description of the task")
    t_create.add_argument("--status", choices=["open", "closed"], default="open", help="Status of the task")
    t_create.add_argument("--list-id", type=int, help="List ID to assign this task to")
    t_create.set_defaults(func=handle_task_create)
    
    # tasks update
    t_update = task_sub.add_parser("update", help="Update task fields")
    t_update.add_argument("id", type=int, help="ID of the task to update")
    t_update.add_argument("--title", help="New title")
    t_update.add_argument("--desc", help="New description")
    t_update.add_argument("--status", choices=["open", "closed"], help="New status")
    t_update.add_argument("--list-id", type=int, help="New list ID")
    t_update.set_defaults(func=handle_task_update)
    
    # tasks delete
    t_del = task_sub.add_parser("delete", help="Delete a task by ID")
    t_del.add_argument("id", type=int, help="ID of the task to delete")
    t_del.set_defaults(func=handle_task_delete)
    
    # tasks link
    t_link = task_sub.add_parser("link", help="Symmetrically link task with another task")
    t_link.add_argument("id", type=int, help="Primary task ID")
    t_link.add_argument("other_id", type=int, help="Other task ID to link to")
    t_link.set_defaults(func=handle_task_link)
    
    # tasks unlink
    t_unlink = task_sub.add_parser("unlink", help="Symmetrically unlink task from another task")
    t_unlink.add_argument("id", type=int, help="Primary task ID")
    t_unlink.add_argument("other_id", type=int, help="Other task ID to unlink")
    t_unlink.set_defaults(func=handle_task_unlink)
    
    # tasks assign
    t_assign = task_sub.add_parser("assign", help="Assign task to a list")
    t_assign.add_argument("id", type=int, help="Task ID")
    t_assign.add_argument("list_id", type=int, help="List ID")
    t_assign.set_defaults(func=handle_task_assign)
    
    # tasks unassign
    t_unassign = task_sub.add_parser("unassign", help="Remove task from its list")
    t_unassign.add_argument("id", type=int, help="Task ID")
    t_unassign.set_defaults(func=handle_task_unassign)
    
    
    # ------------------ Lists Subparser ------------------
    list_parser = subparsers.add_parser("lists", help="Manage Lists")
    list_sub = list_parser.add_subparsers(title="List Actions", dest="action", required=True)
    
    # lists list
    l_list = list_sub.add_parser("list", help="List all lists")
    l_list.set_defaults(func=handle_list_list)
    
    # lists get
    l_get = list_sub.add_parser("get", help="Get a single list by ID")
    l_get.add_argument("id", type=int, help="List ID")
    l_get.set_defaults(func=handle_list_get)
    
    # lists create
    l_create = list_sub.add_parser("create", help="Create a new list")
    l_create.add_argument("name", help="Name of the list")
    l_create.add_argument("--desc", help="Description of the list")
    l_create.set_defaults(func=handle_list_create)
    
    # lists update
    l_update = list_sub.add_parser("update", help="Update a list's fields")
    l_update.add_argument("id", type=int, help="ID of the list to update")
    l_update.add_argument("--name", help="New list name")
    l_update.add_argument("--desc", help="New description")
    l_update.set_defaults(func=handle_list_update)
    
    # lists delete
    l_del = list_sub.add_parser("delete", help="Delete a list by ID")
    l_del.add_argument("id", type=int, help="ID of the list to delete")
    l_del.set_defaults(func=handle_list_delete)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
