class Artist:
    '''Artists represents a song artist.'''
    def __init__(self, name, id):
        '''
        parameters
        name (str): name of artist
        id (str): Spotify id of artist
        '''
        self.name = name
        self.id = id

    def __str__(self):
        return self.name