from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserSchema(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class PhoneFeaturesSchema(BaseModel):
    id: int
    rating: float
    num_ratings: int
    ram: int
    rom: int
    battery: int
    front_cam: int

    class Config:
        from_attributes = True
