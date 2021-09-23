import uuid

import uvicorn
from fastapi import FastAPI
from pydantic.main import BaseModel

app = FastAPI()


class UserRequest(BaseModel):
    username: str


class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username


users = []


@app.get('/users')
async def get_users():
    return users


@app.post('/users')
async def create_users(user_request: UserRequest):
    new_user = User(id=str(uuid.uuid4()), username=user_request.username)
    users.append(new_user)
    return new_user

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
