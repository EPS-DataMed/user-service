from fastapi import APIRouter, HTTPException, status, Response
from typing import List
from ..models.user import UserCreate, UserResponse
from ..database import get_cursor, get_conn

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=List[UserResponse])
def get_users():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate):
    cursor = get_cursor()
    conn = get_conn()
    cursor.execute(
        """INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id, name, email, password""",
        (user.name, user.email, user.password)
    )
    new_user = cursor.fetchone()
    conn.commit()
    return new_user

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int):
    cursor = get_cursor()
    cursor.execute("SELECT id, name, email, password FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist"
        )
    
    return user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int):
    cursor = get_cursor()
    conn = get_conn()
    cursor.execute("DELETE FROM users WHERE id = %s RETURNING id", (id,))
    deleted_user = cursor.fetchone()
    conn.commit()
    
    if deleted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user: UserCreate):
    cursor = get_cursor()
    conn = get_conn()
    cursor.execute(
        """UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s RETURNING id, name, email, password""",
        (user.name, user.email, user.password, id)
    )
    updated_user = cursor.fetchone()
    conn.commit()
    
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist"
        )
    
    return updated_user
