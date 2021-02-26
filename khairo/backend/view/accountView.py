from fastapi import APIRouter, status, Depends
from fastapi.background import BackgroundTasks
from fastapi.responses import Response
from mongoengine import errors

from khairo.backend.mixins.generalMixin import KhairoFullMixin
from khairo.backend.model.userModel import accountModel
from khairo.backend.model.userModel.accountMixin import AccountManager
from khairo.backend.model.userModel.accountPydanticModel import (UserRegisterationInput, UserLoginInput,
                                                                 UserPasswordReset, GetPasswordResetLink)
from khairo.settings import WEBSITE_URL, WEBSITE_NAME, API_BASE_URI

router = APIRouter(prefix=f"{API_BASE_URI}", tags=["User Account"])


@router.post("/register")
def registerUserAccount(user: UserRegisterationInput, background: BackgroundTasks):
    if accountModel.UserAccount.get_singleUserByEmail(email=user.email):
        ErrorResponse = {"message": "Account already exist"}
        return KhairoFullMixin.Response(userMessage=ErrorResponse,
                                        status_code=status.HTTP_400_BAD_REQUEST)
    if user.password == user.confirmPassword:
        try:
            password = AccountManager.hash_password(password=user.password)
            newUserDetails = {
                "email": user.email.lower(),
                "firstname": user.firstname.lower(),
                "lastname": user.lastname.lower(),
                "phoneNo": user.phoneNo,
                "gender": user.gender.lower(),
                "password": password
            }
            newUser = accountModel.UserAccount(**newUserDetails).save(clean=True)
            if newUser:
                mailData = {
                    "title": "Khairo diet Account verification",
                    "message": f" Welcome to {WEBSITE_NAME}, {newUser.firstname} { newUser.lastname}\n "
                               f"Your account was created successfully please "
                               f"click on the link below  to verify your email to continue\n {user.email_verify_url}/{newUser.id}/verify"
                }

                background.add_task(KhairoFullMixin.mailUser, userEmail=newUser.email,
                                    emailTitle=mailData.get("title"),
                                    emailMessage=mailData.get("message"))
                SuccessResponseData = {
                    "message": "Account was created successfully, A mail was sent to your to confirm your email address"}

                return KhairoFullMixin.Response(userMessage=SuccessResponseData,
                                                status_code=status.HTTP_201_CREATED)
            ErrorResponse = {
                "message": "Error creating account, check your detail and try again"}
            return KhairoFullMixin.Response(userMessage=ErrorResponse,
                                            status_code=status.HTTP_400_BAD_REQUEST)
        except errors.ValidationError:
            ErrorResponse = {
                "message": "Error creating account, check your detail and try again"}
            return KhairoFullMixin.Response(userMessage=ErrorResponse,
                                            status_code=status.HTTP_400_BAD_REQUEST)

        except errors.NotUniqueError:
            ErrorResponse = {
                "message": "Account with this email already exist, try again"}
            return KhairoFullMixin.Response(userMessage=ErrorResponse,
                                            status_code=status.HTTP_400_BAD_REQUEST)

    ErrorResponse = {"message": "Password do not match, try again"}
    return KhairoFullMixin.Response(userMessage=ErrorResponse,
                                    status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/user/{userId}/activate")
def confirmEmail(userId: str):
    user = accountModel.UserAccount.objects(id=userId).first()
    if user:
        if user.active:
            responseData = {"message": "account already activated"}
            return KhairoFullMixin.Response(userMessage=responseData,
                                            status_code=status.HTTP_400_BAD_REQUEST)
        user.update(active=True)
        SuccessResponseData = {"message": "Account verified successfully"}
        return KhairoFullMixin.Response(userMessage=SuccessResponseData,
                                        status_code=status.HTTP_200_OK)
    ErrorResponseData = {"message": "Account does not exist"}
    return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/passwordResetting")
def getPasswordLink(userOldData: GetPasswordResetLink, background: BackgroundTasks):
    user = accountModel.UserAccount.get_singleUserByEmail(email=userOldData.email)
    if user:
        mailData = {
            "title": "Password reset",
            "message": f"password reset pass code\n Password reset link: {userOldData.passwordReset_url}/{user.id}"
        }
        background.add_task(KhairoFullMixin.mailUser, userEmail=user.email,
                            emailTitle=mailData.get("title"),
                            emailMessage=mailData.get("message"))
        ResponseData = {"message": "Check your email for password reset link"}
        return KhairoFullMixin.Response(userMessage=ResponseData,
                                        status_code=status.HTTP_200_OK)
    ErrorResponseData = {"message": "Account does not exist"}
    return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@router.put("/passwordReset")
def passwordReset(userOldData: UserPasswordReset):
    user = accountModel.UserAccount.objects(id=userOldData.userId).first()
    if user:
        if userOldData.password.strip() == userOldData.confirmPassword.strip():
            newPassword = AccountManager.hash_password(
                password=userOldData.password)
            if newPassword:
                # user.update(password=newPassword, passwordCode=None)
                SuccessResponseData ={"message": "password change successfully"},
                   
                return KhairoFullMixin.Response(userMessage=SuccessResponseData,
                                                status_code=status.HTTP_200_OK)
            ErrorResponseData = {"message": "could not change password"}
            return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ErrorResponseData = {"message": "password does not match "}
        return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                        status_code=status.HTTP_400_BAD_REQUEST)

    ErrorResponseData = {"message": "Account does not exist"}
    return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/login")
def loginUserAccount(userIn: UserLoginInput, response: Response):
    user = accountModel.UserAccount.get_singleUserByEmail(email=userIn.email)
    if user:
        if user.active:
            if AccountManager.check_password(userIn.password, user.password):
                encode_jwt_access, encode_jwt_refresh = AccountManager.JwtEncoder(
                    user=user.to_json())
                if encode_jwt_access and encode_jwt_refresh:
                    response.set_cookie(key="refresh_token",
                                        value=encode_jwt_refresh,
                                        httponly=True,
                                        max_age=172800,
                                        expires=172800,
                                        domain=WEBSITE_URL,
                                        secure=True)
                plan = accountModel.UserPlan.get_user_plan(userId=user.id)
                SuccessResponseData = {
                    "user": user.to_json(indent=4),
                    "plan": plan.active_plan.to_json() if plan else None,
                    "message": "logged in successfully",
                    "access_token": encode_jwt_access,
                    "access_token_type": "Bearer",
                    "expires": "2 days"
                }
                return KhairoFullMixin.Response(userMessage=SuccessResponseData,
                                                status_code=status.HTTP_200_OK)

            ErrorResponseData = {"message": "Password does not match"}
            return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                            status_code=status.HTTP_401_UNAUTHORIZED)

        ErrorResponseData = {
            "message": "Email was sent to you, please verify your email"}
        return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                        status_code=status.HTTP_401_UNAUTHORIZED)

    ErrorResponseData = {"message": "Account does not exist"}
    return KhairoFullMixin.Response(userMessage=ErrorResponseData,
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/me")
def getUserAccount(user: dict = Depends(AccountManager.authenticate_user)):
    plan = accountModel.UserPlan.get_user_plan(userid=user["id"])
    return KhairoFullMixin.Response({"user": user,
                                     "plan": plan.active_plan.to_json() if plan else None},
                                    status_code=status.HTTP_200_OK)
