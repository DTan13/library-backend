from django.http import JsonResponse


def index(request):
    return JsonResponse({"status": "Working"}, safe=False)
