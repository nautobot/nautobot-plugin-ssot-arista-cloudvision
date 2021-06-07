from django.views.generic import RedirectView
from django.urls import reverse


class CVSyncJobRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("extras:job", kwargs={"class_path": "plugins/aristacv_sync.jobs/CVSyncJob"})
