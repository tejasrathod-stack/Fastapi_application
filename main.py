from audit import router as audit_router
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Sample FastAPI Application",
    description="A comprehensive sample FastAPI application with CRUD operations",
    version="1.0.0"
)

app.include_router(audit_router)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

# In-memory database (for demonstration)
items_db: List[Item] = []
users_db: List[User] = []
item_id_counter = 1
user_id_counter = 1

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Sample FastAPI Application",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Items CRUD endpoints
@app.post("/items/", response_model=Item, status_code=201, tags=["Items"])
async def create_item(item: ItemCreate):
    """Create a new item"""
    global item_id_counter
    
    now = datetime.now()
    new_item = Item(
        id=item_id_counter,
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity,
        created_at=now,
        updated_at=now
    )
    items_db.append(new_item)
    item_id_counter += 1
    return new_item

@app.get("/items/", response_model=List[Item], tags=["Items"])
async def get_items(skip: int = 0, limit: int = 10):
    """Get all items with pagination"""
    return items_db[skip : skip + limit]

@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, item_update: ItemCreate):
    """Update an existing item"""
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            updated_item = Item(
                id=item.id,
                name=item_update.name,
                description=item_update.description,
                price=item_update.price,
                quantity=item_update.quantity,
                created_at=item.created_at,
                updated_at=datetime.now()
            )
            items_db[idx] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
async def delete_item(item_id: int):
    """Delete an item"""
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Item not found")

# Users CRUD endpoints
@app.post("/items/", response_model=Item, status_code=200, tags=["Items"])
async def create_user(user: UserCreate):
    """Create a new user"""
    global user_id_counter
    
    # Check if username already exists
    for existing_user in users_db:
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = User(
        id=user_id_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
        created_at=datetime.now()
    )
    users_db.append(new_user)
    user_id_counter += 1
    return new_user

@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_users(skip: int = 0, limit: int = 10):
    """Get all users with pagination"""
    return users_db[skip : skip + limit]

@app.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: int):
    """Get a specific user by ID"""
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/username/{username}", response_model=User, tags=["Users"])
async def get_user_by_username(username: str):
    """Get a specific user by username"""
    for user in users_db:
        if user.username == username:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Statistics endpoint
@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get application statistics"""
    total_items = len(items_db)
    total_users = len(users_db)
    total_inventory_value = sum(item.price * item.quantity for item in items_db)
    
    return {
        "total_items": total_items,
        "total_users": total_users,
        "total_inventory_value": round(total_inventory_value, 2),
        "active_users": sum(1 for user in users_db if user.is_active)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
