import uvicorn

from fastapi import FastAPI
from typing import Optional


app = FastAPI()


@app.get('/random')
async def random(q: Optional[str] = None):
    return q

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5001)
