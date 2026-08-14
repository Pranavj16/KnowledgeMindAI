from django.shortcuts import render


def placeholder_view(request, title, eyebrow):
    return render(request, "app/placeholder.html", {"title": title, "eyebrow": eyebrow, "section": "future"})
