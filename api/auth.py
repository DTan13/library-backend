import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from api.models import User, Admin
from api.utils import parseBody


@csrf_exempt
def login(request):
    """
    This method is for user to login
    """
    user_body_data = parseBody(request)

    if user_body_data == 0:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

    response = User.CheckUser(user_body_data)
    try:
        if response['code']:
            admin_response = Admin.CheckUser(user_body_data)
            try:
                if admin_response['code']:
                    return JsonResponse(response, status=response['code'], safe=False)
            except KeyError:
                return JsonResponse(admin_response, safe=False)
    except KeyError:
        print(KeyError)

    return JsonResponse(response, safe=False)


@csrf_exempt
def logout(request):
    """
    This method is for user to logout
    """
    user_body_data = parseBody(request)

    if user_body_data == 0:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

    response = User.RemoveAuthToken(user_body_data)
    try:
        if response['code']:
            return JsonResponse(response, status=response['code'], safe=False)
    except KeyError:
        print(KeyError)
    return JsonResponse(response, safe=False)


@csrf_exempt
def signup(request):
    """
    This method is for user to signup
    """
    user_body_data = parseBody(request)

    if user_body_data == 0:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

    response = User.SaveUser(user_body_data)
    try:
        if response['code']:
            return JsonResponse(response, status=response['code'], safe=False)
    except KeyError:
        print(KeyError)
    return JsonResponse(response, safe=False)


def me(request):
    user_body_data = parseBody(request)

    if user_body_data == 0:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

    response = User.GetMe(user_body_data)
    try:
        if response['code']:
            return JsonResponse(response, status=response['code'], safe=False)
    except KeyError:
        print(KeyError)
    return JsonResponse(response, safe=False)
