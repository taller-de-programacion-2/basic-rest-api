import uuid
import requests
import uvicorn
from fastapi import FastAPI, status
from pydantic import EmailStr
from pydantic.main import BaseModel
from typing import List, Optional
from starlette.responses import JSONResponse

app = FastAPI()


class UserRequest(BaseModel):
    username: str
    email: Optional[EmailStr]

class UpdateUserRequest(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[EmailStr]
    random: Optional[str]

    class Config:
        orm_mode = True


class User:
    def __init__(self, id: str, username: str, email: str = None, random: str = None):
        self.id = id
        self.username = username
        self.email = email
        self.random = random


users = {}

def validate_username(username, users):
    for user in users.values():
        if user.username == username:
            return False
    return True


def get_random():
    params = {'q': str(uuid.uuid4())}
    try:
        response = requests.get('http://localhost:5001/random', params=params)
        if response.status_code != 200:
            return None
    except requests.exceptions.ConnectionError as e:
        return None
    return response.json()


def create_user(username: str, email: str):
    user_id = str(uuid.uuid4())
    random = get_random()
    new_user = User(id=user_id, username=username, email=email, random=random)
    users[user_id] = new_user
    return new_user

@app.get('/users',response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(email_filter: Optional[str] = None):
    users_filtered = []
    for user_id, user in users.items():
        if email_filter:
            if email_filter in user.email:
                users_filtered.append(user)
        else:
            users_filtered.append(user)
    return users_filtered


@app.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_users(user_request: UserRequest):
    if not validate_username(user_request.username, users):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f'User {user_request.username} already exists',)
    return create_user(user_request.username, user_request.email)


@app.get('/users/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    if user_id not in users:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    return users[user_id]


@app.patch('/users/{user_id}', response_model=UserResponse, status_code=status.HTTP_202_ACCEPTED)
async def update_users(user_id: str, update_user_request: UpdateUserRequest):
    if user_id not in users:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    user = users[user_id]
    user.email = update_user_request.email
    users[user_id] = user
    return user


@app.delete('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED)
async def delete_users(user_id: str):
    if user_id not in users:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    users.pop(user_id)
    return


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
