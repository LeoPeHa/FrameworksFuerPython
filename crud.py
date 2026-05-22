from sqlalchemy.orm import Session
from typing import Optional
import models
import schemas

# --- List CRUD Operations ---

def get_lists(db: Session):
    return db.query(models.List).all()

def get_list(db: Session, list_id: int):
    return db.query(models.List).filter(models.List.id == list_id).first()

def create_list(db: Session, list_data: schemas.ListCreate):
    db_list = models.List(
        name=list_data.name,
        description=list_data.description
    )
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def update_list(db: Session, list_id: int, list_update: schemas.ListUpdate):
    db_list = get_list(db, list_id)
    if not db_list:
        return None
    
    update_data = list_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_list, key, value)
    
    db.commit()
    db.refresh(db_list)
    return db_list

def delete_list(db: Session, list_id: int):
    db_list = get_list(db, list_id)
    if not db_list:
        return None
    db.delete(db_list)
    db.commit()
    return db_list


# --- Task CRUD Operations ---

def get_tasks(db: Session, status: Optional[str] = None, list_id: Optional[int] = None):
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    if list_id is not None:
        query = query.filter(models.Task.list_id == list_id)
    return query.all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task_data: schemas.TaskCreate):
    # Verify list exists if list_id is provided
    if task_data.list_id is not None:
        db_list = get_list(db, task_data.list_id)
        if not db_list:
            raise ValueError(f"List with ID {task_data.list_id} does not exist.")
            
    db_task = models.Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        list_id=task_data.list_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Verify list exists if list_id is being updated
    if "list_id" in update_data and update_data["list_id"] is not None:
        db_list = get_list(db, update_data["list_id"])
        if not db_list:
            raise ValueError(f"List with ID {update_data['list_id']} does not exist.")
            
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    db.delete(db_task)
    db.commit()
    return db_task


# --- Task Link & Assign Operations ---

def link_tasks(db: Session, task_id: int, other_id: int):
    if task_id == other_id:
        raise ValueError("A task cannot be linked to itself.")
        
    task = get_task(db, task_id)
    other = get_task(db, other_id)
    
    if not task or not other:
        return None
        
    # Append to each other for symmetric linking
    if other not in task.links:
        task.links.append(other)
    if task not in other.links:
        other.links.append(task)
        
    db.commit()
    db.refresh(task)
    db.refresh(other)
    return task

def assign_task_to_list(db: Session, task_id: int, list_id: int):
    task = get_task(db, task_id)
    if not task:
        return None
        
    lst = get_list(db, list_id)
    if not lst:
        raise ValueError(f"List with ID {list_id} does not exist.")
        
    task.list_id = list_id
    db.commit()
    db.refresh(task)
    return task

def unlink_tasks(db: Session, task_id: int, other_id: int):
    task = get_task(db, task_id)
    other = get_task(db, other_id)
    
    if not task or not other:
        return None
        
    # Remove from each other for symmetric unlinking
    if other in task.links:
        task.links.remove(other)
    if task in other.links:
        other.links.remove(task)
        
    db.commit()
    db.refresh(task)
    db.refresh(other)
    return task

def unassign_task_from_list(db: Session, task_id: int):
    task = get_task(db, task_id)
    if not task:
        return None
        
    task.list_id = None
    db.commit()
    db.refresh(task)
    return task

