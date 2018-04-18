from db import *


class Player(db.Model):
    __tablename__ = 'Player'
    idPlayer = db.Column(db.Integer, primary_key=True)
    pseudonyme = db.Column(db.String(45), nullable=False)
    Team_idTeam = db.Column(db.Integer, db.ForeignKey(
        'Team.idTeam'), nullable=True)

    def __repr__(self):
        return '<Player {}>'.format(self.username)

    def __init__(self, pseudonyme, idTeam=False):
        self.pseudonyme = pseudonyme
        self.idTeam = idTeam


class PlayerSchema(ma.Schema):

    class Meta:
        fields = ('idPlayer', 'pseudonyme', 'Team_idTeam')


player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


class Team(db.Model):
    __tablename__ = 'Team'
    idTeam = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=True)
    iconUrl = db.Column(db.String(45), nullable=False)
    ColorRGB = db.Column(db.String(45), nullable=False)
    Game_idGame = db.Column(db.Integer, db.ForeignKey(
        'Game.idGame'), nullable=False)
    lives = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Team {}>'.format(self.name)

    def __init__(self, name, iconURL, ColorRGB, Game_idGame, lives, score):
        self.name = name
        self.iconUrl = iconURL
        self.ColorRGB = ColorRGB
        self.lives = lives
        self.Game_idGame = Game_idGame
        self.score = score


class TeamSchema(ma.Schema):

    class Meta:
        fields = ('idTeam', 'name', 'iconUrl', 'ColorRGB',
                  'Game_idGame', 'lives', 'score')


team_schema = TeamSchema()
teams_schema = TeamSchema(many=True)


class Beacon(db.Model):
    __tablename__ = 'Beacon'
    idBeacon = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    iconUrl = db.Column(db.String(45), nullable=False)
    Riddle_idRiddle = db.Column(db.Integer, db.ForeignKey(
        'Riddle.idRiddle'), nullable=False)
    qrCodeID = db.Column(db.String(64), nullable=True)
    trip = db.relationship("Beacon_has_Trip", back_populates="beacon")

    def __repr__(self):
        return '<Beacon {}>'.format(self.name)


class BeaconSchema(ma.Schema):

    class Meta:
        fields = ('idBeacon', 'name', 'latitude', 'longitude',
                  'iconUrl', 'Riddle_idRiddle', 'qrCodeID', 'trip')


beacon_schema = BeaconSchema()
beacons_schema = BeaconSchema(many=True)


class Trip(db.Model):
    __tablename__ = 'Trip'
    idTrip = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Float, nullable=True)
    heighDifference = db.Column(db.Float, nullable=False)
    Team_idTeam = db.Column(db.Integer, db.ForeignKey(
        'Team.idTeam'), nullable=False)
    beacon = db.relationship("Beacon_has_Trip", back_populates="trip")

    def __repr__(self):
        return '<Trip {}>'.format(self.idTrip)


class TripSchema(ma.Schema):

    class Meta:
        model = Trip


trip_schema = TripSchema()
trips_schema = TripSchema(many=True)


class Beacon_has_Trip(db.Model):
    __tablename__ = 'Beacon_has_Trip'
    Beacon_idBeacon = db.Column(db.Integer, db.ForeignKey(
        'Beacon.idBeacon'), nullable=False, primary_key=True)
    Trip_idTrip = db.Column(db.Integer, db.ForeignKey(
        'Trip.idTrip'), nullable=False, primary_key=True)
    index = db.Column(db.Integer, nullable=False)
    trip = db.relationship("Trip", back_populates="beacon")
    beacon = db.relationship("Beacon", back_populates="trip")

    def __repr__(self):
        return '<Beacon_has_Trip {}>'.format(self.index)


class Beacon_has_TripSchema(ma.Schema):

    class Meta:
        model = Beacon_has_Trip


beacon_has_trip_schema = Beacon_has_TripSchema()
beacon_has_trips_schema = Beacon_has_TripSchema(many=True)


class Riddle(db.Model):
    __tablename__ = 'Riddle'
    idRiddle = db.Column(db.Integer, primary_key=True)
    statement = db.Column(db.String(45), nullable=False)
    answer = db.Column(db.String(45), nullable=False)
    type = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Riddle {}>'.format(self.idRiddle)


class RiddleSchema(ma.Schema):

    class Meta:
        model = Riddle


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
        self.mapViewEnable = mapViewEnable
        self.timerRiddle = timerRiddle
        self.lives = lives
        self.enableNextBeaconVisibility = enableNextBeaconVisibility


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
    joinCode = db.Column(db.String(45), nullable=False)
    gmCode = db.Column(db.String(45), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    isStarted = db.Column(db.Boolean, nullable=False)
    Settings_idSettings = db.Column(db.Integer, db.ForeignKey(
        'Settings.idSettings'), nullable=True)

    def __repr__(self):
        return '<Game {}>'.format(self.name)

    def __init__(self, name, idGame, joinCode, type, isStarted, Settings_idSettings):
        self.name = name
        self.idGame = idGame
        self.joinCode = joinCode
        self.type = type
        self.isStarted = isStarted
        self.Settings_idSettings


class GameSchema(ma.Schema):

    class Meta:
        fields = ('idGame', 'name', 'joinCode', 'gmCode',
                  'type', 'isStarted', 'Settings_idSettings')


game_schema = GameSchema()
games_schema = GameSchema(many=True)

db.create_all()
