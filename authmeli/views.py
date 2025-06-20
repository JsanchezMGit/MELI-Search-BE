from django.contrib.auth.models import User
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
from .models import MercadoLibreToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .serializers import ProductSerializer

@api_view(["GET"])
def meli_callback(request):
    code = request.GET.get("code")
    if not code:
        return Response({"error": "Falta el parámetro 'code'"}, status=400)

    token_url = "https://api.mercadolibre.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.MELI_CLIENT_ID,
        "client_secret": settings.MELI_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.MELI_REDIRECT_URI,
    }

    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return Response({"error": "Token inválido"}, status=500)

    token_data = r.json()

    # Crea un usuario temporal (en producción debes validar mejor)
    username = f"meli_user_{token_data['user_id']}"
    user, created = User.objects.get_or_create(username=username)

    # Guarda o actualiza el token
    MercadoLibreToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", ""),
            "expires_in": token_data["expires_in"],
            "scope": token_data["scope"],
            "token_type": token_data["token_type"],
        },
    )

    return Response({
        "message": "Autenticación exitosa",
        "username": user.username,
        "access_token": token_data["access_token"],
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_products(request):
    query = request.GET.get("q", "")
    if not query:
        return Response({"error": "Parámetro de búsqueda 'q' requerido"}, status=400)

    try:
        meli_token = MercadoLibreToken.objects.get(user=request.user)
    except MercadoLibreToken.DoesNotExist:
        return Response({"error": "Token no encontrado"}, status=403)

    url = f"https://api.mercadolibre.com/sites/MLM/search?q={query}"
    headers = {
        "Authorization": f"Bearer {meli_token.access_token}"
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return Response({"error": "Error en la API de Mercado Libre"}, status=r.status_code)

    results = r.json().get("results", [])
    serialized = ProductSerializer(results, many=True)
    return Response(serialized.data)