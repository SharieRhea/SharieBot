import subprocess
import time

def get_song():
    output = subprocess.run(["rhythmbox-client", "--print-playing"], capture_output = True)
    return output.stdout.decode("UTF-8").strip()

def write_song(song):
    file = open("resources/currentSong.txt", "w")
    file.write(f"Music by Gamechops | {song} | ")
    file.close()

def loop():
    # start playing music
    # note: there is no way to specify a specific rhythmbox playlist, this will play all songs in
    # the folder that rhythmbox checks for music
    subprocess.run(["rhythmbox-client", "--play"])
    song = get_song()
    write_song(song)
    while True:
        new_song = get_song()
        if song != new_song:
            write_song(new_song)
            song = new_song
        time.sleep(1)
