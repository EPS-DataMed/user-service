from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class User(BaseModel):
    name: str
    email: str
    password: str

try:
    conn = psycopg2.connect(host="localhost", database="datamed", 
                            user="postgres", password="123", 
                            cursor_factory = RealDictCursor)
    cursor = conn.cursor()
    print("Connected to the database")
except Exception as error:
    print("Error connecting to the database")
    print("Error: ", error)
    time.sleep(5)

# Querys
@app.get("/users")
def get_users():
    cursor.execute("""SELECT * FROM users""")
    users = cursor.fetchall()
    return {"data": users}

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(users: User):
    cursor.execute("""INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING *""", 
                    (users.name, users.email, users.password))
    new_user = cursor.fetchone()
    conn.commit()
    return {"data": new_user}

@app.get("/users/{id}")
def get_user(id: int):
    cursor.execute("""SELECT * FROM users WHERE id = %s""", (id,))
    user = cursor.fetchone()

    if user == None:
        raise HTTPException(status_code=404, 
                            detail=f"User with id: {id} does not exist")
    
    return {"data": user}

@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int):
    cursor.execute("""DELETE FROM users WHERE id = %s RETURNING *""", (id,))
    deleted_user = cursor.fetchone()
    conn.commit()

    if deleted_user == None:
        raise HTTPException(status_code=404, 
                            detail=f"Post with id: {id} does not exist")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/users/{id}")
def update_user(id: int, user: User):
    cursor.execute("""UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s RETURNING *""", 
                    (user.name, user.email, user.password, id))
    updated_user = cursor.fetchone()
    conn.commit()

    if updated_user == None:
        raise HTTPException(status_code=404, 
                            detail=f"Post with id: {id} does not exist")
    
    return {"data": updated_user}