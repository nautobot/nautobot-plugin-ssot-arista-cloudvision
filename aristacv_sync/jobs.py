from nautobot.extras.jobs import Job, BooleanVar

from aristacv_sync.diffsync.cloudvision import CloudVision


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
        cv = CloudVision()
        self.log("Loading data from CloudVision")
        cv.load()


jobs = [CVSyncFromJob, CVSyncToJob]