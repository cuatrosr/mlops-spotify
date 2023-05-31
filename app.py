from flask import Flask,request, render_template
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.preprocessing import LabelEncoder
from joblib import load
import pandas as pd
import spotipy
import os

app = Flask(__name__)

model = load('modelo_xgb.pkl')
cols = ['Nombre', 'Artistas', 'Album', 'Año', 'country', 'Duración_ms', 'Explícito', 'Popularidad', 'Número_de_pista', 'Tempo', 'Modo', 'Energía', 'valence', 'liveness', 'instrumentalness', 'acousticness', 'speechiness', 'genero', 'loudness']

def search_track(track_name):
    client_id = 'eb0e84e3beef4eb1ac9498c6807c7c42'
    client_secret = '048badec708d47b9b5033b018e973168'

    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q=track_name, type='track', limit=1)

    track = results['tracks']['items'][0]
    audio_features = sp.audio_features([track['id']])[0]
    artist_genres = sp.artist(track['artists'][0]['id'])['genres']

    track_data = [{
        'Nombre': track['name'],
        'Artistas': track['artists'][0]['name'],
        'Album': track['album']['name'],
        'Año': track['album']['release_date'][0:4],
        'country' : track['album']['available_markets'][0] if track['album']['available_markets'] else None,
        'Duración_ms': track['duration_ms'],
        'Popularidad': track['popularity'],
        'Número_de_pista': track['track_number'],
        'Tempo': audio_features['tempo'],
        'Modo': audio_features['mode'],
        'Energía': audio_features['energy'],
        'valence' : audio_features['valence'],
        'liveness' : audio_features['liveness'],
        'instrumentalness' : audio_features['instrumentalness'],
        'acousticness' : audio_features['acousticness'],
        'speechiness' : audio_features['speechiness'],
        'genero' : artist_genres,
        'loudness' : audio_features['loudness']
    }]
    return track_data

def clean_df(data_unseen):
    data_unseen = data_unseen.astype({'Año':'int64'})
    data_unseen['genero'] = data_unseen['genero'].apply(lambda x: ','.join(x))
    enc = LabelEncoder()
    data_unseen['Nombre'] = enc.fit_transform(data_unseen['Nombre'])
    data_unseen['Album'] = enc.fit_transform(data_unseen['Album'])
    data_unseen['country'] = enc.fit_transform(data_unseen['country'])
    data_unseen['Artistas'] = enc.fit_transform(data_unseen['Artistas'])
    data_unseen['genero'] = enc.fit_transform(data_unseen['genero'])
    return data_unseen

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/predict',methods=['POST', 'GET'])
def predict():
    int_features = [x for x in request.form.values()]
    data_unseen = pd.DataFrame(search_track(int_features[0]))
    data_unseen = clean_df(data_unseen)
    prediction = model.predict(data_unseen)[0]
    msg = 'is' if prediction == 1 else 'isn\'t'
    return render_template('home.html', pred='The track {} {} explicit'.format(int_features[0], msg))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)