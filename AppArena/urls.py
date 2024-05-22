from django.urls import path
from .views import *


urlpatterns = [
    path('signup/', register, name='sign_un'),
    path('', user_login, name='login'),
    path('sign_out/', user_logout, name='sign_out'),
    path('competitions/', show_competitions, name='show_competitions'),
    path('profile/<int:id_user>', edit_profile, name='profile'),
    path('add_competition/', add_competition, name='add_competition'),
    path('competition/delete/<slug:comp_slug>/', delete_competition, name='delete_competition'),
    path('competition/<slug:comp_slug>', show_competition, name='competition'),
    path('competition/<slug:comp_slug>/choose-judges/', choose_judges, name='choose_judges'),
    path('competition/<slug:comp_slug>category/<slug:category_slug>', category, name='category'),
]