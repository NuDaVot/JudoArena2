from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from AppArena.models import ExpansionUser


class ExpansionUserInline(admin.StackedInline):
    model = ExpansionUser
    can_delete = False
    verbose_name_plural = "expansion_user"


class UserAdmin(BaseUserAdmin):
    inlines = [ExpansionUserInline]


class CompetitionAdmin(admin.ModelAdmin):
    search_fields = ('name_competition', 'content')
    prepopulated_fields = {"slug": ("name_competition",)}


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ExpansionUser)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Application)
admin.site.register(Age)
admin.site.register(Weight)
admin.site.register(Category)
admin.site.register(Meet)
admin.site.register(CompetitorReferee)
