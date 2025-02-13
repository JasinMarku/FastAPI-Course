from fastapi import Depends, HTTPException, Path, APIRouter, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="ToDoApp/templates")

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Give us a database session, and the current users information
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# This model makes sure the data for a to-do item is in the right format
class TodoRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse("/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {"request" : request, "todos" : todos, "user": user})
    except:
        return redirect_to_login()

@router.get('add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()

@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

    except:
        return redirect_to_login()

### Endpoints
# Function checks that a to-do/user exists,and belongs to the user
# If not, it stops the request by raising an error
def get_todo_for_user(db: Session, todo_id: int, user: dict):
    if user is None: # if user does not exist
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Look for the to-do in the database that belongs to this user
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get('id'))
        .first()
    )

    if todo_model is None:  # if to-do item does not exist message
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo_model


# Read/get all todos from for the current user
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed...")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


# Get a single to-do by its ID
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed...")
    # find the to-do that matches the id and belongs to the user
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")



# create a new to do for the user
@router.post("/todo", status_code= status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed...")
    # Create a new to-do using the data from the request, and mark it with the users id
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()



# Update an existing to-do for the current user
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    # Check that the to-do exists and belongs to the user
    todo_model = get_todo_for_user(db, todo_id, user)

    # Change the to-do with the new data
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()



# Delete a to-do for the current user
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Find and delete the todo in a single query
    todo = db.query(Todos).filter(
        Todos.id == todo_id,
        Todos.owner_id == user.get('id')
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return None




