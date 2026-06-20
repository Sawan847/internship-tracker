from django.urls import path
from . import views

urlpatterns = [
    path("",                         views.home,               name="home"),
    path("apply/",                   views.apply_view,         name="apply"),
    path("dashboard/",               views.dashboard,          name="dashboard"),
    path("application/<int:app_id>/", views.detail_view,       name="detail"),
    path("update-status/",           views.update_status,      name="update_status"),
    path("delete/<int:app_id>/",     views.delete_application, name="delete"),
]
