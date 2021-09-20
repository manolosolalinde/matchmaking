from re import match
from flask import Flask, jsonify, render_template, request,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import *
from datetime import datetime
from matchmaking import Matchmaking
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgres:pass@localhost:5432/mydatabase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# @app.route("/")
# def index():
#     flights = Flight.query.all()
#     return render_template("index.html", flights=flights)

@app.route("/clear_players",methods=["POST"])
def clear_players():
    current_match = Match.query.order_by(Match.id.desc()).first()
    if request.form.get("clear") is not None:
        current_match.clear_all_players()
    # myurl = url_for("matchmaking")
    return redirect('/')



@app.route("/", methods=["POST", "GET"])
def matchmaking():
    """Look at Players"""
    # Get match last id (last match)
    current_match = Match.query.order_by(Match.id.desc()).first()
    if current_match is None:
        m = Match(date=datetime.today())
        db.session.add(m)
        db.session.commit()
        current_match = Match.query.order_by(Match.id.desc()).first()

    # Get form information.
    if request.method == "POST":
        #Add new player
        if request.form.get("name") is not None:
            name = request.form.get("name")
            if request.form.get("mmr") is None:
                mmr = 3000
            else:
                mmr = int(request.form.get("mmr"))
            Player.add_player(name=name,mmr=mmr)
        elif request.form.get("matchmaking") is not None:
            # Sort players with matchmaking
            current_match.update_matchmaked_players()
            matchlist = current_match.get_players_tuples()
            if len(matchlist)>2:
                matchmaking1 = Matchmaking(matchlist)
                newlist = matchmaking1.solve()[0]
                current_match.update_teams(newlist)
        elif request.form.get("include_player") is not None:
            # Add player to current match
            matchplayer = request.form.get('include_player')
            current_match.add_player(matchplayer)
        elif request.form.get("delete_player") is not None:
            # Delete player
            matchplayer = request.form.get('delete_player')
            current_match.delete_player(matchplayer)

    if len(current_match.matchmaked_players)==0:
        current_match.update_matchmaked_players()
    matchplayers = current_match.matchmaked_players
    n = len(matchplayers)
    n12 = math.ceil(n/2) #must use ceil to separate teams
    team1 = matchplayers[0:n12]
    team2 = matchplayers[n12:]
    players = Player.query.all()

    # ingame = Player.query.with_parent(current_match).all()
    

    return render_template("index.html", Players=players, Team1=team1,Team2=team2, Matchobj=current_match)

@app.route("/matchsumary",methods=["POST"])
def matchsumary():
    # FIXME this is not yet done
    """Update match information and show summary."""
    current_match = Match.query.order_by(Match.id.desc()).first()
    if request.form.get("direvictory"):
        current_match.winning_team=0
        current_match.update_matchmaked_players()
    if request.form.get("radiantvictory"):
        current_match.winning_team=1
        current_match.update_matchmaked_players()
        
    matches = Match.query.all()
    return render_template("flights.html", flights=flights)



@app.route("/book", methods=["POST"])
def book():
    """Book a flight."""

    # Get form information.
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")

    # Make sure the flight exists.
    flight = Flight.query.get(flight_id)
    if not flight:
        return render_template("error.html", message="No such flight with that id.")

    # Add passenger.
    flight.add_passenger(name)
    return render_template("success.html")


@app.route("/flights")
def flights():
    """List all flights."""
    flights = Flight.query.all()
    return render_template("flights.html", flights=flights)


@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    """List details about a single flight."""

    # Make sure flight exists.
    flight = Flight.query.get(flight_id)
    if flight is None:
        return render_template("error.html", message="No such flight.")

    # Get all passengers.
    passengers = flight.passengers
    return render_template("flight.html", flight=flight, passengers=passengers)


@app.route("/api/flights/<int:flight_id>")
def flight_api(flight_id):
    """Return details about a single flight."""

    # Make sure flight exists.
    flight = Flight.query.get(flight_id)
    if flight is None:
        return jsonify({"error": "Invalid flight_id"}), 422

    # Get all passengers.
    passengers = flight.passengers
    names = []
    for passenger in passengers:
        names.append(passenger.name)
    return jsonify({
        "origin": flight.origin,
        "destination": flight.destination,
        "duration": flight.duration,
        "passengers": names
    })


if __name__ == "__main__":
    app.run(debug=True,use_reloader=False,host='0.0.0.0')
    # app.run()