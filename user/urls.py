from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import Login_View, Register_Voew, logout_view, Info_Profile, Info_Reply, Revise_View, upload，Info_page, Go_info_page，Info_View

app_name = 'user'
urlpatterns = [
    path('login/', Login_View.as_view(), name='login'),
    path('register/', Register_Voew.as_view(), name='register'),
    path('info/<str:username>', Info_View.as_view(), name='info'),
    path('logout/', logout_view, name='logout'),
    path('<str:username1>/', Info_Profile.as_view(), name='infoprofile'),
    path('<str:username1>/<int:page_id>/',Info_page, name='infoPage'),
    path('info/go/<str:username1>/',Go_info_page, name='info_Pagego'),
    path('reply/<str:username1>/', Info_Reply.as_view(), name='inforeply'),
    url(r'^upload', upload),
]
