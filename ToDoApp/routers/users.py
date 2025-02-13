from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from fastapi import Form
from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user
from .auth import bcrypt_context

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class ChangePasswordRequest(BaseModel):
    old_password: str = Form(..., title="Current Password", description="Enter your current password")
    new_password: str = Form(..., title="New Password", description="Enter your new password")


class UpdatePhoneNumber(BaseModel):
    phone_number: str

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
        user: user_dependency,
        db: db_dependency,
        old_password: str = Form(..., title="Current Password", description="Enter your current password"),
        new_password: str = Form(..., title="New Password", description="Enter your new password"),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Old Password")

    hashed_new_password = bcrypt_context.hash(new_password)
    user_model.hashed_password = hashed_new_password

    db.add(user_model)
    db.commit()


@router.put("/update-phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_phone_number(user: user_dependency, db: db_dependency, phone_request: UpdatePhoneNumber):
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_model.phone_number = phone_request.phone_number

    db.add(user_model)
    db.commit()
