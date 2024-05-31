from django.urls import path

from .views import *


urlpatterns = [
    path('signup/', register, name='sign_un'),
    path('', user_login, name='login'),
    path('sign_out/', user_logout, name='sign_out'),
    path('competitions/', show_competitions, name='show_competitions'),
    path('profile/<int:id_user>', edit_profile, name='profile'),
    path('add_competition/', add_competition, name='add_competition'),
    path('suitable_participants/<int:id_category>/', suitable_participants, name='suitable_participants'),
    path('suitable_participants/<int:id_category>/participant/<int:id_participant>', suitable_participants, name='suitable_participants_with'),
    path('competition/<slug:comp_slug>', show_competition, name='competition'),
    path('competition/<slug:comp_slug>/choose-judges/', choose_judges, name='choose_judges'),
    path('competition/<slug:comp_slug>/category/<int:id_category>', category, name='category'),
    path('competition/<slug:comp_slug>/category/<int:id_category>/meets/', meets, name='meets'),
    path('competition/<slug:comp_slug>/create_category/', create_category, name='create_category'),
    path('competition/<slug:comp_slug>/category/<int:id_category>/application/<int:id_application>', reject_application, name='reject_application'),
    path('competition/<slug:comp_slug>/category/<int:id_category>/meets/draw/', draw_meet, name='draw_meet'),
    path('meet/<int:meet_id>/', meet_detail, name='meet_detail'),
    path('meet/<int:meet_id>/edit/', edit_meet, name='edit_meet'),
    path('generate_pdf/<slug:comp_slug>/', generate_pdf_view, name='generate_pdf'),
]