from fastapi import FastAPI

from app.routes import posts  
from app.routes import auth    

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router) 
@app.get("/")
def root():
    return {"message": "API is running"}


