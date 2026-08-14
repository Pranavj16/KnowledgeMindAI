from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def placeholder_view(request, title, eyebrow):
    return render(request, "app/placeholder.html", {"title": title, "eyebrow": eyebrow, "section": "future"})
