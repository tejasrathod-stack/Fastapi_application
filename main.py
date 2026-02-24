from fastapi import FastAPI, HTTPException
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

# Configure CORS (safe for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# Pydantic Models
# ============================

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
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


# ============================
# In-Memory Database (Demo)
# ============================

items_db: List[Item] = []
users_db: List[User] = []
item_id_counter = 1
user_id_counter = 1


# ============================
# Root & Health
# ============================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Sample FastAPI Application",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================
# ITEMS CRUD
# ============================

@app.post("/items/", response_model=Item, status_code=201, tags=["Items"])
async def create_item(item: ItemCreate):
    global item_id_counter

    now = datetime.utcnow()

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
    return items_db[skip : skip + limit]


@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, item_update: ItemCreate):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            updated_item = Item(
                id=item.id,
                name=item_update.name,
                description=item_update.description,
                price=item_update.price,
                quantity=item_update.quantity,
                created_at=item.created_at,
                updated_at=datetime.utcnow()
            )
            items_db[index] = updated_item
            return updated_item

    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
async def delete_item(item_id: int):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(index)
            return

    raise HTTPException(status_code=404, detail="Item not found")


# ============================
# USERS CRUD
# ============================

@app.post("/users/", response_model=User, status_code=201, tags=["Users"])
async def create_user(user: UserCreate):
    global user_id_counter

    # Check duplicates
    for existing_user in users_db:
        if existing_user.username.lower() == user.username.lower():
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_user.email.lower() == user.email.lower():
            raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        id=user_id_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
        created_at=datetime.utcnow()
    )

    users_db.append(new_user)
    user_id_counter += 1
    return new_user


@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_users(skip: int = 0, limit: int = 10):
    return users_db[skip : skip + limit]


@app.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/username/{username}", response_model=User, tags=["Users"])
async def get_user_by_username(username: str):
    for user in users_db:
        if user.username.lower() == username.lower():
            return user

    raise HTTPException(status_code=404, detail="User not found")


# ============================
# STATISTICS
# ============================

@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    total_items = len(items_db)
    total_users = len(users_db)

    total_inventory_value = sum(
        item.price * item.quantity for item in items_db
    )

    active_users = sum(
        1 for user in users_db if user.is_active
    )

    return {
        "total_items": total_items,
        "total_users": total_users,
        "total_inventory_value": round(total_inventory_value, 2),
        "active_users": active_users
    }


# ============================
# Run Server
# ============================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
