"""Django urlpatterns declaration for aristacv_sync plugin."""
from django.urls import path

from aristacv_sync import views

app_name = "aristacv_sync"

urlpatterns = [
    path("syncfromcv/", views.CVSyncFromJobRedirect.as_view(), name="syncfromcv"),
    path("synctocv/", views.CVSyncToJobRedirect.as_view(), name="synctocv"),
]
