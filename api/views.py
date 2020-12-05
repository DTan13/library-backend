from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from api.models import Book


def index(request):
    return JsonResponse({"status": "Working"}, safe=False)


@csrf_exempt
def books(request):
    body_data = 0
    try:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
    except json.decoder.JSONDecodeError as DecodeError:
        print(DecodeError)

    if request.method == 'POST':
        result = Book.SaveBook(body_data)
        return HttpResponse(result)

    if request.method == 'GET':
        page = request.GET.get('page')
        limit = request.GET.get('limit')

        data = Book.GetBooks(int(page), int(limit))
        return JsonResponse(data, safe=False)
