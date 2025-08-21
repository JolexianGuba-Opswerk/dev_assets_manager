from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("home")

    avatar = getattr(request.user.employee_profile, "avatar_url", None)
    context = {
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "picture": avatar if avatar else "",
    }

    return render(request, "profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")
