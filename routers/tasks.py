from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from logging_config import info_logger

from models.user import User
from models.task import Task
import schemas
from database import get_db
from oauth2 import get_current_user
from exceptions import database_exception


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# CREATE TASK
@router.post(
    "/",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: schemas.TaskCreate,
    db: DbSession,
    current_user: CurrentUser
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

        info_logger.info(
            f"User ID: {current_user.id} - "
            f"Created task - "
            f"Task ID: {new_task.id}"
        )

        return new_task

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# GET ALL TASKS
@router.get(
    "/",
    response_model=List[schemas.TaskResponse]
)
def get_tasks(
    db: DbSession,
    current_user: CurrentUser
):
    try:
        tasks = db.query(Task).filter(
            Task.owner_id == current_user.id
        ).all()

        return tasks

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# GET TASK BY ID
@router.get(
    "/{task_id}",
    response_model=schemas.TaskResponse
)
def get_task(
    task_id: int,
    db: DbSession,
    current_user: CurrentUser
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

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# UPDATE TASK
@router.put(
    "/{task_id}",
    response_model=schemas.TaskResponse
)
def update_task(
    task_id: int,
    updated_task: schemas.TaskCreate,
    db: DbSession,
    current_user: CurrentUser
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

        info_logger.info(
            f"User ID: {current_user.id} - "
            f"Updated task - "
            f"Task ID: {task.id}"
        )

        return task

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# DELETE TASK
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK
)
def delete_task(
    task_id: int,
    db: DbSession,
    current_user: CurrentUser
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

        info_logger.info(
            f"User ID: {current_user.id} - "
            f"Deleted task - "
            f"Task ID: {task.id}"
        )

        return {
            "message": "Task deleted successfully"
        }

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)