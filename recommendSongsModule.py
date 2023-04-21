from scipy.spatial.distance import cdist
import numpy as np
import pandas as pd
import time
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

number_cols = ['popularity', 'duration_ms', 'explicit', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
               'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature', 'year']


def get_mean_vector(song_list):

    song_vectors = []

    for song in song_list:
        song_vector = np.empty((0,))

        for col in number_cols:
            song_vector = np.append(song_vector, song[col])

        song_vectors.append(song_vector)

    song_matrix = np.array(list(song_vectors))
    print('Calculated the mean vector...')
    return np.mean(song_matrix, axis=0)


def check_explicit(Song_df, show_explicit=False):
    print('Checking for explicit songs... ', show_explicit, type(show_explicit))
    if show_explicit == False:
        explicit_songs = Song_df[Song_df['explicit'] == False]
        return explicit_songs

    return Song_df


def release_year_filter_fun(songs_list, start_year=1920, end_year=2020):
    print('Checking for release year filter...')
    filter_condition = (songs_list['year'] >= start_year) & (
        songs_list['year'] <= end_year)
    if filter_condition.any():
        filtered_songs = songs_list[filter_condition]
        return pd.DataFrame(filtered_songs)
    else:
        return pd.DataFrame(columns=songs_list.columns)


def tempo_class_filter(songs_list, tempo_value=None):
    print('Checking for Tempo filter...')
    if tempo_value == 0:
        filtered_tempo = songs_list[songs_list['tempo_class'] == 'class1']

    elif tempo_value == 1:
        filtered_tempo = songs_list[songs_list['tempo_class'] == 'class2']
    else:
        filtered_tempo = songs_list[songs_list['tempo_class'] == 'class3']

    return filtered_tempo


def recommend_songs(song_list, distance_types=['cosine', 'euclidean', 'cityblock', 'jaccard'], n_songs=25000, explicit_filter=None, release_year_filter=None, tempo_filter=None):
    start_time = time.time()
    print('Filters: ', explicit_filter,
          release_year_filter, tempo_filter)

    spotify_data = pd.read_csv(
        r"tracks_data.zip", compression='zip', header=0, sep=',', quotechar='"')

    cols = spotify_data.columns
    spotify_data = spotify_data.drop(cols[0], axis=1)

    print('Read the data...')
    spotify_data['year'] = spotify_data['release_date'].str[:4]
    spotify_data['year'] = spotify_data['year'].astype('int64')

    # Create a function to map tempo to class

    def map_tempo_to_class(tempo):
        if tempo <= 90:
            return 'class1'
        elif tempo <= 130:
            return 'class2'
        else:
            return 'class3'

    # Apply the function to the 'tempo' column and create a new column 'tempo_class'
    spotify_data['tempo_class'] = spotify_data['tempo'].apply(
        lambda x: map_tempo_to_class(x))

    print('Added Tempo column to the data...')

    # spotify_data.dropna(inplace=True)

    # spotify_data = spotify_data.drop_duplicates(subset=['name', 'artists'])

    song_cluster_pipeline = Pipeline([('scaler', StandardScaler()),
                                      ('kmeans', KMeans(n_clusters=20,
                                                        verbose=False))
                                      ], verbose=False)

    X = spotify_data.select_dtypes(np.number)
    number_cols = list(X.columns)
    song_cluster_pipeline.fit(X)
    song_cluster_labels = song_cluster_pipeline.predict(X)
    spotify_data['cluster_label'] = song_cluster_labels

    print('Clustering done...')

    metadata_cols = ['name', 'year', 'artists',
                     'explicit', 'tempo', 'tempo_class', 'id']

    song_center = get_mean_vector(song_list)

    # Scale the input data using the scaler from the song clustering pipeline
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(spotify_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))

    print('Scaled the features...')

    distances = []
    for distance_type in distance_types:
        dist_mat = cdist(scaled_song_center, scaled_data, distance_type)
        distances.append(dist_mat)

    print('Calculated the distances...')

    ensemble_distances = np.mean(np.stack(distances), axis=0)

    index = list(np.argsort(ensemble_distances)[:, :n_songs][0])
    rec_songs = spotify_data.iloc[index]
    song_list_df = pd.DataFrame(song_list)  # Convert song_list to a DataFrame
    # Use song_list_df instead of song_list
    rec_songs = rec_songs[~rec_songs['id'].isin(song_list_df['id'])]
    recommended_songs = rec_songs[metadata_cols].to_dict(orient='records')

    print("Recommendations are ready!")
    Song_df = pd.DataFrame(recommended_songs)

    filtered_songs = Song_df
    print('Filtered Songs Shape: ', filtered_songs.shape)

    if explicit_filter is not None:
        filtered_songs = check_explicit(Song_df, explicit_filter)

    print('Explicit Filtered Songs Shape: ', filtered_songs.shape)

    if release_year_filter is not None:
        filtered_songs = release_year_filter_fun(
            filtered_songs, release_year_filter['start_year'], release_year_filter['end_year'])

    if tempo_filter is not None:
        filtered_songs = tempo_class_filter(filtered_songs, tempo_filter)
    end_time = time.time()

    print('Total time taken: ', end_time-start_time)

    return filtered_songs['id'][:10]
