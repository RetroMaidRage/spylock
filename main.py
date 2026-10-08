import dearpygui.dearpygui as dpg
import pam
import os
import sys
import time
from datetime import datetime
import psutil
import configparser
import re

from Xlib import X, XK, display
from modules import get_with_playerctl, toggle_media, prev_media, next_media, length_media, pos_media, loop_media,  get_cpu_temp, get_cpu_freq, get_cpu_load, get_memory_info, get_process_info, get_tasks_info, get_disk_info, get_current_network
from modules.vis import audio_bars
from modules import check_status
import threading
import subprocess

import random
#window_name = dpg.get_viewport_configuration(item="title")
is_running = True

last_update = 0
start = True

password = ""
useMask = True

p = pam.pam()

PAM_is_active = False
PAM_login_status = "None"

def PAMLogin():
    global password, PAM_is_active
    PAM_is_active = True
    #pwd = dpg.get_value("login_input")
    dpg.show_item("logit_status_complex")

    dpg.bind_item_theme("logit_status_complex", logit_status_text_in_progress)
    dpg.configure_item("logit_status_complex", label="Authorization...")

    pwd = password

    if p.authenticate(os.getlogin(), pwd):
        dpg.bind_item_theme("logit_status_complex", logit_status_text_success)
        dpg.configure_item("logit_status_complex", label="Success!")
        dpg.stop_dearpygui()
        PAM_is_active = False
        sys.exit()

    else:
        dpg.bind_item_theme("logit_status_complex", logit_status_text_fail)
        dpg.configure_item("logit_status_complex", label="Fail!")
        password = ""
        dpg.configure_item("login_input", default_value=password) #or up to show unmasked attempt
        PAM_is_active = False

    PAM_login_status = "None"
#    dpg.hide_item("logit_status_complex")

cfg_path = "spylock.conf"
config = configparser.ConfigParser()

if os.path.isfile(cfg_path):
    print("Config file detected.")
else:

    config['Properties'] = {
    'screen_width': '1920',
    'screen_height': '1080',
    'fps_limit': '60',
    'vsync': 'True'
    }

    config['DefaultWindowTheme'] = {
    'default_font': 'selawk.ttf',
    'default_font_size': '24',
    'R': '0',
    'G': '0',
    'B': '0',
    'A': '0'
    }

    config['Modules'] = {
    'datetime_viewer': 'False',
    'login_viewer': 'False',
    'media_control': 'False',
    'media_visualizer': 'False',
    'stats_viewer': 'False',
    'gif_viewer': 'False',
    'debug_viewer': 'False'

    }

    config['Login'] = {
    'login_text': 'username',
    'login_font': 'selawk.ttf',
    'login_pos_x': '1',
    'login_pos_y': '1',
    'login_bg': 'True',
    'login_image': 'False',
    'login_image_path': 'login.png'
    }

    config['DateTime'] = {
    'date_text': 'True',
    'time_text': 'True',
    'uptime_text': 'True',
    'datetime_font': 'selawk.ttf',
    'date_pos_x': '1',
    'date_pos_y': '1',
    'time_pos_x': '1',
    'time_pos_y': '1',
    'uptime_pos_x': '1',
    'uptime_pos_y': '1',
    'datetime_bg': 'True',
    }

    config['M_Visualizer'] = {
    'bars_length': '32',
    'bars_spacing': '0',
    'bars_width': '0',
    'bars_y_offset': '0',

    'bars_red': '0',
    'bars_green': '0',
    'bars_blue': '0',
    'bars_alpha': '0',

    'bars_outline_red': '0',
    'bars_outline_green': '0',
    'bars_outline_blue': '0',
    'bars_outline_alpha': '0',
    'bars_outline_thickness': '0',

    'vis_background': 'True',
    'vis_bg_red': '0',
    'vis_bg_green': '0',
    'vis_bg_blue': '0',
    'vis_bg_alpha': '50',
    }

    config['Slideshow'] = {
    'slideshow_timer': '60',
    }

    config['GIF'] = {
    'gif_fps': '25',
    }


    with open(cfg_path, "w") as configfile:
        config.write(configfile)

config.read(cfg_path)

#enable/disable modules
datetime_viewer = config.getboolean("Modules",  "datetime_viewer")
login_viewer = config.getboolean("Modules",  "login_viewer")
stats_viewer = config.getboolean("Modules",  "stats_viewer")
debug_viewer = config.getboolean("Modules",  "debug_viewer")
media_control = config.getboolean("Modules",  "media_control")
media_visualizer = config.getboolean("Modules",  "media_visualizer")
show_media_visualizer = media_visualizer
show_gif = config.getboolean("Modules",  "gif_viewer")
slideshow = config.getboolean("Modules",  "slideshow")

#DefaultWindowTheme
DWC_red = config.getint("DefaultWindowTheme",   "R")
DWC_green = config.getint("DefaultWindowTheme", "G")
DWC_blue = config.getint("DefaultWindowTheme",   "B")
DWC_alpha = config.getint("DefaultWindowTheme", "A")

