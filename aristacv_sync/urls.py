"""Django urlpatterns declaration for aristacv_sync plugin."""
from django.urls import path

from aristacv_sync import views

app_name = "aristacv_sync"

urlpatterns = [path("cvsync/", views.CVSyncJobRedirect.as_view(), name="cvsync")]
