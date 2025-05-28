import os

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Any
from app.schemas.user import UserCreate, User, UserLogin, UserWithToken
from app.schemas.graph import Graph, PathResult
from app.cruds import user as user_crud
from app.core.security import (
    verify_password, 
    create_access_token, 
    verify_token,
)
from app.db.database import get_db
from app.services.tsp import solve_tsp
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Any:
    token = credentials.credentials
    user_id = verify_token(token)
    user = user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/sign-up/", response_model=UserWithToken)
def sign_up(
    user: UserCreate, 
    db: Session = Depends(get_db)
) -> Any:
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    user = user_crud.create_user(db=db, user=user)
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return UserWithToken(
        id=user.id,
        email=user.email,
        token=token
    )

@router.post("/login/", response_model=UserWithToken)
def login(
    user: UserLogin, 
    db: Session = Depends(get_db)
) -> Any:
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return UserWithToken(
        id=db_user.id,
        email=db_user.email,
        token=token
    )

@router.get("/users/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    return current_user


@router.post("/shortest-path/", response_model=PathResult)
def get_shortest_path(
    graph: Graph,
    current_user: User = Depends(get_current_user)
) -> PathResult:
    return solve_tsp(graph)