#M_Datetime
date_pos_x = config.getint("DateTime",   "date_pos_x")
date_pos_y = config.getint("DateTime",   "date_pos_y")
time_pos_x = config.getint("DateTime",   "time_pos_x")
time_pos_y = config.getint("DateTime",   "time_pos_y")
uptime_pos_x = config.getint("DateTime",   "uptime_pos_x")
uptime_pos_y = config.getint("DateTime",   "uptime_pos_y")
datetime_bg = config.getboolean("DateTime",   "datetime_bg")

#M_Visualizer
vis_bars = config.getint("M_Visualizer",  "bars_length")
bars_spacing = config.getint("M_Visualizer",  "bars_spacing")
bars_width = config.getint("M_Visualizer",  "bars_width")
bars_red = config.getint("M_Visualizer",  "bars_red")
bars_green = config.getint("M_Visualizer",  "bars_green")
bars_blue = config.getint("M_Visualizer",  "bars_blue")
bars_alpha = config.getint("M_Visualizer",  "bars_alpha")

bars_outline_red = config.getint("M_Visualizer",  "bars_outline_red")
bars_outline_green = config.getint("M_Visualizer",  "bars_outline_green")
bars_outline_blue = config.getint("M_Visualizer",  "bars_outline_blue")
bars_outline_alpha = config.getint("M_Visualizer",  "bars_outline_alpha")

bars_outline_thickness = config.getint("M_Visualizer",  "bars_outline_thickness")
bars_y_offset  = config.getint("M_Visualizer",  "bars_y_offset")

#M_Visualizer_Background
vis_background = config.getboolean("M_Visualizer",  "vis_background")
vis_bg_red = config.getint("M_Visualizer",  "vis_bg_red")
vis_bg_green = config.getint("M_Visualizer",  "vis_bg_green")
vis_bg_blue = config.getint("M_Visualizer",  "vis_bg_blue")
vis_bg_alpha = config.getint("M_Visualizer",  "vis_bg_alpha")

#M_Slideshow
slideshow_timer = config.getint("Slideshow",  "slideshow_timer")
#M_GIF
gif_fps = config.getint("GIF", "gif_fps")

#Properties
vsync = config.getboolean("Properties",  "vsync")
screen_width = config.getint("Properties",  "screen_width")
screen_height = config.getint("Properties",  "screen_height")

d = display.Display()
root = d.screen().root
root.change_attributes(event_mask=X.KeyPressMask)

screen_w = (screen_width+2)
screen_h = (screen_height+2)

screen_center = [screen_w / 2, screen_h / 2]

edit_mode = False

prev_focused_window = 1

loop_track = False

is_current_played = True
hide_mediacontrol = True

max_ionet_down = 5000

is_not_playing = False
is_paused = None

volume = None

dpg.create_context()
#dpg.create_viewport(title='Spylock', width=screen_w, height=screen_h, x_pos=-2, y_pos=-2)
dpg.create_viewport(title='spylock', width=screen_w, height=screen_h, x_pos=-2, y_pos=-2, always_on_top=True)
dpg.set_viewport_vsync(vsync)

with dpg.font_registry():
    default_font = dpg.add_font("fonts/selawk.ttf", 24)
    #default_font = dpg.add_font("DejaVuSans.ttf", 32)
    time_font = dpg.add_font("fonts/selawk.ttf", 72)
    date_font = dpg.add_font("fonts/selawk.ttf", 52)
    uptime_font = dpg.add_font("fonts/selawk.ttf", 32)
    username_font = dpg.add_font("fonts/selawk.ttf", 36)
    timeline_font = dpg.add_font("fonts/selawk.ttf", 0)
    volume_font = dpg.add_font("fonts/AdobeBlank.ttf", 32)
    stats_font = dpg.add_font("fonts/selawk.ttf", 20)

    dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font)
    dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese, parent=default_font)
    dpg.add_font_range(0x1F000, 0x1FFFF, parent=default_font)

dpg.setup_dearpygui()
dpg.set_viewport_decorated(False)
#dpg.set_viewport_clear_color((0, 0, 0, 0))  # RGBA, альфа = 0

def DebugWin():
    window_name = None
    frame_rate = dpg.get_frame_rate()
    frame_count = dpg.get_frame_count()
    memory = int(get_process_info())
    out = subprocess.check_output(["wmctrl", "-lx"]).decode()

    for line in out.splitlines():
        if "spylock" in line.lower():
            print(line)
            window_name = line

    dpg.configure_item("debug_text", default_value=f"Frame Rate: {frame_rate}\nFrame Count: {frame_count}\nRAM usage: {memory} MB\nTitle:{window_name}")

