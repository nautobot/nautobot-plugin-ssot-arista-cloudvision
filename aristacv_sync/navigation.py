"""Add Nautobot AristaCV Sync Navigation."""
from nautobot.extras.plugins import PluginMenuItem


menu_items = (
    PluginMenuItem(
        link="plugins:aristacv_sync:syncfromcv",
        link_text="Sync from Arista CloudVision",
    ),
    PluginMenuItem(
        link="plugins:aristacv_sync:synctocv",
        link_text="Sync to Arista CloudVision",
    ),
)
