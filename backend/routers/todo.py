from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from database.config import get_db
from database.models import Todo, User
from backend.schemas import TodoCreate, TodoResponse
from backend.routers.auth import get_current_user

router = APIRouter(tags=["Todo"])

@router.get("/todos", response_model=List[TodoResponse])
def get_todos(
    completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Todo).filter(Todo.owner_id == user.id)
    if completed is not None:
        query = query.filter(Todo.completed == completed)
    return query.all()

@router.post("/todos", status_code=201, response_model=TodoResponse)
def create_todo(
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_todo = Todo(
        id=uuid4(),
        title=todo_data.title,
        description=todo_data.description,
        due_date=todo_data.due_date,
        completed=todo_data.completed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        owner_id=user.id,
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@router.get("/todos/{id}", response_model=TodoResponse)
def get_todo(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/todos/{id}", response_model=TodoResponse)
def update_todo(
    id: str,
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.title = todo_data.title
    todo.description = todo_data.description
    todo.due_date = todo_data.due_date
    todo.completed = todo_data.completed
    todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    return todo

@router.patch("/todos/{id}", response_model=TodoResponse)
def patch_todo(
    id: str,
    completed: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if completed is not None:
        todo.completed = completed
    todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    return todo

@router.delete("/todos/{id}")
def delete_todo(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"status": "deleted"}