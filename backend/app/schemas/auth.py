from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    is_superuser: bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, user) -> "UserOut":
        return cls(id=str(user.id), email=user.email, username=user.username, is_superuser=user.is_superuser)
