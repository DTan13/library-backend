import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from api.models import User


@csrf_exempt
def login(request):
    """
    This method is for user to login
    """
    user_body_data = 0
    try:
        body_unicode = request.body.decode('utf-8')
        user_body_data = json.loads(body_unicode)
    except json.decoder.JSONDecodeError as DecodeError:
        print(DecodeError)

    reponse = User.CheckUser(user_body_data)
    return JsonResponse(reponse, safe=False)

@csrf_exempt
def signup(request):
    """
    This method is for user to signup
    """
    user_body_data = 0
    try:
        body_unicode = request.body.decode('utf-8')
        user_body_data = json.loads(body_unicode)
    except json.decoder.JSONDecodeError as DecodeError:
        print(DecodeError)

    response = User.SaveUser(user_body_data)
    return JsonResponse(response, safe=False)