def DebugSwitch(s,a):
    global datetime_viewer, login_viewer, stats_viewer, debug_viewer, media_control, media_visualizer, slideshow
    tag = dpg.get_item_alias(s)

    match tag:
        case "debug_btn_slideshow":
            slideshow = not slideshow

        case "debug_btn_datetime":
            datetime_viewer = not datetime_viewer
            if dpg.is_item_shown("time_text"):
                dpg.hide_item("time_text")
                dpg.hide_item("date_text")
                dpg.hide_item("uptime_text")
                dpg.hide_item("text_background")
            else:
                dpg.show_item("time_text")
                dpg.show_item("date_text")
                dpg.show_item("uptime_text")
                dpg.show_item("text_background")

        case "debug_btn_login":
            login_viewer = not login_viewer
            if dpg.is_item_shown("login_input"):
                dpg.hide_item("username_text")
                dpg.hide_item("login_input")
                dpg.hide_item("logit_status_complex")
            else:
                dpg.show_item("username_text")
                dpg.show_item("login_input")
                dpg.show_item("logit_status_complex")

        case "debug_btn_mediacontrol":
            media_control = not media_control
            dpg.hide_item("sub_window_1")

        case "debug_btn_mediavis":
            media_visualizer = not media_visualizer
            for i, v in enumerate(audio_bars):
                dpg.hide_item(f"bar_{i}")

        case "debug_btn_stats":
            stats_viewer = not stats_viewer
            if dpg.is_item_shown("sub_window_2"):
                dpg.hide_item("sub_window_2")
            else:
                dpg.show_item("sub_window_2")
    #global boolean
    #boolean = False

def CurrentStats():
    current, minimal, maximum = get_cpu_freq()
    cpu_load = get_cpu_load()

    total, available, used = get_memory_info()
    mem_used = (used / 1024)

    disk_total, disk_available, disk_used, disk_percent = get_disk_info()

    net_download, net_upload = get_current_network()
    #print(net_download, net_upload)

    download_percent = min(net_download / max_ionet_down, 1.0)
    upload_percent   = min(net_upload / max_ionet_down, 1.0)

    window_x, window_y = dpg.get_item_width("sub_window_2"), dpg.get_item_height("sub_window_2")

    stat_bar_x_max = window_x
    stat_bar_y_max_win = window_y

    stat_bar_x_min = 0
    stat_bar_y_min = 0

    stat_bars_offset_y = 80
    stat_bars_width = 40

    stat_bars_spacing = 15
    stat_bars_offset = 0

    stat_bars_opacity = 200

    stat_bar_y_max = stat_bar_y_max_win - stat_bars_offset_y

    cpu_bar_height = stat_bar_y_max * (cpu_load / 100)
    memory_bar_height = stat_bar_y_max * (used / total)
    disk_bar_height = stat_bar_y_max * (disk_percent / 100)
    io_down_bar_height = stat_bar_y_max * download_percent
    io_upl_bar_height = stat_bar_y_max * upload_percent

    text_offset_x = 5
    text_offset_y = 40

#i'm decided use max value as start value because this much comfortable for me, so bars started from
#CPU------------------------------------------------------------------
    dpg.configure_item(
        "cpu_load_bar_bg",
        pmin=(stat_bars_offset, stat_bar_y_max ), #снизу
        pmax=(stat_bars_offset + stat_bars_width, (stat_bar_y_min + 0)), fill=(0,0,0,100)
    )

    dpg.configure_item(
        "cpu_load_bar",
        pmin=(stat_bars_offset, stat_bar_y_max - cpu_bar_height),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_max), fill=(255,0,0,stat_bars_opacity)
    )

    dpg.configure_item("cpu_load_text", default_value=f"{cpu_load}%",
        pos=[stat_bars_offset+text_offset_x, stat_bar_y_max+text_offset_y])

    stat_bars_offset += stat_bars_width + stat_bars_spacing

#MEMORY------------------------------------------------------------------
    dpg.configure_item(
        "memory_bar_bg",
        pmin=(stat_bars_offset, stat_bar_y_max),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_min), fill=(0,0,0,100)
    )

    dpg.configure_item(
        "memory_bar",
        pmin=(stat_bars_offset, stat_bar_y_max - memory_bar_height),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_max), fill=(0,0,255,stat_bars_opacity)
    )

    dpg.configure_item("memory_text", default_value=f"{mem_used:.1f} GB",
        pos=[stat_bars_offset+text_offset_x, stat_bar_y_max+text_offset_y])

    stat_bars_offset += stat_bars_width + stat_bars_spacing

#disk------------------------------------------------------------------
    dpg.configure_item(
        "disk_bar_bg",
        pmin=(stat_bars_offset, stat_bar_y_max),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_min), fill=(0,0,0,100)
    )

    dpg.configure_item(
        "disk_bar",
        pmin=(stat_bars_offset, stat_bar_y_max - disk_bar_height),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_max), fill=(0,255,0,stat_bars_opacity)
    )

    dpg.configure_item("disk_load_text", default_value=f"{disk_available:.1f} GB",
        pos=[stat_bars_offset+text_offset_x, stat_bar_y_max+text_offset_y])

    stat_bars_offset += stat_bars_width + stat_bars_spacing

