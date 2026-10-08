from .playerctl import get_with_playerctl, toggle_media, next_media, prev_media, length_media, pos_media, loop_media, check_status
from .devstats import get_cpu_temp, get_cpu_freq, get_cpu_load, get_memory_info, get_process_info, get_tasks_info, get_disk_info, get_current_network
#from .vis import get_with_playerctl, toggle_media, next_media, prev_media, legth_media, pos_media
from . import vis

__all__ = ["get_with_playerctl", "toggle_media", "next_media", "prev_media", "length_media", "pos_media", "loop_media", "get_cpu_temp", "get_cpu_freq", "get_cpu_load", "get_memory_info", "get_process_info", "get_tasks_info", "get_disk_info", "get_current_network", "check_status"]
__version__ = "1.0"
