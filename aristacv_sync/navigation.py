"""Add Nautobot AristaCV Sync Navigation."""
from nautobot.extras.plugins import PluginMenuItem


menu_items = (
    PluginMenuItem(
        link="plugins:aristacv_sync:cvsync",
        link_text="Sync from Arista CloudVision",
    ),
)
