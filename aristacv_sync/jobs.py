from grpc import RpcError

from django.templatetags.static import static

from nautobot.extras.jobs import Job, BooleanVar
from nautobot.extras.models.tags import Tag
from nautobot.extras.models.customfields import CustomField

from nautobot_ssot.jobs.base import DataTarget
from nautobot_ssot.jobs.base import DataSource

from aristacv_sync.diffsync.tocv.cloudvision import CloudVision
from aristacv_sync.diffsync.tocv.nautobot import Nautobot

from aristacv_sync.diffsync.fromcv.cloudvision import CloudVision as C
from aristacv_sync.diffsync.fromcv.nautobot import Nautobot as N


class CloudVisionDataSource(DataSource, Job):
    debug = BooleanVar(description="Enable for more verbose debug logging")

    class Meta:
        name = "Sync from CloudVision"
        data_source = "Cloudvision"
        data_source_icon = static("aristacv_sync/cvp_logo.png")
        description = "Sync system tag data from CloudVision to Nautobot"

    def sync_data(self):
        self.log("Loading data from CloudVision")
        cv = C()
        cv.load()
        self.log("Loading data from Nautobot")
        nb = N()
        nb.load()
        self.log("Performing diff between Cloudvision and Nautobot.")
        diff = nb.diff_from(cv)
        self.sync.diff = diff.dict()
        self.sync.save()
        self.log(diff.summary())
        if not self.kwargs["dry_run"]:
            self.log("Syncing to Nautbot")
            try:
                cv.sync_to(nb)
            except RpcError as e:
                self.log_failure("Sync failed.")
                raise e
            self.log_success(message="Sync complete.")

    def lookup_object(self, model_name, unique_id):
        if model_name == "cf":
            try:
                cf_name, value = unique_id.split("__")
                return (CustomField.objects.get(name=f"{cf_name}"), None)
            except CustomField.DoesNotExist:
                pass
        return (None, None)


class CloudVisionDataTarget(DataTarget, Job):
    debug = BooleanVar(description="Enable for more verbose debug logging")

    class Meta:
        name = "CloudVision"
        data_target = "CloudVision"
        data_target_icon = static("aristacv_sync/cvp_logo.png")
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

    def lookup_object(self, model_name, unique_id):
        if model_name == "tag":
            try:
                tag_name, value = unique_id.split("__")
                return (Tag.objects.get(name=f"{tag_name}:{value}"), None)
            except Tag.DoesNotExist:
                pass
        return (None, None)


jobs = [CloudVisionDataSource, CloudVisionDataTarget]
