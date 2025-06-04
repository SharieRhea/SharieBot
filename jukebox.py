import os
import asyncio
import random

from image_utils import ColorTracker


class Jukebox:
    def __init__(self, root_directory_path, sub_directory_path):
        self.root_directory_path = root_directory_path
        self.sub_directory_path = sub_directory_path
        # pull all files from this directory
        self.songs = []
        self.running_song = None
        self.playing = True

        self.colortracker = ColorTracker()

        self.populate_queue()

    def populate_queue(self):
        for file in os.listdir(self.root_directory_path + self.sub_directory_path):
            self.songs.append(self.root_directory_path + self.sub_directory_path + file)
        # shuffle all the songs
        random.shuffle(self.songs)

    def start(self):
        # begin an endless loop of playing songs
        while self.playing:
            if not self.songs:
                # reinit to start the playlist over again
                self.populate_queue()

            song = self.songs.pop(0)
            # write out the song that's about to play
            self.write_song(song)
            self.running_song = asyncio.run(self.play(song))

    async def play(self, song):
        self.running_song = await asyncio.create_subprocess_exec(
            "cvlc", song, "--play-and-exit", "--quiet"
        )
        await self.running_song.communicate()

    async def pause(self):
        if self.running_song:
            self.running_song.kill()
        self.playing = False

    def write_song(self, song):
        song = song.split("/")[-1]
        if song[-4:] == ".mp3":
            song = song[:-4]
        self.title, self.artist = song.split(" - ")
        self.update_image()

    # add this song as the next song to be played
    def add_song(self, song):
        for sub_directory in os.listdir(self.root_directory_path):
            new_path = (
                self.root_directory_path + "/" + sub_directory + "/" + song + ".mp3"
            )
            if os.path.isfile(new_path):
                self.songs.insert(0, new_path)
                return True
        return False

    def update_image(self):
        self.colortracker.update_image(self.title, self.artist, "music")

    def next(self):
        if self.running_song is not None:
            self.running_song.kill()
