from django.urls import path
from .views import (
    api_access, tracker_location, parse_gps_data, process_command,
    add_user, delete_user, add_object, delete_object,
    add_user_object, delete_user_object, user_get_objects,
    object_get_commands, object_get_locations, object_get_messages,
    get_address
)

urlpatterns = [
    path('gps/latest/<str:imei>/', parse_gps_data, name='latest_gps_data'),
    path("api/", api_access, name="api_access"),
    path("tracker/", tracker_location, name="tracker_location"),
    path("command/", process_command, name="process_command"),
    
    # User Management
    path('add_user/', add_user, name="add_user"),
    path('delete_user/', delete_user, name="delete_user"),

    # Object (Tracker) Management
    path('add_object/', add_object, name="add_object"),
    path('delete_object/', delete_object, name="delete_object"),
    
    # User-Object Relations
    path('add_user_object/', add_user_object, name="add_user_object"),
    path('delete_user_object/', delete_user_object, name="delete_user_object"),

    # Data Fetching Endpoints
    path('user_get_objects/<str:email>/', user_get_objects, name="user_get_objects"),
    path('object_get_commands/<str:imei>/', object_get_commands, name="object_get_commands"),
    path('object_get_locations/<str:imeis>/', object_get_locations, name="object_get_locations"),
    path('object_get_messages/<str:imei>/<str:dtf>/<str:dtt>/', object_get_messages, name="object_get_messages"),

    # Google Maps API Integration
    path('get_address/<str:lat>/<str:lng>/', get_address, name="get_address"),
]
