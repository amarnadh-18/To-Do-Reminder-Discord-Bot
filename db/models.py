from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class Task:
    def __init__(self, user_id: int, title: str, description: str = "", 
                 due_date: Optional[datetime] = None, priority: str = "medium",
                 completed: bool = False, created_at: Optional[datetime] = None, _id: Optional[str] = None):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.completed = completed
        self.created_at = created_at or datetime.utcnow()
        self._id = _id
    
    def to_dict(self):
        """Convert task to dictionary for MongoDB storage"""
        return {
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create task from dictionary"""
        return cls(
            user_id=data["user_id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "medium"),
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )

class Reminder:
    def __init__(self, user_id: int, task_id: str, reminder_time: datetime,
                 message: str, sent: bool = False, created_at: Optional[datetime] = None, _id: Optional[str] = None):
        self.user_id = user_id
        self.task_id = task_id
        self.reminder_time = reminder_time
        self.message = message
        self.sent = sent
        self.created_at = created_at or datetime.utcnow()
        self._id = _id
    
    def to_dict(self):
        """Convert reminder to dictionary for MongoDB storage"""
        return {
            "user_id": self.user_id,
            "task_id": self.task_id,
            "reminder_time": self.reminder_time,
            "message": self.message,
            "sent": self.sent,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create reminder from dictionary"""
        return cls(
            user_id=data["user_id"],
            task_id=data["task_id"],
            reminder_time=data["reminder_time"],
            message=data["message"],
            sent=data.get("sent", False),
            created_at=data.get("created_at"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )

class TaskManager:
    def __init__(self, db):
        self.db = db
        self.tasks_collection = db.get_collection("tasks")
        self.reminders_collection = db.get_collection("reminders")
    
    def create_task(self, task: Task) -> str:
        """Create a new task and return its ID"""
        task_dict = task.to_dict()
        result = self.tasks_collection.insert_one(task_dict)
        return str(result.inserted_id)
    
    def get_user_tasks(self, user_id: int, completed: Optional[bool] = None) -> List[Task]:
        """Get all tasks for a user, optionally filtered by completion status"""
        query = {"user_id": user_id}
        if completed is not None:
            query["completed"] = completed
        
        tasks = self.tasks_collection.find(query).sort("created_at", -1)
        return [Task.from_dict(task) for task in tasks]
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID"""
        try:
            task_data = self.tasks_collection.find_one({"_id": ObjectId(task_id)})
            if task_data:
                return Task.from_dict(task_data)
            return None
        except:
            return None
    
    def update_task(self, task_id: str, updates: dict) -> bool:
        """Update a task"""
        try:
            result = self.tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task and its associated reminders"""
        try:
            # Delete the task
            task_result = self.tasks_collection.delete_one({"_id": ObjectId(task_id)})
            
            # Delete associated reminders
            self.reminders_collection.delete_many({"task_id": task_id})
            
            return task_result.deleted_count > 0
        except:
            return False
    
    def create_reminder(self, reminder: Reminder) -> str:
        """Create a new reminder and return its ID"""
        reminder_dict = reminder.to_dict()
        result = self.reminders_collection.insert_one(reminder_dict)
        return str(result.inserted_id)
    
    def get_pending_reminders(self, current_time: datetime) -> List[Reminder]:
        """Get all pending reminders that should be sent"""
        reminders = self.reminders_collection.find({
            "reminder_time": {"$lte": current_time},
            "sent": False
        })
        return [Reminder.from_dict(reminder) for reminder in reminders]
    
    def mark_reminder_sent(self, reminder_id: str) -> bool:
        """Mark a reminder as sent"""
        try:
            result = self.reminders_collection.update_one(
                {"_id": ObjectId(reminder_id)},
                {"$set": {"sent": True}}
            )
            return result.modified_count > 0
        except:
            return False
