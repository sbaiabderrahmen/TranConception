from django.urls import path
from .views import home, afficher ,detailExpedition

app_name = 'Expedition'
urlpatterns = [
    path('home/',home, name='home'),
    path('afficher/<str:name>/',afficher,
    name='afficher'),
]
urlpatterns += [
    path('',home , name='home'),
    path('afficher/<str:name>/',afficher, name='afficher'),
    path('detail/<str:reference>/', detailExpedition, name='detail_expedition'),
    path('list/', detailExpedition, name='list_expeditions'),
]