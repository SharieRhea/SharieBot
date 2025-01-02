import os
import subprocess
import random

class MusicHandler:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        # pull all files from this directory
        self.songs = []
        for file in os.listdir(directory_path):
            self.songs.append(file)
        # shuffle all the songs
        random.shuffle(self.songs)

        # begin
        self.start()
    
    def start(self):
        # begin an endless loop of playing songs
        while True:
            if not self.songs:
                # reinit to start the playlist over again
                self.__init__(self.directory_path)
            song = self.songs.pop()
            # write out the song that's about to play
            self.write_song(song)
            # this blocks until the song has finished
            subprocess.run(["cvlc", self.directory_path + song, "--play-and-exit"])

    def play(self):
        song = self.songs.pop()
        print(f"playing song {song}")
        subprocess.run(["cvlc", song, "--play-and-exit"])
        print("done playing")

    def write_song(self, song):
        file = open("resources/current_song.txt", "w")
        # trim off the .mp3 file extension
        file.write(f"Music by Gamechops | {song[:-4]} | ")
        file.close()

def play():
    MusicHandler("/home/sharie/Music/test/")
