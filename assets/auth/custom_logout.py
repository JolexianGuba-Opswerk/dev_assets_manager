from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect


def customlogout(request):
    response = HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    logout(request)
    return response
