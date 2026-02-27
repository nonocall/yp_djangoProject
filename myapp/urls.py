from django.urls import path
from . import views

urlpatterns = [
    path('limit_diag/', views.limit_diag, name='limit_diag'),
    path('same_time/', views.same_time, name='same_time'),
    path('over_num/', views.over_num, name='over_num'),
    path('over_level/', views.over_level, name='over_level'),
    path('map_name/<int:tag>/', views.map_name, name='map_name'),
    path('map_name_1/', views.map_name_1, name='map_name_1'),
    path('map_name_2/', views.map_name_2, name='map_name_2'),
    path('map_name_3/', views.map_name_3, name='map_name_3'),
    path('limit_room/', views.limit_room, name='limit_room'),
]