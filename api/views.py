from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from api.models import Book
from api.utils import parseBody


def index(request):
    return JsonResponse({"status": "Working"}, safe=False)


@csrf_exempt
def books(request):
    body_data = parseBody(request)

    if request.method == 'POST':
        result = Book.SaveBook(body_data)
        return HttpResponse(result)

    if request.method == 'GET':
        page = request.GET.get('page') if request.GET.get(
            'page') != None else 1
        limit = request.GET.get('limit') if request.GET.get(
            'page') != None else 20

        data = Book.GetBooks(int(page), int(limit))

        try:
            if data['code']:
                return JsonResponse(data, status=data['code'], safe=False)
        except (KeyError, TypeError) as error:
            print(error)

        for book in data:
            try:
                book['_id'] = (book['_id'])['$oid']
            except KeyError:
                print(KeyError)
        return JsonResponse(data, safe=False)
