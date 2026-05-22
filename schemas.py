from pydantic import BaseModel, ConfigDict
from typing import List as TypedList, Optional, Literal

# Status restriction to 'open' or 'closed'
TaskStatus = Literal["open", "closed"]

# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = "open"
    list_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    list_id: Optional[int] = None

class TaskShort(BaseModel):
    id: int
    title: str
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)

# --- List Schemas ---
class ListBase(BaseModel):
    name: str
    description: Optional[str] = None

class ListCreate(ListBase):
    pass

class ListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# --- Detailed Response Schemas to prevent infinite recursion ---
class TaskResponse(TaskBase):
    id: int
    links: TypedList[TaskShort] = []

    model_config = ConfigDict(from_attributes=True)

class ListResponse(ListBase):
    id: int
    name: str
    description: Optional[str] = None
    tasks: TypedList[TaskShort] = []

    model_config = ConfigDict(from_attributes=True)
