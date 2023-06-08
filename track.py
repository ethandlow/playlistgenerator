from artist import Artist

class Track:
    '''Track represents a Spotify song.'''
    def __init__(self, name, id, artists):
        '''
        parameters:
        name (str): track name
        id (str): Spotify track id
        artists (list of Artist): list of track's artists
        '''
        self.name = name
        self.id = id
        self.artists = artists
    
    def __str__(self):
        info = f"{self.name} by {self.artists[0].name}"
        for artist in self.artists[1:]:
            info = info + ", " + artist.name
        return info
    
    def printArtists(self):
        for index, artist in enumerate(self.artists, start=1):
            print(f"{index}. {artist.name}")