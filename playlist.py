from track import Track

class Playlist:
    '''Playlist represents a Spotify playlist.'''
    def __init__(self, name, id, tracks):
        '''
        parameters:
        name (str): playlist name
        id (str): Spotify playlist id
        tracks (list of Track): songs in playlist
        '''
        self.name = name
        self.id = id
        self.tracks = tracks

    def __str__(self):
        playlist = f"====={self.name}====="
        for index, track in enumerate(self.tracks, start=1):
            playlist = playlist + f"\n{index}. {str(track)}"
        return playlist