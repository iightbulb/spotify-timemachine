import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os


def configure():
    load_dotenv()


configure()
date = input("Which year would you like to travel to? Type the format as YYYY-MM-DD. \n")
response = requests.get(url=os.getenv('URL') + date)
contents = response.text

soup = BeautifulSoup(contents, "html.parser")

removed_words = ["Songwriter(s):", "Producer(s):", "Imprint/Promotion Label:", "Gains in Weekly Performance", "Additional Awards"]

titles = soup.find_all(name="h3", class_=re.compile("c-title"))

top_100_titles = [title.getText().strip() for title in titles[1:404]]

for word in list(top_100_titles):
    if word in removed_words:
        top_100_titles.remove(word)

print(top_100_titles)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=None,
        client_secret=None,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]

track_uris = []
year = date.split("-")[0]
for track in top_100_titles:
    result = sp.search(q=f"track:{track} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        track_uris.append(uri)
    except IndexError:
        print(f"{track} does not exist in spotify, skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"Top 100 songs for {date}", public=False)

sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
