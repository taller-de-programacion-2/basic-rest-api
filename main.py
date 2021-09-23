import uuid

import uvicorn
from fastapi import FastAPI, status
from pydantic.main import BaseModel
from typing import List
from starlette.responses import JSONResponse

app = FastAPI()


class UserRequest(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: str
    username: str

    class Config:
        orm_mode = True


class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username


users = {}


@app.get('/users',response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users():
    return [v for k, v in users.items()]


def validate_username(username, users):
    for user in users.values():
        if user.username == username:
            return False
    return True


@app.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_users(user_request: UserRequest):
    if not validate_username(user_request.username, users):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f'User {user_request.username} already exists',)
    user_id = str(uuid.uuid4())
    new_user = User(id=user_id, username=user_request.username)
    users[user_id] = new_user
    return new_user


@app.get('/users/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_users(user_id: str):
    if user_id not in users:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    return users[user_id]


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
