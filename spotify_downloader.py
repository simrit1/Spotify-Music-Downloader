from mutagen.id3 import ID3, TIT2, TALB, TPE1
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import os
import spotipy
import pytube


class Spotify_Downloader():
    # Stable, Recommended
    def audio_download_pytube(self, url, artist_name, album_name, track_name, loc):
        video = pytube.YouTube(url).streams.filter(only_audio=True).first()
        # File Management for Safety
        if loc[-1] == "/":
            pass
        else:
            loc += "/"

        if os.path.isdir(loc):  # Checking if the Location is true
            os.chdir(loc)
            try:
                # Do not Download audio if it already exists
                if os.path.exists(f"{track_name}.mp3"):
                    return
                else:
                    pass

                out_file = video.download(loc)
                new_file = track_name + '.mp3'
                os.rename(out_file, new_file)

                # Setting up the Artist's Name in Metadata
                tags = ID3()  # No filename as the downloaded file doesn't have ID3 tags
                tags['TIT2'] = TIT2(encoding=3, text=track_name)  # Title
                tags['TPE1'] = TPE1(encoding=3, text=artist_name)  # Artist
                tags['TALB'] = TALB(encoding=3, text=album_name)  # Album Name
                tags.save(new_file)

                # Setting up Indicators
                self.audio_download_success_count += 1
                self.audio_remaining_count -= 1
                print(f"Downloaded {track_name}.mp3")
            except:
                self.audio_download_failure_count += 1
                self.audio_remaining_count -= 1
                print(f"Error in downloading {track_name}.mp3")
        else:
            print("Exiting due to wrong location for download")
            sys.exit()

    def get_names(self, p_link):  # Gets the list of all tracks in a playlist
        playlist_URI = p_link.split("/")[-1].split("?")[0]
        for track in self.sp.playlist_tracks(playlist_URI)["items"]:
            track_name = track["track"]["name"]  # Song name

            artist_uri = track["track"]["artists"][0]["uri"]
            artist_name = self.sp.artist(artist_uri)["name"]  # Artist Name

            album_uri = track["track"]["album"]["uri"]
            album_name = self.sp.album(album_uri)["name"]

            self.data_playlist.append(
                [track_name, artist_name, album_name])

    def start_download_process(self, sp_client_id, sp_secret, p_link):
        # Setting up a connection with the API
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=sp_client_id, client_secret=sp_secret)
            self.sp = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager)
        except:
            print("Error in Validating Spotify Api Key or Secret. Exiting ...")
            sys.exit()

        self.get_names(p_link)
        self.audio_remaining_count = len(self.data_playlist)

    def __init__(self):
        self.data_playlist = []  # Its length is the total number of tracks
        self.audio_download_success_count = 0
        self.audio_download_failure_count = 0
        self.audio_remaining_count = 0