#network------------------------------------------------------------------
    dpg.configure_item(
        "ionet_down_bar_bg",
        pmin=(stat_bars_offset, stat_bar_y_max),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_min), fill=(0,0,0,100)
    )

    dpg.configure_item(
        "ionet_down_bar",
        pmin=(stat_bars_offset, stat_bar_y_max - io_down_bar_height),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_max), fill=(0,255,255,stat_bars_opacity)
    )

    dpg.configure_item("ionet_down_text", default_value=f"{net_download/ 1024:.1f} MB",
        pos=[stat_bars_offset+text_offset_x, stat_bar_y_max+text_offset_y])

    stat_bars_offset += stat_bars_width + stat_bars_spacing

    dpg.configure_item(
        "ionet_upl_bar_bg",
        pmin=(stat_bars_offset, stat_bar_y_max),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_min), fill=(0,0,0,100)
    )

    dpg.configure_item(
        "ionet_upl_bar",
        pmin=(stat_bars_offset, stat_bar_y_max - io_upl_bar_height),
        pmax=(stat_bars_offset + stat_bars_width, stat_bar_y_max), fill=(0,255,255,stat_bars_opacity)
    )

    dpg.configure_item("ionet_upl_text", default_value=f"{net_upload / 1024:.1f} MB",
        pos=[stat_bars_offset+text_offset_x, stat_bar_y_max+text_offset_y])

    stat_bars_offset += stat_bars_width + stat_bars_spacing
    stat_bars_offset_window = stat_bars_offset
    window_new_x_pos = screen_w -   stat_bars_offset_window

    dpg.configure_item("sub_window_2", width=stat_bars_offset_window, pos=[window_new_x_pos, 0])
    #currentstats update in always

def TerminalEmuDraw():
    if password is not None:
        dpg.configure_item("terminal_input_text", default_value=password)

def TerminalEmuSend():
    input_output = dpg.get_value("terminal_input_text")

    result = subprocess.run(
        [input_output],
        capture_output=True,
        text=True
        )

    output = result.stdout

    dpg.configure_item("terminal_text", default_value=f"{output}")

def MakeScreenshot():
    dpg.hide_item("debug_window")
    dpg.set_frame_callback(dpg.get_frame_count() + 5, MakeScreenshot1)

def MakeScreenshot1():
    dpg.output_frame_buffer(
        f"screenshots/{datetime.now().strftime('%H-%M-%S')}_{datetime.now().strftime('%d-%m-%Y')}.png"
    )
    dpg.show_item("debug_window")

def MakeDisplayScreenshot():
    os.system("import -window root screenshots/display.png")
    #os.system("ffmpeg -y -f x11grab -i :0.0 screenshots/display.png")
    #ffmpeg -f x11grab -i :0.0 output.png

#MakeDisplayScreenshot()

def LoadImage():
    #width, height, channels, data = dpg.load_image("/home/retromaid/Pictures/Anime/Uncategorized/Wall/main2_1920x1080_blur.png")
    width, height, channels, data = dpg.load_image("wallpapers/main2.jpg")

    with dpg.texture_registry(tag="bg_registry"):
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="background_img")


    #width, height, channels, data = dpg.load_image("login1.png")

    #with dpg.texture_registry():
    #    dpg.add_static_texture(width=width, height=height, default_value=data, tag="login_img")

slideshow_images_path = []
slideshow_images = []
#/home/retromaid/start/lock.sh
def Slideshow():
    directory = os.listdir("wallpapers")

    for image in directory:
        if image.lower().endswith((".jpg", ".png")):
            slideshow_images_path.append(image)
        #    print(image)
    #        path = f"{directory}/{image}"
    #        print("loading:", path)
#            width, height, channels, data = dpg.load_image(f"wallpapers/{image}")
#            with dpg.texture_registry(show=False):
#                dpg.add_static_texture(width=width, height=height, default_value=data, tag=f"{image}_img")
#                slideshow_images.append(f"{image}_img")
#
    dpg.add_text("Directory: wallpapers", parent="debug_window")
    #print(slideshow_images_path)


#    for i, img in enumerate(slideshow_images):
#
#        if i % 5 == 0:
#            group = dpg.add_group(horizontal=True, parent="debug_window")
#
#        dpg.add_image(img, parent=group, tag=f"img_{i}", width=128, height=128)

last_update_sl = 0
sl_id = 0

def SlideshowDraw():
    global sl_id, width, height, data, curr_slideshow_texture, last_update_sl

    current_time = time.time()

    if current_time - last_update_sl >= slideshow_timer:
        sl_id +=1

        random_image = random.choice(slideshow_images_path)

        width, height, channels, data = dpg.load_image(f"wallpapers/{random_image}")

        old_slideshow_texture = f"{sl_id}_img"
        curr_slideshow_texture = f"{sl_id + 1}_img"

        print("cur", curr_slideshow_texture)
        print("old", old_slideshow_texture)


        dpg.delete_item(old_slideshow_texture)
        dpg.add_static_texture(width=width, height=height, default_value=data, tag=curr_slideshow_texture, parent="bg_registry")
        dpg.configure_item("main_img",texture_tag=curr_slideshow_texture)

    #    threading.Thread(target=SlideshowRender).start()
    #    if prev_slideshow_texture is not None:
    #        dpg.delete_item(prev_slideshow_texture)

    #    prev_slideshow_texture = curr_slideshow_texture
        if dpg.does_item_exist("background_img"):
            dpg.delete_item("background_img")
        last_update_sl = current_time

def SlideshowRender():
    #print("22")
    dpg.add_static_texture(width=width, height=height, default_value=data, tag=curr_slideshow_texture, parent="bg_registry")
    dpg.configure_item("main_img",texture_tag=curr_slideshow_texture)

def LocalTime():
    currentTime = datetime.now().strftime('%H:%M:%S')
    dpg.configure_item("time_text", default_value=currentTime)

