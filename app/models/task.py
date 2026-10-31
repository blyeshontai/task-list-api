from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..db import db
from datetime import datetime
from typing import Optional, TYPE_CHECKING

'''Wave 6 connect goals and tasks'''
if TYPE_CHECKING:
    from .goal import Goal

'''Wave1 Create Task Model'''
class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]]                                    #Wave 3, is_complete returns true or flase

    #Wave 6
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")


    #Task object -> Python dict
    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }
        if self.goal_id:
            task_dict["goal_id"] = self.goal_id

        return task_dict


    #Python dict <- from_dict() <- Task object
    @classmethod
    def from_dict(cls, task_data):
        return cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at=cls.parse_completed_at(task_data.get("completed_at")),
            goal_id=task_data.get("goal_id")
        )

    @staticmethod
    def parse_completed_at(value):
        if value is None:
            return None
        return datetime.fromisoformat(value)
