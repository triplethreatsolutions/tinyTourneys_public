# django imports
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
def get_publishable_key(request):
    if request.method == "GET":
        return JsonResponse(
            {
                "publicKey": settings.STRIPE_PUBLISHABLE_KEY,
            }
        )
    else:
        return render(request, "http_response/403.html", status=403)