def LocalUser():
    currentUser = os.getlogin()
    dpg.configure_item("username_text", default_value=currentUser)

def LocalDate():
    currentDate = datetime.now().strftime('%d.%m.%Y')
    dpg.configure_item("date_text", default_value=currentDate)

def UptimeTime():
    currentUptime = time.time() - psutil.boot_time()
    hours = int(currentUptime // 3600)
    minutes = int((currentUptime % 3600) // 60)
    seconds = int(currentUptime % 60)
    currentUptimeStr = f"Uptime: {hours} Hours {minutes} Minutes"
    dpg.configure_item("uptime_text", default_value=currentUptimeStr)

def PlaybackSlider(sender, app_data):
    #    print(app_data)
        slider_pos = app_data
        pos_media(slider_pos)

def VolumeSlider(sender, app_data):
        slider_pos = app_data
        os.system(f'amixer -D pulse sset Master {slider_pos}%')

def toggle_loop_media():
    global loop_track
    loop_track = not loop_track
    if loop_track:
        dpg.configure_item("playerctl_loop",label="L+")
    else:
        dpg.configure_item("playerctl_loop",label="L-")

def CurrentlyPlaying():

    global paused_media, is_not_playing, volume
    try:
        artist,title = get_with_playerctl()
        playing = f"{artist} - {title}"
        if hide_mediacontrol:
            dpg.show_item("sub_window_1")

    except:
        if hide_mediacontrol:
            dpg.hide_item("sub_window_1") #if selected hide
        is_not_playing = True
        playing = f""

    text_size = dpg.get_text_size(playing)
    window_width = dpg.get_item_width("sub_window_1")

    window_half_width = dpg.get_item_width("sub_window_1") / 2

    window_pos = [(screen_w - window_width) / 2, 10]

    total_pos, current_pos, time_str, current_str = length_media()

    button_width = dpg.get_item_width("playerctl_prev")

    conf_button_width = (window_half_width - (button_width / 2))
    #print(total_pos, current_pos)

    if text_size is not None:
        conf_width = (window_width - text_size[0]) / 2
        #print("wid", conf_width)

        dpg.configure_item("playerctl_text", label=playing, pos=[0, 10], width=window_width)
        dpg.configure_item("sub_window_1", pos=window_pos)

        dpg.configure_item("playerctl_prev", pos=[conf_button_width-115, 60])
        dpg.configure_item("playerctl_toggle", pos=[conf_button_width, 60])
        dpg.configure_item("playerctl_next", pos=[conf_button_width+115, 60])

        if loop_track:
            dpg.configure_item("playerctl_loop", label="L+", pos=[conf_button_width+225, 60], width = 50)
        else:
            dpg.configure_item("playerctl_loop", label="L-", pos=[conf_button_width+225, 60], width = 50)


        dpg.configure_item("text_timeline", label=f"{current_str} / {time_str}", pos=[conf_button_width-340, 60], width=215)

        timeline_offset = 5

        dpg.configure_item("playerctl_timeline",
            pos=[0+timeline_offset, 105],
            width=window_width-timeline_offset*2,
            height=5,
            min_value=0,
            max_value=total_pos)

        volume_control_offset = 235

        dpg.configure_item("volume_control",
            pos=[window_width/2+volume_control_offset, 60],
            width=160,
            height=5,
            min_value=0,
            max_value=100)

        #if not paused_media:

        current_volume = subprocess.check_output(
            ["amixer", "-D", "pulse", "sget", "Master"]
        ).decode()

        match = re.search(r"\[(\d+)%\]", current_volume)

        if match:
            volume = int(match.group(1))

        dpg.set_value("playerctl_timeline", current_pos)
        dpg.set_value("volume_control", volume)

def LoopMedia():
    if loop_track:
        loop_media()

smooth_bars = [0.0] * vis_bars
vis_gain = 1
vis_bars_height = 300

def VisualizeMedia():
    global media_visualizer, is_paused

    is_paused = check_status()

    if is_not_playing or is_paused:
        media_visualizer = False
    else:
        media_visualizer = True



    base_x = (screen_w / 2) - ((vis_bars * bars_width + (vis_bars - 1) * bars_spacing) / 2) #ширина каждого + промежуток каждого / 2
    base_y = screen_h - bars_y_offset  # bottom
#    audio_bars
    if vis_background == True:
        dpg.configure_item("vis_background", fill=(vis_bg_red,vis_bg_green,vis_bg_blue,vis_bg_alpha),
        pmin=((base_x) + -0.5 * (bars_width + bars_spacing), base_y),
        pmax=((base_x) + vis_bars * (bars_width + bars_spacing),750), color=(0,0,0,0))


    if dpg.does_item_exist("bar_3"):
        for i, v in enumerate(audio_bars):

            target = min(float(v) * vis_gain * vis_bars_height, vis_bars_height)

            if target > smooth_bars[i]:
                speed = 0.5 #35
            else:
                speed = 0.12 #08

            smooth_bars[i] += (target - smooth_bars[i]) * speed

            height = smooth_bars[i]

            dpg.configure_item(
                f"bar_{i}",
                pmin=((base_x) + i * (bars_width + bars_spacing), base_y),
                pmax=((base_x) + i * (bars_width + bars_spacing) + bars_width, base_y - height),
                show=media_visualizer
            )

if show_gif:
    animation_thread = None
    #gif_fps = 60

    from modules.gif import texture_data,frame_width, frame_height, animate_gifs

    def RenderGIF():
        while True:
            gif_frame = animate_gifs()
            dpg.set_value("gif_texture", gif_frame)
            time.sleep(1/gif_fps)

    animation_thread = threading.Thread(target=RenderGIF, daemon=True)

    def StartGIFThread():
        animation_thread.start()

    StartGIFThread()

LoadImage()

with dpg.window(no_move=True,
no_collapse=True,no_close=True,
no_scrollbar=True, no_scroll_with_mouse=False,
no_bring_to_front_on_focus=True, no_resize=True,
horizontal_scrollbar=False, no_title_bar=True,
tag="main_window",
width=screen_w,height=screen_h,
pos=[-1,-1]):
    dpg.draw_image("background_img", [-10,-10], [screen_w,screen_h], tag='main_img')
    pass

with dpg.window(tag="main", #to main
no_title_bar=True,
no_move=True,
no_resize=True,
no_background=True,
no_scrollbar=True,
width=screen_w+8, height=screen_h,
pos=[-8,0],
no_bring_to_front_on_focus=False):

    with dpg.drawlist(width=screen_w, height=screen_h, pos=[screen_center[0], screen_center[1]]):

        if datetime_bg:
            dpg.draw_rectangle(pmin=(screen_center[0]-200, screen_center[1]-250),
            pmax=(screen_center[0]+200, screen_center[1]-70), tag="text_background", color=(0,0,0,0), fill=(0,0,0,50))

    #    dpg.draw_image("login_img",
    #    pmin=[screen_center[0]-100, screen_center[1]-50],
    #    pmax=[screen_center[0]+100, screen_center[1]+150],
    #    tag='userlogin_img')
        if vis_background == True:
            dpg.draw_rectangle(pmin=(0,0), pmax=(1,1), tag="vis_background")

        for i in range(vis_bars):
            dpg.draw_rectangle(
                pmin=(screen_center[0] /2 -20, screen_center[1]),
                pmax=((screen_center[0] /2) + 20, 200),
                color=(bars_outline_red, bars_outline_green, bars_outline_blue, bars_outline_alpha),
                thickness=bars_outline_thickness,
                fill=(bars_red, bars_green, bars_blue, bars_alpha),
                tag=f"bar_{i}"
            )

    dpg.add_text(f"...", tag="time_text", pos=[screen_center[0]+time_pos_x, screen_center[1]+time_pos_y])
    dpg.add_text(f"...", tag="date_text", pos=[screen_center[0]+date_pos_x, screen_center[1]+date_pos_y])
    dpg.add_text(f"...", tag="uptime_text", pos=[screen_center[0]+uptime_pos_x, screen_center[1]+uptime_pos_y])

    dpg.add_text(tag="username_text", pos=[screen_center[0]-60, screen_center[1]+50])
    dpg.add_input_text(tag="login_input", width=250 ,height=100, pos=[screen_center[0]-120, screen_center[1]+100])

    dpg.add_button(label="", tag="logit_status_complex", pos=[screen_center[0]-120, screen_center[1]+110], width=250 ,height=100)

sub_window_1_res = [800, 120]
sub_window_1_center = [sub_window_1_res[0] / 2, sub_window_1_res[1] / 2]
sub_window_1_pos = [(screen_w - 800) / 2, 10]

with dpg.window(label="",tag="sub_window_1",
width=sub_window_1_res[0],
height=sub_window_1_res[1],
pos=sub_window_1_pos,
no_title_bar=True,
no_resize=True,
no_move=True,
show=media_control):
    #dpg.add_input_text(multiline=True, width=600)
    dpg.add_button(label=f"", tag="playerctl_text")
    with dpg.group(horizontal=True):
        dpg.add_button(label="0:00", width=100, tag="text_timeline", callback=lambda: pos_media(0))
        dpg.add_button(label="I<", width=100, tag="playerctl_prev", callback = prev_media)
        dpg.add_button(label="[II>]", width=100, tag="playerctl_toggle", callback = toggle_media)
        dpg.add_button(label=">I", width=100, tag="playerctl_next", callback = next_media)

        dpg.add_button(label="L", width=100, tag="playerctl_loop", callback = toggle_loop_media)

        dpg.add_slider_int(tag="playerctl_timeline", no_input=True, callback=PlaybackSlider)

        dpg.add_slider_int(label="Volume",tag="volume_control", no_input=True, callback=VolumeSlider)

    #dpg.add_button(label="Login", callback=PAMLogin, width=50, height=50, pos=[screen_w-screen_h+201, screen_h/2])

#with dpg.window(label="Terminal Emulator", tag="terminal_window", width=300):

#    dpg.add_input_text(tag="terminal_input_text")
#    dpg.add_button(label="Enter...", callback=TerminalEmuSend)
#    dpg.add_text("Test", tag="terminal_text")
with dpg.window(label="Stats", tag="sub_window_2", width=300, height=400, pos=[screen_w/1.2, 0],
no_title_bar=False,
no_resize=False,
no_close=True,
no_collapse=True,
no_move=False,
show=stats_viewer):
#CPU------------------------------------------
    dpg.draw_rectangle(pmin=(0,0),
    pmax=(100,100), tag="cpu_load_bar_bg", color=(255,0,0,0), fill=(255,0,0,50))
    dpg.draw_rectangle(pmin=(0,0),
    pmax=(100,100), tag="cpu_load_bar", color=(255,0,0,0), fill=(255,0,0,50))

    dpg.add_text("CPU", tag="cpu_load_text")
#RAM------------------------------------------
    dpg.draw_rectangle(pmin=(100,0),
    pmax=(200,100), tag="memory_bar_bg", color=(0,0,255,0), fill=(0,0,255,50))
    dpg.draw_rectangle(pmin=(100,0),
    pmax=(200,100), tag="memory_bar", color=(0,0,255,0), fill=(0,0,255,50))

    dpg.add_text("RAM", tag="memory_text")
#DISK------------------------------------------
    dpg.draw_rectangle(pmin=(50,0),
    pmax=(150,100), tag="disk_bar_bg", color=(0,255,0,0), fill=(0,255,0,50))
    dpg.draw_rectangle(pmin=(50,0),
    pmax=(150,100), tag="disk_bar", color=(0,255,0,0), fill=(0,255,0,50))

    dpg.add_text("DISK", tag="disk_load_text")

#----------------------------------------
#IONET-----------------------------------DOWNLOAD
#----------------------------------------

    dpg.draw_rectangle(pmin=(50,0),
    pmax=(150,100), tag="ionet_down_bar_bg", color=(0,255,0,0), fill=(0,255,0,50))
    dpg.draw_rectangle(pmin=(50,0),
    pmax=(150,100), tag="ionet_down_bar", color=(0,255,0,0), fill=(0,255,0,50))

    dpg.add_text("IONET1", tag="ionet_down_text")
#----------------------------------------
#IONET-----------------------------------UPLOAD
#----------------------------------------
    dpg.draw_rectangle(pmin=(50,0),
    pmax=(150,100), tag="ionet_upl_bar_bg", color=(0,255,0,0), fill=(0,255,0,50))
    dpg.draw_rectangle(pmin=(50,0),
    pmax=(150,100), tag="ionet_upl_bar", color=(0,255,0,0), fill=(0,255,0,50))

    dpg.add_text("IONET2", tag="ionet_upl_text")
#=====================GIF=========================
if show_gif:
    with dpg.texture_registry(show=False):
        dpg.add_raw_texture(
            frame_width,
            frame_height,
            texture_data,
            tag="gif_texture",
            format=dpg.mvFormat_Float_rgb,
        )
    with dpg.window(label="GIF", tag="sub_window_3",
    pos=[1500, 0],
    width=frame_width+15, height=frame_height+70,
    no_resize=True,
    no_scrollbar=True,
    show=show_gif):
        with dpg.drawlist(frame_width, frame_height):
            dpg.draw_image("gif_texture", (0, 0), (frame_width, frame_height))
#===================================================
with dpg.window(label="Debug", tag="debug_window", width=400, height=500,
show=debug_viewer):
    dpg.add_text("", tag="debug_text")
    dpg.add_button(label="Screenshot", callback= MakeScreenshot)
    dpg.add_button(label="Slideshow", tag="debug_btn_slideshow", callback=DebugSwitch)
    dpg.add_button(label=f"Show DateTime", tag="debug_btn_datetime", callback=DebugSwitch)
    dpg.add_button(label="Show Login", tag="debug_btn_login", callback=DebugSwitch)
    dpg.add_button(label="Show MediaControl", tag="debug_btn_mediacontrol", callback=DebugSwitch)
    dpg.add_button(label="Show MediaVis", tag="debug_btn_mediavis", callback=DebugSwitch)
    dpg.add_button(label="Show Stats",  tag="debug_btn_stats",callback=DebugSwitch)

LocalUser()

def Lock():
    root.grab_keyboard(
        True,
        X.GrabModeAsync,
        X.GrabModeAsync,
        X.CurrentTime
    )

dpg.set_frame_callback(1, CurrentlyPlaying)
Slideshow()

dpg.show_viewport()
dpg.toggle_viewport_fullscreen()
dpg.set_viewport_always_top(True)

dpg.bind_font(default_font)
dpg.bind_item_font("time_text", time_font)
dpg.bind_item_font("uptime_text", uptime_font)
dpg.bind_item_font("sub_window_1", uptime_font)
dpg.bind_item_font("date_text", date_font)
dpg.bind_item_font("login_input", uptime_font)
dpg.bind_item_font("username_text", username_font)
dpg.bind_item_font("logit_status_complex", username_font)
dpg.bind_item_font("playerctl_timeline", timeline_font)
dpg.bind_item_font("volume_control", volume_font)
dpg.bind_item_font("sub_window_2", stats_font)

muted = 121
volume_minus = 122
volume_plus = 123
prev_track = 173
play_resume_track = 172
next_track = 171

def GrabKeyboardX11():
    global password
    while d.pending_events():
        event = d.next_event()

        if event.type == X.KeyPress:
            shift = event.state & X.ShiftMask
            group = 1 if shift else 0

            other_keys = event.detail
            print("keycode:", other_keys)

            if other_keys == muted:
                os.system(f'amixer -D pulse sset Master toggle')
            elif other_keys == volume_minus:
                os.system(f'amixer -D pulse sset Master {volume-10}%')
            elif other_keys == volume_plus:
                os.system(f'amixer -D pulse sset Master {volume+10}%')
            elif other_keys == prev_track:
                prev_media()
            elif other_keys == play_resume_track:
                toggle_media()
            elif other_keys == next_track:
                next_media()



            keysym = d.keycode_to_keysym(event.detail, group)

            if keysym == XK.XK_Return:
                #PAMLogin()
                PAMThead = threading.Thread(target=PAMLogin)
                PAMThead.start()

            elif keysym == XK.XK_P:
                dpg.destroy_context()
                sys.exit()

            elif keysym == XK.XK_Delete:
                if not PAM_is_active:
                    password = password[:-1]
                    dpg.configure_item("login_input", default_value=password)

            elif keysym == XK.XK_BackSpace:
                password = ""
                dpg.configure_item("login_input", default_value=password)


 #show terminal emu
            else:
                if not PAM_is_active:
                    if dpg.is_item_shown("logit_status_complex"):
                        dpg.hide_item("logit_status_complex")

                    key = XK.keysym_to_string(keysym)
                    print("Pressed:", key)
                    if key is not None and len(key) == 1:
                        password += str(key)
                        print("Pressed:", key)

            if useMask:
                input_text_mask = "*" * len(password)
                dpg.configure_item("login_input", default_value=input_text_mask)
            else:
                dpg.configure_item("login_input", default_value=password)

            #print("password:", password)
            #dpg.destroy_context()
            #sys.exit()

with dpg.theme() as default_theme: #menu bar
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (65, 65, 65, 110))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (65, 65, 65, 120)) #separately to settings
        dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))       # border color
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 60))     #
        dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5, 0.5)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (75, 75, 75, 120))
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (75, 75, 75, 120))

        dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip, (65, 65, 65, 150))
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGripHovered, (65, 65, 65, 170))
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGripActive, (65, 65, 65, 170))

        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 50), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

