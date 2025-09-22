from typing import List, Optional
from enum import IntEnum
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

all_todos = [
    {"id": 1, "task": "Sports", "task_description": "Play football"},
    {"id": 2, "task": "Study", "task_description": "Read books"},
    {"id": 3, "task": "Shopping", "task_description": "Buy groceries"},
    {"id": 4, "task": "Work", "task_description": "Complete project"},
    {"id": 5, "task": "Exercise", "task_description": "Go for a run"},
]

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in all_todos:
        if todo['id'] == todo_id:
            return {'result': todo}


@app.get("/todos")
def get_todos(first_n: int = None):
    if first_n:
        return all_todos[:first_n]
    else:
        return all_todos


@app.post("/todos")
def create_todo(todo: dict):
    new_todo_id = max(todos['id'] for todos in all_todos) + 1

    new_todo = {
        "id": new_todo_id,
        "task": todo["task"],
        "task_description": todo["task_description"],
    }

    all_todos.append(new_todo)
    return new_todo


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: dict):
    for todo in all_todos:
        if todo['id'] == todo_id:
            todo["task"] = updated_todo["task"]
            todo["task_description"] = updated_todo["task_description"]
            return todo
    return "Error, not found"


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(all_todos):
        if todo["id"] == todo_id:
            deleted_todo = all_todos.pop(index)
            return deleted_todo
    return "Error, not found"
