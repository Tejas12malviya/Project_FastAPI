from fastapi import FastAPI,Depends,HTTPException,Path
from typing_extensions import Annotated
from sqlalchemy.orm import Session
import models
from models import Todo
from database import engine,SessionLocal
from starlette import status
from pydantic import BaseModel,Field

app=FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

class TodoRequest(BaseModel):
    title: str=Field(min_lenght=3)
    description: str=Field(min_length=3,max_length=100)
    priority: int=Field(gt=0,lt=6)
    complete: bool

    model_config={
        "json_schema_extra":{
            "example":{
                "title":"type_work",
                "description":"define_work",
                "priority":5,
                "complete":False

            }
        }
    }

@app.get("/")
def read_all(db: Annotated[Session,Depends(get_db)]):
    return db.query(Todo).all()

@app.get("/read_db/{db_id}",status_code=status.HTTP_200_OK)
def read_by_id(db:db_dependency,db_id:int=Path(gt=0)):
    item =db.query(Todo).filter(Todo.id==db_id).first()
    if item is not None:
        return item
    raise  HTTPException(status_code=404,detail='Todo not found.')

@app.post("/todo")
def create_todo(db:db_dependency, todo_create:TodoRequest):
    todo=Todo(**todo_create.dict())

    db.add(todo)
    db.commit()

@app.put("/todo/{todo_id}")
def update_book(db:db_dependency,todo_id:int,update_todo:TodoRequest):
    todo=db.query(Todo).filter(Todo.id==todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404,details="Todo not found")
    else:
        todo.title=update_todo.title
        todo.description=update_todo.description
        todo.priority=update_todo.priority
        todo.complete=update_todo.complete

        db.add(todo)
        db.commit()

@app.delete("/todo/{todo_id}")
def delete_todo(db:db_dependency,todo_id:int=Path(gt=0)):
    del_item = db.query(Todo).filter(Todo.id==todo_id).first()
    if del_item is None:
        raise HTTPException(status_code=404,details="Not present")
    else:
        db.query(Todo).filter(Todo.id==todo_id).delete()

        db.commit()