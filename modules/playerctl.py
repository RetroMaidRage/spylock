import subprocess

paused = None

def get_with_playerctl():
    try:
        title = subprocess.check_output(
            ['playerctl', 'metadata', 'xesam:title']
        ).decode().strip()

        artist = subprocess.check_output(
            ['playerctl', 'metadata', 'xesam:artist']
        ).decode().strip()

        #print(f"{artist} - {title}")
        #print("   ", artist)

        return artist, title

    except subprocess.CalledProcessError:
        return None


def check_status():
    try:
        status = subprocess.check_output(
            ['playerctl', 'status']
        ).decode().strip()

        if status == "Playing":
            paused = False
        else:
            paused = True

        return paused
    except subprocess.CalledProcessError:
        return True

def pause_media():
    subprocess.run(["playerctl", "pause"])

def resume_media():
    subprocess.run(["playerctl", "play"])

def toggle_media():
    global paused
    paused != paused
    subprocess.run(["playerctl", "play-pause"])

def next_media():
    subprocess.run(["playerctl", "next"])

def prev_media():
    subprocess.run(["playerctl", "previous"])

def length_media():
    try:
        length_us = int(subprocess.check_output(["playerctl", "metadata", "mpris:length"]).strip())
        total_seconds = length_us // 1_000_000
        minutes = total_seconds // 60
        secs = total_seconds % 60

        current_pos = float(subprocess.check_output(
        ["playerctl", "position"]
        ).strip())


        current_sec = int(current_pos)
        curr_minutes = current_sec // 60
        curr_seconds = current_sec % 60

        str_total = f"{minutes}:{secs:02d}"
        str_current = f"{curr_minutes}:{curr_seconds:02d}"

        return total_seconds, current_pos, str_total, str_current

    except:
        return 0,0, "0:00","0:00"

def pos_media(pos):
    subprocess.run(["playerctl", "position", str(pos)])

def loop_media():
    total_seconds, current_pos, str_total, str_current = length_media()
    if total_seconds - current_pos < 0.5:
        subprocess.run(["playerctl", "position", str(0)])

check_status()
