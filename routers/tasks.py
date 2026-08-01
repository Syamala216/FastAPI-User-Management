from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.user import User
from models.task import Task
import schemas
from database import get_db
from oauth2 import get_current_user
from exceptions import database_exception

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ---------------- CREATE TASK ---------------- #

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_task = Task(
            title=task.title,
            description=task.description,
            completed=task.completed,
            owner_id=current_user.id
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# ---------------- GET ALL TASKS ---------------- #

@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        tasks = db.query(Task).filter(
            Task.owner_id == current_user.id
        ).all()

        return tasks

    except SQLAlchemyError:
        database_exception()


# ---------------- GET TASK BY ID ---------------- #

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.owner_id == current_user.id
        ).first()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task

    except SQLAlchemyError:
        database_exception()


# ---------------- UPDATE TASK ---------------- #

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    updated_task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.owner_id == current_user.id
        ).first()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        task.title = updated_task.title
        task.description = updated_task.description
        task.completed = updated_task.completed

        db.commit()
        db.refresh(task)

        return task

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# ---------------- DELETE TASK ---------------- #

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.owner_id == current_user.id
        ).first()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        db.delete(task)
        db.commit()

        return {
            "message": "Task deleted successfully"
        }

    except SQLAlchemyError:
        db.rollback()
        database_exception()