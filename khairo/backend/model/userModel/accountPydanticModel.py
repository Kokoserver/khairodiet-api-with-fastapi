from pydantic import BaseModel, EmailStr, Field


class UserRegisterationInput(BaseModel):
    firstname: str = Field(
        title="Username", description="The user name that will appear everywhere", min_length=3, max_length=50)
    lastname: str = Field(
        title="Username", description="The user name that will appear everywhere", min_length=3, max_length=50)
    email: EmailStr
    gender: str
    phoneNo: str
    password: bytes = Field(title="User password",
                            description="User password to protect account")
    confirmPassword: bytes = Field(
        title=" Confirm user password", description="User password to protect account")
    email_verify_url: str


class UserLoginInput(BaseModel):
    email: EmailStr
    password: bytes


class GetPasswordResetLink(BaseModel):
    email: EmailStr
    passwordReset_url: str




class UserPasswordReset(BaseModel):
    userId:str
    password: str
    confirmPassword: str
