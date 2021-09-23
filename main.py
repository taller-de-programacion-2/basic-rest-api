import uvicorn
from fastapi import FastAPI

app = FastAPI()

users = []

@app.get('/users')
async def get_users():
    return users


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
