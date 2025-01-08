import os
import asyncio
import random

class Jukebox:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        # pull all files from this directory
        self.songs = []
        self.running_song = None
        for file in os.listdir(directory_path):
            self.songs.append(file)
        # shuffle all the songs
        random.shuffle(self.songs)

    def start(self):
        # begin an endless loop of playing songs
        while True:
            if not self.songs:
                # reinit to start the playlist over again
                self.__init__(self.directory_path)

            song = self.songs.pop(0)
            # write out the song that's about to play
            self.write_song(song)
            self.running_song = asyncio.run(self.play(song))

    async def play(self, song):
        self.running_song = await asyncio.create_subprocess_exec("cvlc", self.directory_path + song, "--play-and-exit", "--quiet")
        await self.running_song.communicate()

    def write_song(self, song):
        file = open("resources/current_song.txt", "w")
        # trim off the .mp3 file extension
        if song[-4:] == ".mp3":
            song = song[:-4]
        file.write(f"Music by Gamechops | {song} | ")
        file.close()

    # add this song as the next song to be played
    def add_song(self, song):
        if os.path.isfile(self.directory_path + song + ".mp3"):
            self.songs.insert(0, song + ".mp3")
            return True
        return False

    def next(self):
        if self.running_song is not None:
            self.running_song.kill()
