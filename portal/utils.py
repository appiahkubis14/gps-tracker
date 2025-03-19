from .models import GSUser, TrackerData, AddUser, AddObject, AddUserObject
from django.utils.timezone import now
import json
from datetime import datetime


# ----------------- USER FUNCTIONS ----------------- #

def get_user_id_from_api_key(api_key):
    """Fetch user ID from API key if API access is enabled."""
    try:
        user = GSUser.objects.get(api_key=api_key)
        return user.id if user.api else None  # Ensure API access is enabled
    except GSUser.DoesNotExist:
        return None


def get_user_id_from_username(username):
    """Fetch user ID from username."""
    try:
        return GSUser.objects.get(username=username).id
    except GSUser.DoesNotExist:
        return None


def get_user_id_from_email(email):
    """Fetch user ID from email."""
    try:
        return GSUser.objects.get(email=email).id
    except GSUser.DoesNotExist:
        return None


def add_user(email, privileges):
    """Add a new user."""
    AddUser.objects.create(email=email, privileges=privileges)


def delete_user(user_id):
    """Delete user by ID."""
    AddUser.objects.filter(id=user_id).delete()


# ----------------- OBJECT FUNCTIONS ----------------- #

def add_object(name, imei, active_dt):
    """Add a new tracking object."""
    AddObject.objects.create(name=name, imei=imei, active_dt=active_dt, active=False)


def delete_object(imei):
    """Delete an object by IMEI."""
    AddObject.objects.filter(imei=imei).delete()


def add_user_object(user_id, imei):
    """Assign an object to a user."""
    try:
        user = AddUser.objects.get(id=user_id)
        obj = AddObject.objects.get(imei=imei)
        AddUserObject.objects.create(user=user, object=obj)
    except (AddUser.DoesNotExist, AddObject.DoesNotExist):
        return None  # Handle missing user or object


def delete_user_object(user_id, imei):
    """Remove an object from a user."""
    AddUserObject.objects.filter(user_id=user_id, object__imei=imei).delete()


def update_object_activity(imei, active, active_dt=None):
    """Update object activity status."""
    try:
        obj = AddObject.objects.get(imei=imei)
        obj.active = active
        obj.active_dt = active_dt if active_dt else now()
        obj.save()
    except AddObject.DoesNotExist:
        return None


# ----------------- TRACKER DATA FUNCTIONS ----------------- #

def params_to_dict(params):
    """Converts params string to dictionary."""
    if isinstance(params, dict):
        return params  # If already a dictionary, return as is

    if not params:
        return {}

    try:
        return json.loads(params)
    except json.JSONDecodeError:
        return {}


def insert_db_loc(loc):
    """Insert tracker location into the database."""
    TrackerData.objects.create(
        imei=loc["imei"],
        protocol=loc.get("protocol", "api_loc"),
        ip=loc.get("ip"),
        port=int(loc["port"]) if loc.get("port") else None,
        dt_server=datetime.strptime(loc["dt_server"], "%Y-%m-%d %H:%M:%S"),
        dt_tracker=datetime.strptime(loc["dt_tracker"], "%Y-%m-%d %H:%M:%S"),
        lat=float(loc["lat"]) if loc.get("lat") else None,
        lng=float(loc["lng"]) if loc.get("lng") else None,
        altitude=float(loc["altitude"]) if loc.get("altitude") else None,
        angle=float(loc["angle"]) if loc.get("angle") else None,
        speed=float(loc["speed"]) if loc.get("speed") else None,
        loc_valid=bool(int(loc["loc_valid"])) if loc.get("loc_valid") else False,
        params=params_to_dict(loc.get("params")),
        event=loc.get("event")
    )
