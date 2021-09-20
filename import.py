import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("players.csv")
    reader = csv.reader(f)
    db.execute("DELETE FROM players")
    db.execute("DELETE FROM matches")
    db.execute("DELETE FROM players_to_matches")
    for name, mmr in reader:
        db.execute("INSERT INTO players (name, mmr) VALUES (:name, :mmr)",
                    {"name": name, "mmr": mmr})
        print(f"Added player {name} with mmr {mmr}.")
    # f = open("players_to_matches.csv")
    # reader = csv.reader(f)
    # for id, player_id, match_id in reader:
    #     db.execute("INSERT INTO players_to_matches (player_id, match_id) VALUES (:player_id, :match_id)",
    #                 {"player_id": player_id, "match_id": match_id})
    db.commit()

if __name__ == "__main__":
    main()
