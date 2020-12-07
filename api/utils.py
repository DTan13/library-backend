import json


def parseBody(request):
    user_body_data = 0
    try:
        body_unicode = request.body.decode('utf-8')
        user_body_data = json.loads(body_unicode)
    except json.decoder.JSONDecodeError as DecodeError:
        print(DecodeError)

    return user_body_data
