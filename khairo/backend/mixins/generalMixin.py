from fastapi.responses import JSONResponse
import smtplib
from khairo.settings import EMAIL, PASSWORD
import shutil


class KhairoFullMixin:
    @staticmethod
    def Response(userMessage: object, status_code: int) -> object:
        return JSONResponse(content=userMessage, status_code=status_code)

    @staticmethod
    async def upload(fileObject, file_path):
        try:
            with open(file_path, "wb+") as file_object:
                shutil.copyfileobj(fileObject.file, file_object)
                return True
        except Exception as e:
            return False

    @staticmethod
    def mailUser(userEmail: str, emailMessage: str, emailTitle):
        ######################### setting mail server #######################
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as access360Mail:
            try:
                ######################### Authenticate account #######################
                access360Mail.login(EMAIL, PASSWORD)
                ######################### setting up mail body #######################
                # message["subject"] = emailTitle
                # message['from'] = EMAIL
                # message['to'] = userEmail
                # message.set_content(emailMessage)
                # access360Mail.send_message(message)
                message = f"subject:{emailTitle}\n\n {emailMessage}"
                access360Mail.sendmail(EMAIL, userEmail, message)
                ######################### return success message #######################
                print("message sent successfully")
                return "message sent successfully"

            except Exception:
                ######################### return error if mail failed to send #######################
                print("message sent successfully")
                return "Error sending message"
