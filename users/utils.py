from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and response.status_code == status.HTTP_403_FORBIDDEN:
        if 'detail' in response.data and response.data['detail'] == 'Authentication credentials were not provided.':
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {'detail': 'Autentifikatsiya maʼlumotlari taqdim etilmagan.'}
        elif 'detail' in response.data and response.data['detail'] == 'Given token not valid for any token type':
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {
                "detail": "Berilgan token hech qanday token turi uchun yaroqsiz!",
                "code": "token_not_valid",
                "messages": [
                    {
                        "token_class": "AccessToken",
                        "token_type": "access",
                        "message": "Token yaroqsiz yoki muddati tugagan"
                    }
                ]
            }
        elif 'detail' in response.data and response.data['detail'] == ('You do not have permission to perform this '
                                                                       'action.'):
            response.status_code = status.HTTP_403_FORBIDDEN
            response.data = {
                "detail": "Sizda bu amalni bajarish uchun ruxsat yo‘q."
            }

    return response
