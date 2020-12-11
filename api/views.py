from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from api.models import Book, Admin, User
from api.utils import parseBody


def index(request):
    return JsonResponse({"status": "Working"}, safe=False)


@csrf_exempt
def books(request):
    body_data = parseBody(request)

    if request.method == 'POST':
        try:
            if body_data['type'] == "save":
                result = Admin.SaveBook(body_data['book'], body_data['admin'])
            elif body_data['type'] == 'delete':
                result = Admin.RemoveBook(
                    body_data['book'], body_data['admin'])
            elif body_data['type'] == 'update':
                result = Admin.UpdateBook(
                    body_data['book'], body_data['admin'])
        except KeyError:
            return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

        try:
            if result['code']:
                return JsonResponse(result, status=result['code'], safe=False)
        except KeyError as error:
            print(error)

    if request.method == 'GET':
        page = request.GET.get('page') if request.GET.get(
            'page') != None else 1
        limit = request.GET.get('limit') if request.GET.get(
            'limit') != None else 100

        data = Book.GetBooks(int(page), int(limit))

        try:
            if data['code']:
                return JsonResponse(data, status=data['code'], safe=False)
        except (KeyError, TypeError) as error:
            print(error)

        for book in data:
            try:
                book['_id'] = (book['_id'])['$oid']
                book['user'] = (book['user'])['$oid']
            except KeyError:
                print(KeyError)
        return JsonResponse({'code': 200, 'books': data}, safe=False)


@csrf_exempt
def book(request):
    '''
    Method for various actions related to books
    '''
    parsedRequest = parseBody(request)
    response = None

    if parsedRequest == 0:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

    try:
        if parsedRequest['type'] == 'borrow':
            response = Admin.BorrowBook(
                parsedRequest['user'], parsedRequest['book'])

        if parsedRequest['type'] == "submit":
            response = Admin.SubmitBook(
                parsedRequest['user'], parsedRequest['book']
            )
    except KeyError:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

    try:
        if response['code']:
            return JsonResponse(response, status=response['code'], safe=False)
    except KeyError:
        print(KeyError)

    return JsonResponse(response, safe=False)


@csrf_exempt
def users(request):
    body_data = parseBody(request)

    if body_data == 0:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

    if request.method == "POST":
        try:
            data = User.UpdateUser(
                user_data=body_data['user'], updateduser=body_data['updateduser']
            )
        except KeyError:
            return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

        try:
            if data['code']:
                return JsonResponse(data, status=data['code'], safe=False)
        except (KeyError, TypeError) as error:
            print(error)

    if request.method == 'GET':
        page = request.GET.get('page') if request.GET.get(
            'page') != None else 1
        limit = request.GET.get('limit') if request.GET.get(
            'page') != None else 100

        page = int(page)
        limit = int(limit)
        data = Admin.GetUsers(page, limit, body_data['admin'])

        try:
            if data['code']:
                for user in data['users']:
                    try:
                        user['_id'] = (user['_id'])['$oid']
                        del user['password']
                        del user['authToken']
                        user['book'] = (user['book'])['$oid']
                    except KeyError:
                        print(KeyError)
                return JsonResponse(data, status=data['code'], safe=False)
        except (KeyError, TypeError) as error:
            print(error)
            return JsonResponse(data, status=data['code'], safe=False)


@csrf_exempt
def remove(request):
    body_data = parseBody(request)

    if request.method == "POST":
        try:
            data = User.RemoveUser(body_data['admin'], body_data['user'])
        except KeyError:
            return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)

        try:
            if data['code']:
                return JsonResponse(data, status=data['code'], safe=False)
        except (KeyError, TypeError) as error:
            print(error)
    else:
        return JsonResponse({'code': 404, "error": "Not found"}, status=404, safe=False)
