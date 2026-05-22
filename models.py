from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Association table for task-to-task links (many-to-many, self-referential)
task_links = Table(
    "task_links",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("linked_task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
)

class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # If list is deleted, related tasks' list_id is set to NULL (handled by ForeignKey constraint and relationship configuration)
    tasks = relationship("Task", back_populates="list")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="open", nullable=False)  # Constraint to 'open' or 'closed' will be validated at application level
    list_id = Column(Integer, ForeignKey("lists.id", ondelete="SET NULL"), nullable=True)

    list = relationship("List", back_populates="tasks")

    # Self-referential relationship to represent linked tasks
    # We will manage the links symmetrically in our CRUD layer to ensure consistency
    links = relationship(
        "Task",
        secondary=task_links,
        primaryjoin="Task.id==task_links.c.task_id",
        secondaryjoin="Task.id==task_links.c.linked_task_id",
    )
