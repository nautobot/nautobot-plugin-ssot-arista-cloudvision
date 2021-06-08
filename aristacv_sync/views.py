from django.views.generic import RedirectView
from django.urls import reverse


class CVSyncFromJobRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("extras:job", kwargs={"class_path": "plugins/aristacv_sync.jobs/CVSyncFromJob"})


class CVSyncToJobRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("extras:job", kwargs={"class_path": "plugins/aristacv_sync.jobs/CVSyncToJob"})