import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import math
db = SQLAlchemy()



players_to_matches = db.Table('players_to_matches',
                    db.Column('id', db.Integer, primary_key=True,
                              autoincrement=True),
                    db.Column('player_id', db.Integer, db.ForeignKey(
                        'players.id'), primary_key=True),
                    db.Column('match_id', db.Integer, db.ForeignKey(
                        'matches.id'), primary_key=True),
                    db.Column('mmr', db.Integer, nullable=True,primary_key=False),
                    db.Column('team', db.Boolean, nullable=True,primary_key=False)
                    )

# class players_to_matches(db.Model):
#     __tablename__ = "players_to_matches"
#     id = db.Column(db.Integer,primary_key=True, autoincrement=True)
#     player_id = db.Column(db.Integer, db.ForeignKey('players.id'), primary_key=True)
#     match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
#     mmr = db.Column(db.Integer, nullable=True)

class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    winning_team = db.Column(db.Boolean, nullable=True)
    players = db.relationship('Player', secondary=players_to_matches, backref=db.backref(
        'matches', lazy=True), lazy='subquery')
    matchmaked_players = []

    def update_matchmaked_players(self):
        self.matchmaked_players = self.players

    def clear_all_players(self):
        self.players = []
        self.matchmaked_players = self.players
        db.session.add(self)
        db.session.commit()
        
    def delete_player(self,name):
        p = Player.query.filter_by(name=name).first()
        if p is not None:
            try:
                index = self.players.index(p)
                self.players.pop(index)
                self.matchmaked_players = self.players
                db.session.add(self)
            except:
                pass
            db.session.delete(p)
            db.session.commit()

    def add_player(self, name):
        # Add only existing player
        p = Player.query.filter_by(name=name).first()
        if p is not None:
            self.players.append(p)
            db.session.add(self)
            db.session.commit()
            # Remove first player on list if more than 10
            if len(self.players)>10:
                del self.players[0]
                db.session.add(self)
                db.session.commit()
        self.matchmaked_players = self.players
    
    def avg_mmr(self,team=0):
            top = len(self.matchmaked_players)
            bottom = team*math.ceil((top/2))
            if bottom>=top:
                return 0
            if team==0 and top>(top/2):
                top = math.ceil((top/2))
            suma=0
            for idx in range(bottom,top):
                suma = suma + self.matchmaked_players[idx].mmr
            return suma/(top-bottom)

    
    def get_players_tuples(self):
        jugadores = []
        for player in self.matchmaked_players:
            jugadores.append((player.name,player.mmr))
        return jugadores
    
    def update_teams(self,jugadores):
        # self.players = []
        # db.session.add(self)
        # db.session.commit()
        matchid = self.id
        self.matchmaked_players = []
        for idx,jugador in enumerate(jugadores):
            p = Player.query.filter_by(name=jugador).first()
            self.matchmaked_players.append(p)
            playerid = p.id
        #     if idx>=5:
        #         db.session.execute("UPDATE players_to_matches SET team=True WHERE match_id=:matchid AND player_id=:playerid",{"matchid":matchid,"playerid":playerid})
        #     else:
        #         db.session.execute("UPDATE players_to_matches SET team=False WHERE match_id=:matchid AND player_id=:playerid",{"matchid":matchid,"playerid":playerid})
        # db.session.commit()

class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    mmr = db.Column(db.Integer, nullable=True)

    def delete_player(self):
        db.session.delete(self)
        db.session.commit()

    def has_parent(self,match):
        players_in_match = Player.query.with_parent(match).all()
        return self in players_in_match
        

    @staticmethod
    def add_player(name,mmr):
        player = Player.query.filter_by(name=name).first()
        if player is not None:
            player.mmr = mmr
        else:
            player = Player(name=name,mmr=mmr)
            db.session.add(player)
            db.session.commit()

        

