from typing import Annotated, Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from app.core.config import settings

router = APIRouter()

@router.get("/hello")
def hello():
    return {"hello": "world"}

@router.get("/hello/{name}")
def hello_name(name: str):
    return {"hello": name}