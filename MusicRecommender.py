from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from recommendSongsModule import recommend_songs

app = Flask(__name__)
app.use_static_for = 'static'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="98b3473922a946a3b93292d2300534f2",
                                                           client_secret="705eff8e88ff4f5d9f1131b397b297b6"))

song_audio_features = []


def recommendSongsModule():
    # time.sleep(3)
    return ["5Rn1DPzSzUktbhuNDDJocS", "4AoQVhME8Ko6LNm4lV2wwQ",
            "06JpgY7DgZDe8aHURDNBvQ", "7ptdw6ybSdlbifWWp4sfvb", "26b3oVLrRUaaybJulow9kz"]


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/get_audio_features', methods=['GET', 'POST'])
def get_audio_features():
    if request.method == 'POST':
        song_id = request.form['id']
        song_features = sp.track(song_id)
        audio_features = sp.audio_features(song_id)[0]
        audio_features['popularity'] = song_features['popularity']
        audio_features['year'] = int(
            song_features['album']['release_date'][:4])

        print(song_features['explicit'], type(song_features['explicit']))
        if song_features['explicit']:
            audio_features['explicit'] = 1
        else:
            audio_features['explicit'] = 0

        song_audio_features.append(audio_features)
        print(audio_features)
        return audio_features
    else:
        return "Failure"


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        song_name = request.form['songName']
        print(f"Searching for {song_name}")

        results = sp.search(q='track: {}'.format(song_name), limit=5)

        if results['tracks']['items'] == []:
            return None

        song_list = []

        for song in results['tracks']['items']:
            song_attr = {}
            song_attr['id'] = song['id']
            song_attr['name'] = song['name']
            song_attr['year'] = song['album']['release_date'][:4]
            song_attr['album_image_url'] = song['album']['images'][0]['url']
            song_list.append(song_attr)

        return song_list
    else:
        return render_template('index.html')


@app.route('/get_recommendations', methods=['GET', 'POST'])
def get_recommendations():
    # We need to call the recommend_songs function here

    print('IN GET RECOMMENDATIONS!!!!!!!!!!!')
    if request.method == 'POST':

        explicit_filter = request.form['explicit']
        print(type(explicit_filter))

        if explicit_filter == 'true':
            explicit_filter = 1
        elif explicit_filter == 'false':
            explicit_filter = 0
        else:
            explicit_filter = None

        startYear = request.form['startYear']
        year_filter = None
        if startYear == "None":
            year_filter = None
        else:
            year_filter = {
                'start_year': int(request.form['startYear']),
                'end_year': int(request.form['endYear'])
            }

        tempo_filter = request.form['tempo']
        if tempo_filter == "None":
            tempo_filter = None
        else:
            tempo_filter = int(tempo_filter) - 1

        recommendation_ids = recommend_songs(
            song_audio_features, explicit_filter=explicit_filter, release_year_filter=year_filter, tempo_filter=tempo_filter)

        print(recommendation_ids)

        songs = []
        for id in recommendation_ids:
            song_details = {}
            song = sp.track(id)
            song_details['name'] = song['name']
            song_details['artist'] = ""
            for artist in song['artists']:
                song_details['artist'] += artist['name'] + ", "
            song_details['artist'] = song_details['artist'][:-2]
            song_details['album'] = song['album']['name']
            song_details['year'] = song['album']['release_date'][:4]
            song_details['image_url'] = song['album']['images'][0]['url']
            song_details['url'] = song['external_urls']['spotify']
            songs.append(song_details)

        print(songs[0])

        return songs

    else:
        print('Looking for IDs')

        ids = ["5Rn1DPzSzUktbhuNDDJocS", "4AoQVhME8Ko6LNm4lV2wwQ",
               "06JpgY7DgZDe8aHURDNBvQ", "7ptdw6ybSdlbifWWp4sfvb", "26b3oVLrRUaaybJulow9kz"]

        songs = []
        for id in ids:
            song_details = {}
            song = sp.track(id)
            song_details['name'] = song['name']
            song_details['artist'] = ""
            for artist in song['artists']:
                song_details['artist'] += artist['name'] + ", "
            song_details['artist'] = song_details['artist'][:-2]
            song_details['album'] = song['album']['name']
            song_details['year'] = song['album']['release_date'][:4]
            song_details['image_url'] = song['album']['images'][0]['url']
            song_details['url'] = song['external_urls']['spotify']
            songs.append(song_details)

        print(songs[0])

        return songs


if __name__ == '__main__':
    app.run(debug=True)
