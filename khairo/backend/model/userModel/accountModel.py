from datetime import datetime

from mongoengine import *

from khairo.backend.model.services.serviceModel import Service


class UserAccount(Document):
    firstname = StringField(required=True, min_length=3)
    lastname = StringField(required=True, min_length=3)
    email = EmailField(required=True,  unique=True)
    phoneNo = StringField(required=True)
    gender = StringField(required=True, choices=("male", "female", "other"))
    password = StringField(required=True)
    active_plan = ListField(ReferenceField(Service, dbref=True))
    active = BooleanField(default=False)
    admin = BooleanField(default=False)
    dietician = BooleanField(default=False)
    created_at = DateField(default=datetime.utcnow)
    meta = {"collection": "user"}

    @queryset_manager
    def get_singleUserByEmail(doc_cls, queryset, email):
        return queryset.filter(email=email).first()

    @queryset_manager
    def get_singleUserById(doc_cls, queryset, userId):
        return queryset.filter(id=userId).first()

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "phoneNo": self.phoneNo,
            "active_plan": self.active_plan,
            "active": self.active,
            "admin": self.admin,
            "created_at": str(self.created_at)
        }
