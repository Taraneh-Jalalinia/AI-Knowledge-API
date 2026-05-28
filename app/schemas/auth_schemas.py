from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class SignupResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