with dpg.theme() as sub_window_theme: #menu bar
    with dpg.theme_component(dpg.mvAll):
    #    dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (65, 65, 65, 50))
        #dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (65, 65, 65, 50))
        dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (50, 50, 50, 50))     #

        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255, 190))     #
        #dpg.add_theme_color(dpg.mvThemeCol_SliderGrabHovered, (255, 255, 255, 170))     #
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255, 255))     #
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 50))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 70))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 70))
        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 50)
    #    dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5, 0.5)

        #dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (75, 75, 75, 50))
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (75, 75, 75, 50))

        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (30, 30, 30, 50))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (20, 20, 20, 50))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (20, 20, 20, 50))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (20, 20, 20, 50))

        dpg.add_theme_color(dpg.mvThemeCol_Button, (30, 30, 30, 50))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (20, 20, 20, 70))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (20, 20, 20, 80))

with dpg.theme() as playerctl_text_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))

with dpg.theme() as logit_status_text_in_progress:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))

        dpg.add_theme_color(dpg.mvThemeCol_Text, (255,255,255,220))

with dpg.theme() as logit_status_text_success:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))

        dpg.add_theme_color(dpg.mvThemeCol_Text, (0,255,0,220))

with dpg.theme() as logit_status_text_fail:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))

        dpg.add_theme_color(dpg.mvThemeCol_Text, (255,0,0,220))

        #sdpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 0, 0))
