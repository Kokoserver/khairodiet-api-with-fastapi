import os
from uuid import uuid4

from fastapi import APIRouter, Depends, status
from mongoengine.errors import NotUniqueError

from khairo.backend.mixins.generalMixin import KhairoFullMixin
from khairo.backend.model.services.serviceModel import (Categories, Service,
                                                        ServiceOption)
from khairo.backend.model.services.servicesPydanticModel import (
    CategoryInput, CategoryUpdateInput, OptionInput, OptionUpdateInput,
    ServiceInput, ServiceUpdateInput)
from khairo.backend.model.userModel.accountMixin import AccountManager
from khairo.settings import (API_BASE_URI, STATIC_DIR, STATIC_FILE_NAME,
                             WEBSITE_URL)

service_router = APIRouter(prefix=f"{API_BASE_URI}/service", tags=["Service"])
option_router = APIRouter(prefix=f"{API_BASE_URI}/option", tags=["option"])
category_router = APIRouter(prefix=f"{API_BASE_URI}/category", tags=["category"])


#  service logic start
@service_router.post("/create")
async def create_service(serviceData: ServiceInput = Depends(ServiceInput.as_form),
                         user: dict = Depends(AccountManager.authenticate_user)):
    """[creating new service]

    Args:
        serviceData (ServiceInput): [name, description, cover_img, price, options, categories]

    Returns:
        [type]: [new_service]
        :param user:
        :param serviceData:
        :type cover_img: object

    """

    # file_type = cover_img.content_type[-3:]
    if user["admin"]:
        try:
            random_string = uuid4().hex
            file_location = f"{STATIC_DIR}/{random_string}{serviceData.cover_image.filename}"
            new_service = Service(
                name=serviceData.name,
                description=serviceData.description,
                price=serviceData.price,
                category=serviceData.category,
                options=serviceData.options.split(','),
                image_path=file_location,
                cover_img=f"{WEBSITE_URL}/{STATIC_FILE_NAME}/{random_string}{serviceData.cover_image.filename}"
            ).save()
            if new_service:
                await KhairoFullMixin.upload(fileObject=serviceData.cover_image, file_path=file_location)
                return KhairoFullMixin.Response(
                    userMessage={"service": new_service.to_json()},
                    status_code=status.HTTP_201_CREATED)
            else:
                new_service.delete()
                return KhairoFullMixin.Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                userMessage={"error": "Error saving service"})
        except NotUniqueError:
            return KhairoFullMixin.Response(userMessage={"message": "service with this name already exist"},
                                            status_code=status.HTTP_400_BAD_REQUEST)
    return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@service_router.get("/{serviceId}")
