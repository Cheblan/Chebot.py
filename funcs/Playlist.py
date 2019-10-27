class Playlist(asyncio.Queue):
    def __iter__(self):
        return self._queue.__iter__()

    def clear(self):
        for song in self._queue:
            try:
                os.remove(song.filename)
            except:
                pass
        self._queue.clear()

    def get_song(self):
        return self.get_nowait()

    def add_song(self, song):
        self.put_nowait(song)

    def __str__(self):
        info = 'Текущий плейлист:\n'
        info_len = len(info)
        for song in self:
            s = str(song)
            l = len(s) + 1  # Counting the extra \n
            if info_len + l > 1995:
                info += '[...]'
                break
            info += f'{s}\n'
            info_len += l
        return info
