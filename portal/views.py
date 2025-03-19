from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json

from .models import User, Object, UserObject, Command, TrackerData
from .utils import (
    get_user_id_from_api_key, get_user_id_from_email, params_to_dict,
    insert_db_loc
)


# -----------------------------
# API AUTHENTICATION & ACCESS CONTROL
# -----------------------------
def api_access(request):
    """Handles API authentication and access control."""
    api = request.GET.get("api")
    ver = request.GET.get("ver")
    key = request.GET.get("key")
    cmd = request.GET.get("cmd")

    if not api or not ver or not cmd:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    if ver != "1.0":
        return JsonResponse({"error": "Invalid API version"}, status=400)

    if api == "server":
        if key != settings.HW_KEY:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        return JsonResponse({"message": "Server API Access Granted"})

    if api == "user":
        user_id = get_user_id_from_api_key(key)
        if not user_id:
            return JsonResponse({"error": "Invalid API key"}, status=403)
        return JsonResponse({"message": "User API Access Granted", "user_id": user_id})

    return JsonResponse({"error": "Invalid API type"}, status=400)


# -----------------------------
# TRACKER LOCATION HANDLING
# -----------------------------
@csrf_exempt
def tracker_location(request):
    """Handles tracker location data."""
    if "imei" not in request.GET:
        return JsonResponse({"error": "IMEI not provided"}, status=400)

    loc = {
        "imei": request.GET.get("imei"),
        "protocol": "api_loc",
        "ip": "",
        "port": "",
        "dt_server": now().strftime("%Y-%m-%d %H:%M:%S"),
        "dt_tracker": request.GET.get("dt", now().strftime("%Y-%m-%d %H:%M:%S")),
        "lat": request.GET.get("lat"),
        "lng": request.GET.get("lng"),
        "altitude": request.GET.get("altitude"),
        "angle": request.GET.get("angle"),
        "speed": request.GET.get("speed"),
        "loc_valid": request.GET.get("loc_valid"),
        "params": params_to_dict(request.GET.get("params", "")),
        "event": request.GET.get("event")
    }

    insert_db_loc(loc)
    return JsonResponse({"message": "OK"}, status=200)


# -----------------------------
# USER & OBJECT MANAGEMENT
# -----------------------------
@api_view(['POST'])
def add_user(request):
    """Creates a new user."""
    email = request.data.get('email')
    user, created = User.objects.get_or_create(email=email, defaults={'privileges': {}})
    return Response({"message": "User added", "user": {"id": user.id, "email": user.email}})


@api_view(['POST'])
def delete_user(request):
    """Deletes a user."""
    email = request.data.get('email')
    user = get_object_or_404(User, email=email)
    user.delete()
    return Response({"message": "User deleted"})


@api_view(['POST'])
def add_object(request):
    """Creates a new object (tracker)."""
    data = request.data
    obj = Object.objects.create(
        imei=data.get('imei'),
        protocol=data.get('protocol', ''),
        ip=data.get('ip', ''),
        port=data.get('port', 0),
        active=data.get('active', False),
        active_dt=data.get('active_dt', None),
        name=data.get('name', '')
    )
    return Response({"message": "Object added", "object": {"id": obj.id, "imei": obj.imei, "name": obj.name}})


@api_view(['POST'])
def delete_object(request):
    """Deletes an object (tracker)."""
    imei = request.data.get('imei')
    obj = get_object_or_404(Object, imei=imei)
    obj.delete()
    return Response({"message": "Object deleted"})


@api_view(['POST'])
def add_user_object(request):
    """Assigns an object to a user."""
    email = request.data.get('email')
    imei = request.data.get('imei')
    user = get_object_or_404(User, email=email)
    obj = get_object_or_404(Object, imei=imei)
    UserObject.objects.create(user=user, object=obj)
    return Response({"message": "Object assigned to user"})


@api_view(['POST'])
def delete_user_object(request):
    """Removes an object from a user."""
    email = request.data.get('email')
    imei = request.data.get('imei')
    user = get_object_or_404(User, email=email)
    obj = get_object_or_404(Object, imei=imei)
    UserObject.objects.filter(user=user, object=obj).delete()
    return Response({"message": "Object removed from user"})


# -----------------------------
# OBJECT & COMMAND MANAGEMENT
# -----------------------------
@api_view(['GET'])
def user_get_objects(request, email):
    """Fetches objects assigned to a user."""
    user = get_object_or_404(User, email=email)
    user_objects = UserObject.objects.filter(user=user)
    objects = [{"id": obj.object.id, "imei": obj.object.imei, "name": obj.object.name} for obj in user_objects]
    return Response(objects)


@api_view(['GET'])
def object_get_commands(request, imei):
    """Fetches pending commands for an object and marks them as executed."""
    cmds = Command.objects.filter(imei__imei=imei, status=False)
    response = [{"id": cmd.id, "command": cmd.command, "created_at": cmd.created_at} for cmd in cmds]
    cmds.update(status=True)
    return Response(response)


@api_view(['GET'])
def object_get_locations(request, imeis):
    """Fetches location data for multiple objects."""
    imeis_list = imeis.split(';')
    objects = Object.objects.filter(imei__in=imeis_list)
    data = [{"id": obj.id, "imei": obj.imei, "name": obj.name, "lat": obj.lat, "lng": obj.lng} for obj in objects]
    return Response(data)


@api_view(['GET'])
def object_get_messages(request, imei, dtf, dtt):
    """Fetches messages (commands) for an object within a time range."""
    messages = Command.objects.filter(imei__imei=imei, created_at__range=[dtf, dtt])
    data = [{"id": msg.id, "command": msg.command, "created_at": msg.created_at} for msg in messages]
    return Response(data)


# -----------------------------
# GOOGLE MAPS API INTEGRATION
# -----------------------------
@api_view(['GET'])
def get_address(request, lat, lng):
    """Fetches the address of a given latitude and longitude using Google Maps API."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key=YOUR_API_KEY"
    response = requests.get(url)
    return Response(response.json())
