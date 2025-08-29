from django.contrib.auth import logout
from django.http import HttpResponseRedirect


def customlogout(request):
    """
    Logs out the user completely:
    - Deletes Django session server-side
    - Deletes JWT and session cookies
    - Redirects to frontend or OIDC logout
    """
    logout(request)

    # Prepare response to redirect to frontend logout page

    response = HttpResponseRedirect("http://127.0.0.1:5173/login/")

    # Delete cookies
    cookies_to_delete = ["access_token", "refresh_token", "sessionid", "csrftoken"]
    for cookie_name in cookies_to_delete:
        response.delete_cookie(cookie_name, path="/")

    return response
