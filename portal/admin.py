from django.contrib import admin
from .models import (
    GSUser, TrackerData, AddUser, AddObject, AddUserObject, UserObject, Command, ObjectActivity, APICommand
)


@admin.register(GSUser)
class GSUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'api_key', 'api', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'api_key')
    list_filter = ('api', 'is_active', 'is_staff')


@admin.register(TrackerData)
class TrackerDataAdmin(admin.ModelAdmin):
    list_display = ('imei', 'dt_tracker', 'lat', 'lng', 'speed', 'loc_valid')
    search_fields = ('imei', 'dt_tracker')
    list_filter = ('loc_valid',)


@admin.register(AddUser)
class AddUserAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)


@admin.register(AddObject)
class AddObjectAdmin(admin.ModelAdmin):
    list_display = ('imei', 'name', 'active', 'active_dt')
    search_fields = ('imei', 'name')
    list_filter = ('active',)


@admin.register(AddUserObject)
class AddUserObjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'object')
    search_fields = ('user__email', 'object__imei')


@admin.register(UserObject)
class UserObjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'object')
    search_fields = ('user__username', 'object__imei')


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ('imei', 'user', 'cmd', 'status')
    search_fields = ('imei__imei', 'user__username', 'cmd')
    list_filter = ('status',)


@admin.register(ObjectActivity)
class ObjectActivityAdmin(admin.ModelAdmin):
    list_display = ('imei', 'active', 'active_dt')
    search_fields = ('imei__imei',)
    list_filter = ('active',)


@admin.register(APICommand)
class APICommandAdmin(admin.ModelAdmin):
    list_display = ('command', 'user', 'created_at')
    search_fields = ('command', 'user__username')
    list_filter = ('created_at',)
