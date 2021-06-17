from grpc import RpcError

from nautobot.extras.jobs import Job, BooleanVar

from nautobot_ssot.jobs.base import DataTarget

from aristacv_sync.diffsync.tocv.cloudvision import CloudVision
from aristacv_sync.diffsync.tocv.nautobot import Nautobot


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


class CloudVisionDataTarget(DataTarget, Job):
    debug = BooleanVar(description="Enable for more verbose debug logging")

    class Meta:
        name = "CloudVision"
        data_target = "CloudVision"
        description = "Sync tag data from Nautobot to CloudVision"

    def sync_data(self):
        self.log("Loading data from CloudVision")
        cv = CloudVision()
        cv.load()
        self.log("Loading data from Nautobot")
        nb = Nautobot()
        nb.load()
        self.log("Performing diff between Nautobot and Cloudvision")
        diff = cv.diff_from(nb)
        self.sync.diff = diff.dict()
        self.sync.save()
        self.log(diff.summary())
        # if self.kwargs["debug"]:
        #     self.log_debug(diff_nb_cv.dict())
        if not self.kwargs["dry_run"]:
            self.log("Syncing to CloudVision")
            try:
                nb.sync_to(cv)
            except RpcError as e:
                self.log_failure("Sync failed.")
                raise e
            self.log_success(message="Sync complete")


jobs = [CVSyncFromJob, CloudVisionDataTarget]
