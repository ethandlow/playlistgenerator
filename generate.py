import spotipy
import os

from artist import Artist
from track import Track
from playlist import Playlist
from spotipy import SpotifyOAuth

CLIENT_ID = 'a0c4070f670b48b3afc464c263ba3caa'
CLIENT_SECRET = 'ffe4dd25053a4194a12fc5e3a6c40ac0'
REDIRECT_URI = 'https://localhost:8888/callback'

def avg(l):
    return sum(l)/len(l)

# returns a Track object given a track from the Spotify API
def createTrack(track):
    '''parameters:
    track (TrackObject): track from Spotify API
    '''
    artists = []
    for artist in track['artists']:
        temp = Artist(name=artist['name'], id=artist['id'])
        artists.append(temp)

    name = track['name']
    id = track['id']
    return Track(name=name, id=id, artists=artists)


# returns the user's recently played songs as a Playlist
def getRecentlyPlayed(sp, limit):
    '''
    parameters:
    sp (client object): Spotify API client
    limit (int): number of recently played songs to return
    '''
    recently_played = sp.current_user_recently_played(limit=limit)
    results = []
    for index, item in enumerate(recently_played['items'], start=1):
        temp = createTrack(track=item['track'])
        print(f"{index}. {str(temp)}")
        results.append(temp)
    
    result = Playlist(name="Recently Played", id="", tracks=results)
    return result

# allows the user to select a playlist of their choice and returns a Playlist object
def selectUserPlaylist(sp):
    '''
    parameters:
    sp (client object): Spotify API client
    '''
    playlists = sp.current_user_playlists()['items']
    for index, playlist in enumerate(playlists, start=1):
        print(f"{index}. {playlist['name']}")

    index = int(input("Select a playlist: ")) - 1
    while (index < 0 or index >= len(playlists)):
        index = int(input("Select a playlist: ")) - 1

    playlist = sp.playlist_items(playlists[index]['id'])
    tracks = []
    for item in playlist['items']:
        temp = createTrack(item['track'])
        tracks.append(temp)
    
    name = playlists[index]['name']
    id = playlists[index]['id']
    result = Playlist(name=name, id=id, tracks=tracks)

    print(result)
    return result

# allows the user to select a track to add to their seed tracks
def select(seed_tracks, playlist):
    '''
    parameters:
    seed_tracks (list of Track): list of current seed tracks
    playlist (Playlist object): list of tracks to choose from
    '''
    indexes = input("Select seed tracks: ")
    indexes = indexes.split()
    for index in indexes:
        index = int(index)
        if index > 0 and index <= len(playlist.tracks):
            seed_tracks.append(playlist.tracks[int(index) - 1])

    return seed_tracks

# averages the values of a list of songs' features
def getAvgFeatures(sp, ids):
    '''
    parameters:
    sp (client object): Spotify API client
    ids (list of Spotify ids)= list of song ids to average 
    '''
    acousticness = []
    danceability = []
    energy = []
    instrumentalness = []
    tempo = []
    valence = []

    features = sp.audio_features(ids)
    for item in features:
        acousticness.append(item['acousticness'])
        danceability.append(item['danceability'])
        energy.append(item['energy'])
        instrumentalness.append(item['instrumentalness'])
        tempo.append(item['tempo'])
        valence.append(item['valence'])

    acousticness = avg(acousticness)
    danceability = avg(danceability)
    energy = avg(energy)
    instrumentalness = avg(instrumentalness)
    tempo = avg(tempo)
    valence = avg(valence)

    return acousticness, danceability, energy, instrumentalness, tempo, valence

# generates recommendations based on seed tracks and returns a list of track ids
def getRecommendations(sp, seed_tracks, limit, acousticness, danceability, energy, instrumentalness, tempo, valence):
    '''
    parameters:
    sp (client object): Spotify API client
    seed_tracks (list of Track): seed tracks
    limit (int): number of recomendations to generate
    acousticness (int): target acousticness for recommendations
    danceability (int): target danceability for recommendations
    energy (int): target energy for recommendations
    instrumentalness (int): target instrumentalness for recommendations
    tempo (int): target tempo for recommendations
    valence (int): target valence for recommendations
    '''
    recommendations = []
    tracks = sp.recommendations(seed_tracks=seed_tracks,
                                     limit=limit, 
                                     target_acousticness=acousticness, 
                                     target_danceability=danceability, 
                                     target_energy=energy, 
                                     target_instrumentalness=instrumentalness, 
                                     target_tempo=tempo, 
                                     target_valence=valence)['tracks']
    for track in tracks:
        print(track['name'])
        recommendations.append(track['id'])
    return recommendations 

# generates a plyalist based on seed tracks
def generatePlaylist(sp, seed_tracks):
    '''
    parameters:
    sp (client object): Spotify API client
    seed_tracks (list of Track): list of seed tracks
    '''
    limit = int(input("Length of playlist: ")) - len(seed_tracks)
    name = input("Name of playlist: ")
    uid = sp.me()['id']
    playlist = sp.user_playlist_create(user=uid, name=name)
    pid = playlist['id']

    ids = []

    if len(seed_tracks) > 5:
            for index, track in enumerate(seed_tracks, start=1):
                print(f"{index}. {str(track)}")
            selections = input("Select up to 5 tracks: ")
            selections = selections.split()
            for i in selections:
                if i.isdigit():
                    ids.append(seed_tracks[i].id)
    else:
        for track in seed_tracks:
            ids.append(track.id)
    
    if (len(ids) == 0):
        print("No seed tracks.")
        return
    
    acousticness, danceability, energy, instrumentalness, tempo, valence = getAvgFeatures(sp=sp, ids=ids)

    songs_to_add = getRecommendations(sp=sp, seed_tracks=ids, limit=limit, 
                                      acousticness=acousticness, 
                                      danceability=danceability, 
                                      energy=energy, 
                                      instrumentalness=instrumentalness, 
                                      tempo=tempo, 
                                      valence=valence)
    for track in seed_tracks:
        songs_to_add.append(track.id)
    
    sp.user_playlist_add_tracks(user=uid, playlist_id=pid, tracks=songs_to_add)

def main():
    scope = 'user-read-recently-played playlist-modify-private playlist-modify-public playlist-read-private'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, 
                                                   client_secret=CLIENT_SECRET, 
                                                   redirect_uri=REDIRECT_URI, 
                                                   scope=scope))
    
    seed_tracks = []

    msg = "1. Select seed track(s) from recently played.\n2. Select seed track(s) from playlist.\n3. Generate playlist.\n4. Exit.\n"
    
    while (True): 
        os.system("cls")

        print("=====Spotify Playlist Generator=====")
        print("Seed Tracks: ", end="")
        if (len(seed_tracks) == 0):
            print(seed_tracks)
        else:
            temp = []
            for track in seed_tracks:
                temp.append(str(track))
            print(temp)

        selection = int(input(msg))
        match selection:
            case 1:
                print("=====Last 25 played songs=====")
                recent = getRecentlyPlayed(sp=sp, limit=25)
                seed_tracks = select(seed_tracks=seed_tracks, playlist=recent)
            case 2:
                print("=====User's playlists=====")
                playlist = selectUserPlaylist(sp)
                seed_tracks= select(seed_tracks=seed_tracks, playlist=playlist)
            case 3:
                print("=====Generating playlist=====")
                generatePlaylist(sp=sp, seed_tracks=seed_tracks)
                break
            case 4:
                break
            case _:
                continue
    

if __name__ == "__main__":
    main()