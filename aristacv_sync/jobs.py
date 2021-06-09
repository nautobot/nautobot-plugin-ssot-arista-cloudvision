from requests.exceptions import HTTPError

from nautobot.extras.jobs import Job, BooleanVar

from aristacv_sync.diffsync.cloudvision import CloudVision
from aristacv_sync.diffsync.nautobot import Nautobot


class FormEntry:
    debug = BooleanVar(description="Enable for more verbose debug logging")


class CVSyncFromJob(Job, FormEntry):
    debug = FormEntry.debug

    class Meta:
        name = "Sync from CloudVision"
        description = "Sync system tag data from CloudVision to Nautobot"

    def run(self, data, commit):
        cv = CloudVision()
        self.log("Loading data from CloudVision")
        cv.load()


class CVSyncToJob(Job, FormEntry):
    debug = FormEntry.debug

    class Meta:
        name = "Sync to CloudVision"
        description = "Sync custom tag data from Nautobot to CloudVision"

    def run(self, data, commit):
        self.log("Loading data from CloudVision")
        cv = CloudVision()
        cv.load()
        self.log("Loading data from Nautobot")
        nb = Nautobot()
        nb.load()
        self.log("Performing diff between Nautobot and Cloudvision")
        diff_nb_cv = cv.diff_from(nb)
        self.log(diff_nb_cv.summary())
        if data["debug"]:
            self.log_debug(diff_nb_cv.dict())
        if commit:
            self.log("Syncing to CloudVision")
            try:
                nb.sync_to(cv)
            except HTTPError as e:
                self.log_failure(message=f"Sync failed")
                raise e
            self.log_success(message="Sync complete")


jobs = [CVSyncFromJob, CVSyncToJob]