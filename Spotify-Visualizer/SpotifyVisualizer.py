import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

#DOCUMENTATION:
#https://developer.spotify.com/documentation/web-api
ClientID="1a17b644ac5147a3afa6bf492f54c89e"
Clientsecret="f26d2889023a4c719328654bf45e1dde"
#Authentication (without user)
client_credentials_manager = SpotifyClientCredentials(client_id=ClientID, client_secret=Clientsecret)
spotify = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#generates a random color
def generate_random_color():
    
    colors = [
        "#FF0000",  # Red
        "#00FF00",  # Green
        "#0000FF",  # Blue
        "#FFFF00",  # Yellow
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
        "#FFA500",  # Orange
        "#008080",  # Teal
        "#800080",  # Purple
        "#008000",  # Dark Green
        "#FF4500",  # Orange Red
        "#FFD700",  # Gold
        "#ADFF2F",  # Green Yellow
        "#20B2AA",  # Light Sea Green
        "#800000",  # Maroon
        "#F08080",  # Light Coral
        "#8B4513",  # Saddle Brown
        "#2E8B57",  # Sea Green
        "#D2691E",  # Chocolate
        "#DC143C",  # Crimson
        "#6A5ACD",  # Slate Blue
        "#9370DB",  # Medium Purple
        "#FF69B4",  # Hot Pink
        "#32CD32",  # Lime Green
        "#FF6347",  # Tomato
        "#4B0082",  # Indigo
        "#8B008B",  # Dark Magenta
        "#556B2F",  # Dark Olive Green
    ]
    
    return random.choice(colors)

#range of 0 to 100 based on listens and how recent the listens are
def getTrackPopularity(track):
    return spotify.track(track)['popularity']

#range of 0.0 to 1.0 with 1.0 being most dancable
def getTrackDanceability(track):
    return spotify.audio_features(track)[0]['danceability']

#range from -60 to 0 decibals
def getTrackLoudness(track):
    return spotify.audio_features(track)[0]['loudness']

#range from 0.0 to 1.0 describing the musical positiveness conveyed by a track (high = happy(pos), low = sad(neg))
def getTrackValence(track):
    return spotify.audio_features(track)[0]['valence']

#range from 0.0 to 1.0 representing the measure of intensity
def getTrackEnergy(track):
    return spotify.audio_features(track)[0]['energy']

#scale the value from -60-0 to 0-100
def scaleLoudness(x):
    return ((x - (-60)) / (0 - (-60))) * (100 - 0) + 0

#scale the value from 0-1 to 0-100
def scaleOther(x):
    return x * 100

def getValues(trackID):
    values = [] 
    values.append(getTrackPopularity(trackID))
    values.append(scaleOther(getTrackDanceability(trackID)))
    values.append(scaleLoudness(getTrackLoudness(trackID)))
    values.append(scaleOther(getTrackValence(trackID)))
    values.append(scaleOther(getTrackEnergy(trackID)))
    return values

#takes a list of 5 values to be plotted
def buildRadar(values, names, playlistName):
    labels = ['popularity', 'danceability', 'loudness', 'valence', 'energy']
    num_vars = len(labels) 

    # Split the circle into even parts and save the angles so we know where to put each axis.
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Helper function to plot each car on the radar chart.
    def add_to_radar(song_name, color, value):
        # The plot is a circle, so we need to "complete the loop" and append the start value to the end.
        value += value[:1]
        # Draw the outline of our data.
        ax.plot(angles, value, color=color, linewidth=1, label=song_name)
        # Fill it in.
        ax.fill(angles, value, color=color, alpha=0.25)
    
    for i in range(len(values)):
        add_to_radar(names[i], generate_random_color(), values[i])

    # Fix axis to go in the right order and start at 12 o'clock.
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw axis lines for each angle and label.
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    
    # Go through labels and adjust alignment based on where it is in the circle.
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')
    
    # Ensure radar goes from 0 to 100.
    ax.set_ylim(0, 100)
    # Set position of y-labels (0-100) to be in the middle of the first two axes.
    ax.set_rlabel_position(180 / num_vars)

    #styling
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.set_title(playlistName, y=1.08)

    plt.show()

#returns list of all track ids in a playlist
def getPlaylistTrackIDs(playlist):
    playlistTracks = spotify.playlist_tracks(playlist)['items']
    playlistTrackIDs = []
    for i in playlistTracks:
        track = i['track']
        playlistTrackIDs.append(track['id'])

    return playlistTrackIDs

#returns list of all track names in a playlist
def getPlaylistTrackNames(playlist):
    playlistTracks = spotify.playlist_tracks(playlist)['items']
    playlistTrackNames = []
    for i in playlistTracks:
        track = i['track']
        playlistTrackNames.append(track['name'])

    return playlistTrackNames

#returns list of all track ids in a album
def getAlbumTrackIDs(album):
    albumTracks = spotify.album_tracks(album)['items']
    albumTrackIDs = []
    for i in albumTracks:
        #track = i['track']
        albumTrackIDs.append(i['id'])

    return albumTrackIDs

#returns list of all track names in a playlist
def getAlbumTrackNames(album):
    albumTracks = spotify.album_tracks(album)['items']
    albumTrackNames = []
    for i in albumTracks:
        #track = i['track']
        albumTrackNames.append(i['name'])

    return albumTrackNames

def main():

    link = input("Enter a link to a playlist or album: ")

    #determine if an album or a playlist
    if "/playlist/" in link:
        #get playlist id
        playlist_link = link.rsplit('/', 1)[-1]
        #get playlist info (name, tracks)
        playlistName = spotify.playlist(playlist_link)['name']
        playlist_track_ids =  getPlaylistTrackIDs(playlist_link)
        playlist_track_names =  getPlaylistTrackNames(playlist_link) 
        #build radar plot
        valuesList = []
        for i in playlist_track_ids:
            valuesList.append(getValues(i))
        buildRadar(valuesList, playlist_track_names, playlistName)

    elif "/album/" in link:
        #get album id
        album_link = link.rsplit('/', 1)[-1]
        #get album info (name, tracks)
        albumName = spotify.album(album_link)['name']
        album_track_ids =  getAlbumTrackIDs(album_link)
        album_track_names =  getAlbumTrackNames(album_link) 
        #build radar plot
        valuesList = []
        for i in album_track_ids:
            valuesList.append(getValues(i))
        buildRadar(valuesList, album_track_names, albumName)
    else:
        print("Invalid link. Please try again.")
        main()

if __name__ == "__main__":
    main()
