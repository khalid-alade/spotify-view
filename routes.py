import requests, json
from urllib.parse import urlencode
from flask import render_template, redirect, url_for, request
from spotify_app import app

from spotify_app.cred import SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI,SCOPE
access_token_holder = []


def get_request(access_token, endpoint):
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    response = requests.get(endpoint, headers=authorization_header)
    response_data = json.loads(response.text)
    return response_data

def get_artist(access_token, id):
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    response = requests.get('https://api.spotify.com/v1/artists/{}'.format(id), headers=authorization_header)
    response_artists = json.loads(response.text)
    return response_artists


@app.route('/')
@app.route('/login', methods=['GET'])
def login():
    authentication_request_params = {
    'client_id': SPOTIPY_CLIENT_ID,'response_type': 'code','redirect_uri': 'http://127.0.0.1:5000/profile',
    'state': 'RAndomstrinGRandOmstring',"show_dialog": 'true','scope': SCOPE}
    auth_url = 'https://accounts.spotify.com/en/authorize?' + urlencode(authentication_request_params)

    return redirect(auth_url)


@app.route('/profile')
def index():
    auth_token = request.args['code']
    code_payload = {"grant_type": "authorization_code","code": str(auth_token),"redirect_uri": 'http://127.0.0.1:5000/profile',
    'client_id': SPOTIPY_CLIENT_ID,'client_secret': SPOTIPY_CLIENT_SECRET,}
    
    post_request = requests.post('https://accounts.spotify.com/api/token', data=code_payload)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    access_token_holder.append(access_token)

    return redirect(url_for('me'))



@app.route('/me')
def me():
    if len(access_token_holder) > 0:
        access_token = access_token_holder[0]

        user_data = get_request(access_token, "https://api.spotify.com/v1/me")
        following  = get_request(access_token, "https://api.spotify.com/v1/me/following?type=artist")
        playlists  = get_request(access_token, "https://api.spotify.com/v1/me/playlists")
        first_artist  = get_artist(access_token, '66CXWjxzNUsdJxJ2JdwvnR')
        second_artist  = get_artist(access_token, '06HL4z0CvFAxyc27GXpf02')
        third_artist  = get_artist(access_token, '6vWDO969PvNqNYHIOW5v0m')
        last_artist  = get_artist(access_token, '0EmeFodog0BfCgMzAIvKQp')


        f_name = first_artist['name']
        f_image = first_artist['images'][0]['url']
        first_genre = []
        for genre in first_artist['genres']:
            first_genre.append(genre)
        f_genre = ", ".join(map(str,first_genre))
        f_link = first_artist['external_urls']['spotify']

        s_name = second_artist['name']
        s_image = second_artist['images'][0]['url']
        second_genre = []
        for genre in second_artist['genres']:
            second_genre.append(genre)
        s_genre = ", ".join(map(str,second_genre))
        s_link = second_artist['external_urls']['spotify']

        t_name = third_artist['name']
        t_image = third_artist['images'][0]['url']
        third_genre = []
        for genre in third_artist['genres']:
            third_genre.append(genre)
        t_genre = ", ".join(map(str,third_genre))
        t_link = third_artist['external_urls']['spotify']

        l_name = last_artist['name']
        l_image = last_artist['images'][0]['url']
        last_genre = []
        for genre in last_artist['genres']:
            last_genre.append(genre)
        l_genre = ", ".join(map(str,last_genre))
        l_link = last_artist['external_urls']['spotify']



        Following_count = following['artists']['total']   
        playlists_count = playlists['total']  
        playlists_link = playlists['href']
        username = user_data['display_name']
        Followers = user_data['followers']['total']
        Link_on_spotify = user_data['external_urls']['spotify']
        profile_pic = user_data['images'][0]['url']
        return render_template('spotify_me.html', username=username, Followers=Followers,
        Link_on_spotify=Link_on_spotify, profile_pic=profile_pic, Following_count=Following_count,
        playlists_count=playlists_count, playlists_link=playlists_link, f_name=f_name, f_image=f_image, f_genre=f_genre, f_link=f_link,s_name= s_name,
        s_image=s_image, s_genre=s_genre, s_link=s_link,t_name=t_name, t_image=t_image, t_genre=t_genre, t_link=t_link,l_name=l_name,
        l_image=l_image, l_genre=l_genre, l_link=l_link)
        
    return redirect(url_for('login'))


@app.route('/top-tracks')
def top_tracks():
    if len(access_token_holder) > 0:
        access_token = access_token_holder[0]

        top_tracks = get_request(access_token, "https://api.spotify.com/v1/me/top/tracks?time_range=long_term")
        return render_template('top_tracks.html', top_tracks=top_tracks)
        
    return redirect(url_for('login'))


@app.route('/playlists')
def playlists():
    if len(access_token_holder) > 0:
        access_token = access_token_holder[0]
        playlists = get_request(access_token, "https://api.spotify.com/v1/me/playlists")

        return render_template('playlists.html', playlists=playlists)
    return redirect(url_for('login'))


@app.route('/recents')
def recents():
    if len(access_token_holder) > 0:
        access_token = access_token_holder[0]
        recents = get_request(access_token, "https://api.spotify.com/v1/me/player/recently-played")

        for duration in recents['items']:
            for key, value in enumerate(duration['track']):
                if key == 'duration_ms':
                    time = value['duration_ms']
                    milli = int(time)
                    seconds=(milli/1000)%60
                    minutes=(milli/(1000*60))%60
                    new_time = str(minutes) + ':' + str(seconds)
                    duration['track'][key] = new_time
                    
        return render_template('recents.html', recents=recents)
    return redirect(url_for('login'))

@app.route('/episodes')
def episodes():
    if len(access_token_holder) > 0:
        access_token = access_token_holder[0]
        episodes = get_request(access_token, "https://api.spotify.com/v1/me/episodes")
        return render_template('your_episodes.html', episodes=episodes)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    return redirect(url_for('login'))