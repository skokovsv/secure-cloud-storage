from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=12, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
