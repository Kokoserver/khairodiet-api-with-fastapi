from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional
from khairo.model.customeFom import as_form
from fastapi import File, UploadFile


class CategoryInput(BaseModel):
    category: str


class CategoryUpdateInput(BaseModel):
    id: str
    category: str


@as_form
class ServiceInput(BaseModel):
    name: str
    description: str
    options: str
    price: int
    cover_image: UploadFile = File(...)
    category: str


class ServiceUpdateInput(BaseModel):
    id: str
    name: str
    description: str
    options: list
    price: int


class OptionInput(BaseModel):
    option: str = Field()


class OptionUpdateInput(BaseModel):
    id: str
    option: str = Field()
