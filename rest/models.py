# -*- coding: utf-8 -*-
from db import *
from flask_restplus import inputs


class Player(db.Model):
    __tablename__ = 'Player'
    idPlayer = db.Column(db.Integer, primary_key=True)
    pseudonyme = db.Column(db.String(45), nullable=False)
    token = db.Column(db.String(256), nullable=False)
    Team_idTeam = db.Column(db.Integer, db.ForeignKey(
        'Team.idTeam'), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return self.pseudonyme

    def __init__(self, pseudonyme, longitude,token, latitude, idTeam=False):
        self.pseudonyme = pseudonyme
        self.Team_idTeam = idTeam
        self.token = token
        self.longitude = longitude
        self.latitude = latitude


class PlayerSchema(ma.Schema):

    class Meta:
        fields = ('idPlayer', 'pseudonyme', 'Team_idTeam', 'token')


player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


class Team(db.Model):
    __tablename__ = 'Team'
    idTeam = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=True)
    iconUrl = db.Column(db.String(45), nullable=True)
    ColorHex = db.Column(db.String(45), nullable=False)
    Game_idGame = db.Column(db.Integer, db.ForeignKey(
        'Game.idGame'), nullable=True)
    lives = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=True)
    Checkpoint = db.Column(db.Integer, nullable=False)
    players = db.relationship('Player',backref='team',lazy=False)

    def __repr__(self):
        return '<Team {}>'.format(self.name)

    def __init__(self, name, iconURL, ColorHex, lives, score, Checkpoint):
        self.name = name
        self.iconUrl = iconURL
        self.ColorHex = ColorHex
        self.lives = lives
        self.score = score
        self.Checkpoint = Checkpoint


class TeamSchema(ma.Schema):

    class Meta:
        fields = ('idTeam', 'name', 'iconUrl', 'ColorHex',
                  'Game_idGame', 'lives', 'score', 'Checkpoint')


team_schema = TeamSchema()
teams_schema = TeamSchema(many=True)


Beacon_has_Trip = db.Table('Beacon_has_Trip',
                           db.Column('Beacon_idBeacon', db.Integer, db.ForeignKey(
                               'Beacon.idBeacon'), primary_key=True),
                           db.Column('Trip_idTrip', db.Integer, db.ForeignKey(
                               'Trip.idTrip'), primary_key=True)
                           )


class Trip(db.Model):
    __tablename__ = 'Trip'
    idTrip = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=True)
    distance = db.Column(db.Float, nullable=True)
    heighDifference = db.Column(db.Float, nullable=False)
    Team_idTeam = db.Column(db.Integer, db.ForeignKey(
        'Team.idTeam'), nullable=False)

    def __repr__(self):
        return '<Trip {}>'.format(self.idTrip)

    def __init__(self, name, distance, heighDifference, Team_idTeam):
        self.name = name
        self.distance = distance
        self.heighDifference = heighDifference
        self.Team_idTeam = Team_idTeam


class TripSchema(ma.Schema):

    class Meta:
        fields = ('idTrip','name','distance','heighDifference','Team_idTeam')


trip_schema = TripSchema()
trips_schema = TripSchema(many=True)


class Beacon(db.Model):
    __tablename__ = 'Beacon'
    idBeacon = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    iconUrl = db.Column(db.String(45), nullable=True)
    Riddle_idRiddle = db.Column(db.Integer, db.ForeignKey(
        'Riddle.idRiddle'), nullable=True)
    qrCodeID = db.Column(db.String(64), nullable=True)
    trips = db.relationship(
        'Trip', secondary=Beacon_has_Trip, backref=db.backref('beacons',lazy=False))

    def __repr__(self):
        return '<Beacon {}>'.format(self.name)

    def __init__(self, name, latitude, longitude, iconUrl, qrCodeID):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.iconUrl = iconUrl
        self.qrCodeID = qrCodeID


class BeaconSchema(ma.Schema):

    class Meta:
        fields = ('idBeacon', 'name', 'latitude', 'longitude',
                  'iconUrl', 'Riddle_idRiddle', 'qrCodeID')


beacon_schema = BeaconSchema()
beacons_schema = BeaconSchema(many=True)


class Riddle(db.Model):
    __tablename__ = 'Riddle'
    idRiddle = db.Column(db.Integer, primary_key=True)
    statement = db.Column(db.String(45), nullable=False)
    answer = db.Column(db.String(45), nullable=False)
    GameMode = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Riddle {}>'.format(self.idRiddle)

    def __init__(self, statement, answer, GameMode):
        self.statement = statement
        self.answer = answer
        self.GameMode = GameMode

class RiddleSchema(ma.Schema):

    class Meta:
        fields = ('statement','answer','GameMode')


riddle_schema = RiddleSchema()
riddles_schema = RiddleSchema(many=True)


class Settings(db.Model):
    __tablename__ = 'Settings'
    idSettings = db.Column(db.Integer, primary_key=True)
    tresholdShrink = db.Column(db.Integer, nullable=True)
    mapViewEnable = db.Column(db.Boolean, nullable=False)
    timerRiddle = db.Column(db.Integer, nullable=False)
    lives = db.Column(db.Integer, nullable=True)
    enableNextBeaconVisibility = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Settings {}>'.format(self.idSettings)

    def __init__(self, tresholdShrink, mapViewEnable, timerRiddle, lives, enableNextBeaconVisibility):
        self.tresholdShrink = tresholdShrink
        self.mapViewEnable = inputs.boolean(mapViewEnable)
        self.timerRiddle = timerRiddle
        self.lives = lives
        self.enableNextBeaconVisibility = inputs.boolean(
            enableNextBeaconVisibility)


class SettingsSchema(ma.Schema):

    class Meta:
        fields = ('idSettings', 'tresholdShrink', 'mapViewEnable',
                  'timerRiddle', 'lives', 'enableNextBeaconVisibility')


setting_schema = SettingsSchema()
settings_schema = SettingsSchema(many=True)


class Email(db.Model):
    __tablename__ = 'Email'
    email = db.Column(db.String(50), primary_key=True)
    firstname = db.Column(db.String(45), nullable=True)
    lastname = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return '<Email {}>'.format(self.idSettings)


class EmailSchema(ma.Schema):

    class Meta:
        model = Email


email_schema = EmailSchema()
emails_schema = EmailSchema(many=True)


class Game(db.Model):
    __tablename__ = 'Game'
    idGame = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=True)
    GameMode = db.Column(db.Integer, nullable=False)
    isStarted = db.Column(db.Boolean, nullable=False)
    Settings_idSettings = db.Column(db.Integer, db.ForeignKey(
        'Settings.idSettings'), nullable=True)
    PlayerCode = db.Column(db.String(45), nullable=False)
    GameMasterCode = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return '<Game {}>'.format(self.name)

    def __init__(self, name, GameMode, isStarted, Settings_idSettings, GameMasterCode, PlayerCode):
        self.name = name
        self.isStarted = inputs.boolean(isStarted)
        self.Settings_idSettings
        self.GameMasterCode = GameMasterCode
        self.PlayerCode = PlayerCode
        self.GameMode = GameMode


class GameSchema(ma.Schema):

    class Meta:
        fields = ('idGame', 'name', 'joinCode', 'gmCode',
                  'type', 'isStarted', 'Settings_idSettings', 'PlayerCode', 'GameMasterCode')


game_schema = GameSchema()
games_schema = GameSchema(many=True)

db.create_all()
