from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Initialize FastAPI app
app = FastAPI()

# Define a data model for request body
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# Define a basic root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI backend!"}

# Define a get endpoint with a path parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "query": q}

# Define a post endpoint to create an item
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    item_dict["price_with_tax"] = item.price + (item.tax if item.tax else 0)
    return item_dict
