from pydantic import BaseModel, EmailStr, Field, model_validator


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    confirmPassword: str

    @model_validator(mode= 'after')
    def pass_match(cls, model):
        if model.password != model.confirmPassword:
            raise ValueError("Password does not match!")
        return model