async def get_single_service(serviceId: str):
    """[get single service]

    Args:
        serviceId (str): [the service Id to be returned]

    Returns:
        [type]: [match service id if exist]
    """
    service = Service.get_single_service(serviceId)
    if service:
        return KhairoFullMixin.Response(userMessage={"service": service.to_json()}, status_code=status.HTTP_200_OK)
    return KhairoFullMixin.Response(userMessage={"message": "service does not exist user"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


@service_router.get("/")
async def get_all_service():
    all_service = Service.get_all_service()
    if all_service:
        return KhairoFullMixin.Response(userMessage={"service": [service.to_json() for service in all_service]},  status_code=status.HTTP_200_OK)
    return KhairoFullMixin.Response(userMessage={"message": "error getting all product"},
                                    status_code=status.HTTP_404_NOT_FOUND)


@service_router.put("/update")
async def update_single_service(serviceData: ServiceUpdateInput, user: dict = Depends(AccountManager.authenticate_user)):
    """[updating service]

    Args:
        serviceData (ServiceUpdateInput): [any passed data]

    Returns:
        [type]: [update_service]
        :param serviceData:
        :param user:
    """
    if user["admin"]:
        update_service = Service.get_single_service(serviceId=serviceData.id)
        if update_service:
            update_service.update(**serviceData.dict())
            update_service.save(clean=True)
            if update_service:
                return KhairoFullMixin.Response(userMessage={"service": update_service.to_json()}, status_code=status.HTTP_200_OK)
            return KhairoFullMixin.Response(userMessage={"message": "Error updating  service"},
                                            status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                        status_code=status.HTTP_401_UNAUTHORIZED)


@service_router.delete("/{serviceId}")
async def remove_single_service(serviceId: str, user: dict = Depends(AccountManager.authenticate_user)):

    """[remove or delete service]

    Args:
        serviceId (str): [service id to be removed]

    Returns:
        [type]: [objectId of the service deleted ]
        :param user:
        :param serviceId:
    """
    if user["admin"]:
        old_data = Service.get_single_service(serviceId)
        if old_data:
            try:
                os.unlink(old_data.image_path)
                old_data.delete()
                return KhairoFullMixin.Response(userMessage={"id": serviceId}, status_code=status.HTTP_200_OK)
            except OSError as e:
                return KhairoFullMixin.Response(userMessage={"message": " error deleting service"},
                                                status_code=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return KhairoFullMixin.Response(userMessage={"message": " error deleting service"},
                                                status_code=status.HTTP_404_NOT_FOUND)
        return KhairoFullMixin.Response(userMessage={"message": " service does not exist"},
                                        status_code=status.HTTP_404_NOT_FOUND)
    else:
        return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                        status_code=status.HTTP_401_UNAUTHORIZED)

#  service logic end

#  creating service option start


@option_router.post("/create")
async def create_service_option(optionData: OptionInput, user: dict = Depends(AccountManager.authenticate_user)):
    if user["admin"]:
        new_option = ServiceOption(**optionData.dict())
        new_option.save(clean=True)
        if new_option:
            return KhairoFullMixin.Response(userMessage={"option": new_option.to_json()},
                                            status_code=status.HTTP_201_CREATED)
        return KhairoFullMixin.Response(userMessage={"message": "error creating option"},
                                        status_code=status.HTTP_400_BAD_REQUEST)
    return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@option_router.get("/")
async def get_service_option():
    all_option = ServiceOption.get_all_option()
    if all_option:
        return KhairoFullMixin.Response(userMessage={"option": [option.to_json() for option in all_option]}, status_code=status.HTTP_200_OK)
    return KhairoFullMixin.Response(userMessage={"message": "no option is found"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@option_router.put("/update")
async def update_service_option(optionData: OptionUpdateInput, user: dict = Depends(AccountManager.authenticate_user)):
    if user["admin"]:
        update_option = ServiceOption.get_single_option(optionId=optionData.id)
        if update_option:
            update_option.update(option=optionData.option)
            update_option.save()
            return KhairoFullMixin.Response(userMessage={"option": update_option.to_json()},
                                            status_code=status.HTTP_200_OK)
        return KhairoFullMixin.Response(userMessage={"message": "error creating option"},
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@option_router.get("/{optionId}")
async def update_service_option(optionId: str):
    single_option = ServiceOption.get_single_option(optionId)
    if single_option:
        return KhairoFullMixin.Response(userMessage={"option": single_option.to_json()}, status_code=status.HTTP_200_OK)
    return KhairoFullMixin.Response(userMessage={"message": "option does not exist"},
                                    status_code=status.HTTP_404_NOT_FOUND)


@option_router.delete("/{optionId}")
async def update_service_option(optionId: str, user: dict = Depends(AccountManager.authenticate_user)):
    if user["admin"]:
        old_option = ServiceOption.get_single_option(optionId)
        if old_option:
            old_option.delete()
            return KhairoFullMixin.Response(userMessage={"id": optionId}, status_code=status.HTTP_200_OK)
        return KhairoFullMixin.Response(userMessage={"message": "error deleting option"},
                                        status_code=status.HTTP_400_BAD_REQUEST)
    return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)


#   service option end

# service categories start


@category_router.post("/create")
async def create_service_category(category: CategoryInput, user: dict = Depends(AccountManager.authenticate_user)):
    if user["admin"]:
        new_Category = Categories(**category.dict())
        new_Category.save(clean=True)
        if new_Category:
            return KhairoFullMixin.Response(userMessage={"category": new_Category.to_json()},
                                            status_code=status.HTTP_201_CREATED)
        return KhairoFullMixin.Response(userMessage={"message": "error adding category"},
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@category_router.put("/update")
async def create_service_category(category: CategoryUpdateInput, user: dict = Depends(AccountManager.authenticate_user)):
    if user["admin"]:
        update_Category = Categories.get_single_category(
            categoryId=category.id)
        if update_Category:
            update_Category.update(**category.dict())
            update_Category.save(clean=True)
            return KhairoFullMixin.Response(userMessage={"category": update_Category.to_json()},
                                            status_code=status.HTTP_200_OK)
        return KhairoFullMixin.Response(userMessage={"message": "error adding category"},
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)


@category_router.get("/")
async def create_service_category():
    get_all_category = Categories.get_all_category()
    if get_all_category:
        return KhairoFullMixin.Response(userMessage={"category": [category.to_json() for category in Categories.get_all_category() ]}, status_code=status.HTTP_200_OK)
    return KhairoFullMixin.Response(userMessage={"message": "no category is found"},
                                    status_code=status.HTTP_404_NOT_FOUND)


@category_router.delete("/{categoryId}")
async def create_service_category(categoryId: str, user: dict = Depends(AccountManager.authenticate_user)):
    if user["admin"]:
        new_Category = Categories.get_single_category(categoryId)
        if new_Category:
            new_Category.delete()
            return KhairoFullMixin.Response(userMessage={"id": categoryId}, status_code=status.HTTP_200_OK)
        return KhairoFullMixin.Response(userMessage={"message": "category is found"},
                                        status_code=status.HTTP_404_NOT_FOUND)
    return KhairoFullMixin.Response(userMessage={"message": " error validating admin"},
                                    status_code=status.HTTP_401_UNAUTHORIZED)
