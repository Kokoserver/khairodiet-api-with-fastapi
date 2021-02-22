from datetime import datetime
from mongoengine import *


class Categories(Document):
    category = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

    def to_json(self, *args, **kwargs):
        return{
            "id": str(self.id),
            "categories": self.category,
            "created_at": self.created_at

        }

    @queryset_manager
    def get_single_category(doc_cls, queryset, categoryId):
        return queryset.filter(id=categoryId).first()

    @queryset_manager
    def get_all_category(doc_cls, queryset):
        return queryset.all()


class ServiceOption(Document):
    option = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

    def to_json(self, *args, **kwargs):
        return{
            "id": str(self.id),
            "options": self.option,
            "created_at": str(self.created_at)

        }

    @queryset_manager
    def get_single_option(doc_cls, queryset, optionId):
        return queryset.filter(id=optionId).first()

    @queryset_manager
    def get_all_option(doc_cls, queryset):
        return queryset.all()


class Service(Document):
    name = StringField(required=True, unique=True)
    description = StringField(required=True)
    category = StringField(required=True)
    cover_img = URLField(required=True)
    image_path = StringField(required=True)
    options = ListField(required=True)
    price = IntField(default=3000, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    meta = {"collection": "service"}

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "cover_img": self.cover_img,
            "price": self.price,
            "options": self.options,
            "created_at": str(self.created_at)

        }

    @queryset_manager
    def get_all_service(doc_cls, queryset):
        return queryset.all()

    @queryset_manager
    def get_single_service(doc_cls, queryset, serviceId):
        return queryset.filter(id=serviceId).first()
