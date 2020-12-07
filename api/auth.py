import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from api.models import User
from api.utils import parseBody


@csrf_exempt
def login(request):
    """
    This method is for user to login
    """
    user_body_data = parseBody(request)

    response = User.CheckUser(user_body_data)
    if response['code']:
        return JsonResponse(response, status=response['code'], safe=False)
    return JsonResponse(response, safe=False)


@csrf_exempt
def logout(request):
    """
    This method is for user to logout
    """
    user_body_data = parseBody(request)

    response = User.RemoveAuthToken(user_body_data)
    if response['code']:
        return JsonResponse(response, status=response['code'], safe=False)
    return JsonResponse(response, safe=False)


@csrf_exempt
def signup(request):
    """
    This method is for user to signup
    """
    user_body_data = parseBody(request)

    response = User.SaveUser(user_body_data)
    if response['code']:
        return JsonResponse(response, status=response['code'], safe=False)
    return JsonResponse(response, safe=False)


def me(request):
    user_body_data = parseBody(request)
    response = User.GetMe(user_body_data)
    if response['code']:
        return JsonResponse(response, status=response['code'], safe=False)
    return JsonResponse(response, safe=False)
