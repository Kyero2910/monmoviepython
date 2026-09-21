from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

API_TOKEN = os.environ.get("TMDB_API_TOKEN")
API_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"


def recuperer_films(url, params):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "accept": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )
    
    print("STATUT TMDB :", response.status_code)
    print("REPONSE TMDB :", response.text[:300])

    if response.status_code != 200:
        return []

    data = response.json()

    return data.get("results", [])


@app.route("/")
def accueil():
    films = recuperer_films(
        f"{API_URL}/movie/popular",
        {
            "language": "fr-FR",
            "page": 1
        }
    )

    return render_template(
        "index.html",
        films=films,
        image_url=IMAGE_URL
    )


@app.route("/recherche")
def recherche():
    recherche = request.args.get("q", "").strip()

    if recherche == "":
        return render_template(
            "index.html",
            films=[],
            image_url=IMAGE_URL,
            erreur="Veuillez entrer un film."
        )

    films = recuperer_films(
        f"{API_URL}/search/movie",
        {
            "query": recherche,
            "language": "fr-FR",
            "page": 1
        }
    )

    if not films:
        return render_template(
            "index.html",
            films=[],
            image_url=IMAGE_URL,
            erreur="Aucun film trouvé."
        )

    return render_template(
        "index.html",
        films=films,
        image_url=IMAGE_URL
    )


@app.route("/suggestions")
def suggestions():
    recherche = request.args.get("q", "").strip()

    if recherche == "":
        return []

    films = recuperer_films(
        f"{API_URL}/search/movie",
        {
            "query": recherche,
            "language": "fr-FR",
            "page": 1
        }
    )

    suggestions = []

    for film in films[:5]:
        suggestions.append({
            "id": film.get("id"),
            "title": film.get("title"),
            "release_date": film.get("release_date"),
            "vote_average": film.get("vote_average"),
            "poster_path": film.get("poster_path")
        })

    return suggestions


@app.route("/film/<int:film_id>")
def details_film(film_id):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "accept": "application/json"
    }

    response = requests.get(
        f"{API_URL}/movie/{film_id}",
        headers=headers,
        params={
            "language": "fr-FR"
        }
    )

    if response.status_code != 200:
        return "Film introuvable."

    film = response.json()

    return render_template(
        "details.html",
        film=film,
        image_url="https://image.tmdb.org/t/p/w780"
    )


if __name__ == "__main__":
    app.run(debug=True)