with dpg.theme() as volume_control_theme: #menu bar
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 30))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 50))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 50))
        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 10)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255, 220))


dpg.bind_theme(default_theme)
dpg.bind_item_theme("sub_window_1", sub_window_theme)

dpg.bind_item_theme("playerctl_text", playerctl_text_theme)
dpg.bind_item_theme("volume_control", volume_control_theme)
dpg.bind_item_theme("logit_status_complex", playerctl_text_theme)


def print_memory_map():
    pid = os.getpid()
    result = subprocess.run(['pmap', '-x', str(pid)], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    print('\n'.join(lines[:50]))


while dpg.is_dearpygui_running() and is_running:

    if (dpg.is_item_focused("main")):
        if prev_focused_window != 0:
            dpg.focus_item(prev_focused_window)
    prev_focused_window = dpg.get_focused_item()

    #Each frame
    Lock()
    GrabKeyboardX11()
    if debug_viewer:
        DebugWin()

    if datetime_viewer:
        LocalTime()
        LocalDate()
        UptimeTime()

    if show_media_visualizer:
        VisualizeMedia()

    LoopMedia()

    if slideshow:
        SlideshowDraw()

    #Confire items on first frame
    if start:
        CurrentlyPlaying()
        start = False

    #Call functions once per time
    current_time = time.time()

    if current_time - last_update >= 1:

        subprocess.run([
            "wmctrl", "-x", "-r", "spylock.spylock",
            "-b", "add,above"
        ])

        if media_control:
            CurrentlyPlaying()
        if stats_viewer:
            CurrentStats()

        last_update = current_time

    dpg.render_dearpygui_frame()

dpg.destroy_context()
