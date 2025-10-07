from django.urls import path
from .views import RolListView

urlpatterns = [
    path('roles/', RolListView.as_view(), name='roles_list'),
]
