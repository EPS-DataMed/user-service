from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (user_Pydantic, user_PydanticIn, User)
app = FastAPI()

@app.get("/")
def index():
    return {"message": "go to /docs for te API documentation."}

@app.post('/user')
async def add_user(user_info: user_PydanticIn):
    user_obj = await user.create(**user_info.dict(exclude_unset=True))
    response = await user_Pydantic.from_tortoise_orm(user_obj)
    return {"status":"Ok", "data":response}

@app.get('/user')
async def get_all_users():
    response = await user_Pydantic.from_queryset(user.all())
    return {"status":"Ok", "data":response}

@app.get('/user/{id}')
async def get_specific_user(id_user: int):
    response = await user_Pydantic.from_queryset_single(user.get(id=id_user))
    return {"status":"Ok", "data":response}

@app.put('/user/{id}')
async def update_user(id_user: int, update_info: user_PydanticIn):
    user = await user.get(id=id_user)
    update_info = update_info.dict(exclude_unset=True)
    user.name = update_info['name']
    user.email = update_info['email']
    user.phone = update_info['phone']
    user.company = update_info['company']
    await user.save()
    response = await user_Pydantic.from_tortoise_orm(user)
    return {"status":"Ok", "data":response}

@app.delete('/user/{id}')
async def delete_user(id_user: int):
    user = await user.get(id=id_user)
    await user.delete()
    return {"status":"Ok", "data":"user deleted successfully"}

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)