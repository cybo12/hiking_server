# -*- coding: utf-8 -*-
from models import *
from db import *
from flask import render_template, make_response, request, jsonify, send_file
# from sqlalchemy.exc import exc
import random
import string
import json
import base64
import os
from objdict import ObjDict
import requests
import datetime

app.config['JSON_AS_ASCII'] = False


@app.route("/players", methods=["GET"])
def get_player():
    all_players = Player.query.all()
    return players_schema.jsonify(all_players)


@app.route("/games", methods=["GET"])
def get_games():
    all_games = Game.query.all()
    return games_schema.jsonify(all_games)


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['Error'] = error
    return resp


def Shrink(idGame):
    test = 0
    game = Game.query.get(idGame)
    settings = Settings.query.get(game.Settings_idSettings)


#####################
###################
@app.route("/upload", methods=["POST"])
def upload():
    randomisation = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(9))
    randomisation += ".png"
    print request.get_data()
    image = open(randomisation, "wb")
    image.write(base64.b64decode(request.get_data()))
    image.close()
    command = "mv {} images/".format(randomisation)
    os.popen(command)
    return "https://hikong.masi-henallux.be:5000/image/{}".format(randomisation)


@app.route("/image/<name>", methods=["GET"])
def image(name):
    print name
    path = "images/{}".format(name)
    return send_file(path, mimetype='image/png')


@app.route("/joingame", methods=["POST"])
def joingame():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    if check_adm(json_handle['code']):
        game = Game.query.filter_by(GameMasterCode=json_handle['code']).first()
        settings = Settings.query.get(game.Settings_idSettings)
        teams = Team.query.filter_by(Game_idGame=game.idGame).all()
        data = ObjDict()
        data.game = json.loads(game_schema.jsonify(game).data)
        data.settings = json.loads(setting_schema.jsonify(settings).data)
        data.teams = []
        data.admin = True
        for team in teams:
            test = json.loads(team_schema.jsonify(team).data)
            trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
            beacons = trip.beacons
            test['trip'] = json.loads(trip_schema.jsonify(trip).data)
            test['trip']['beacons'] = []
            for beacon in beacons:
                riddle = Riddle.query.filter_by(
                    idRiddle=beacon.Riddle_idRiddle).first()
                ensemble = json.loads(beacon_schema.jsonify(beacon).data)
                ensemble['Riddle'] = json.loads(
                    riddle_schema.jsonify(riddle).data)
                test['trip']['beacons'].append(ensemble)
            data.teams.append(test)
        ret = data.dumps()
        reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    elif Game.query.filter_by(PlayerCode=json_handle['code']).first():
        game = Game.query.filter_by(PlayerCode=json_handle['code']).first()
        settings = Settings.query.filter_by(
            idSettings=game.Settings_idSettings).first()
        response = ObjDict()
        response.admin = False
        response['game'] = json.loads(game_schema.jsonify(game).data)
        response['settings'] = json.loads(
            setting_schema.jsonify(settings).data)
        ret = response.dumps()
        reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    else:
        reponse = make_response("code invalide", 410)
    return reponse


@app.route("/jointeam", methods=["POST"])
def add_player_team():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    ret = "False"
    if Player.query.filter_by(pseudonyme=json_handle['pseudonyme']).first() is None:
        game = Game.query.filter_by(
            PlayerCode=json_handle['playercode']).first()
        team = Team.query.filter_by(
            Game_idGame=game.idGame, name=json_handle['name']).first()
        me = Player(pseudonyme=json_handle['pseudonyme'],
                    idTeam=team.idTeam, token=json_handle['token'], latitude=json_handle['latitude'], longitude=json_handle['longitude'])
        db.session.add(me)
        db.session.commit()
        team = Team.query.get(team.idTeam)
        ret = team_schema.jsonify(team)
        reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    else:
        reponse = make_response("pseudo déjà prit", 410)
    return reponse


@app.route("/game", methods=["POST"])
def add_game():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    code_player = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(6))
    code_admin = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(6))
    teams = []
    for x in json_handle['teams']:
        team = Team(lives=json_handle['lives'], name=x[
                    'name'], Checkpoint=0, score=0, iconURL=x['iconURL'], ColorHex=x['colorHex'])
        db.session.add(team)
        db.session.commit()
        teams.append(team)
        trip = Trip(name=x['trip']['name'], distance=x['trip']['distance'], heighDifference=x[
                    'trip']['heighDifference'], Team_idTeam=team.idTeam)
        db.session.add(trip)
        db.session.commit()
        for z in x['trip']['beacons']:
            beacon = Beacon(name=z['name'], latitude=z['latitude'], longitude=z[
                            'longitude'], iconUrl=z['iconURL'], qrCodeID=z['qrCodeID'])
            riddle = Riddle(statement=z['riddle']['statement'], answer=z[
                            'riddle']['statement'], GameMode=json_handle['gameMode'])
            db.session.add(riddle)
            db.session.commit()
            trip.beacons.append(beacon)
            beacon.Riddle_idRiddle = riddle.idRiddle
            db.session.add(beacon)
            db.session.commit()
    settings = Settings(tresholdShrink=json_handle['tresholdShrink'],
                        mapViewEnable=json_handle['mapViewEnable'],
                        timerRiddle=json_handle['timerRiddle'],
                        lives=json_handle['lives'],
                        enableNextBeaconVisibility=json_handle['enableNextBeaconVisibility'])
    db.session.add(settings)
    db.session.commit()
    game = Game(name="test", PlayerCode=code_player,
                GameMasterCode=code_admin, GameMode=json_handle['gameMode'],
                Settings_idSettings=settings.idSettings, isStarted=False, gameStartedTime=datetime.datetime.now())
    db.session.add(settings)
    game.Settings_idSettings = settings.idSettings
    db.session.add(game)
    db.session.commit()
    for x in teams:
        x.Game_idGame = game.idGame
    db.session.commit()
    ret = {'PlayerCode': code_player, 'GameMasterCode': code_admin}
    ret = jsonify(ret)
    reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    return reponse


@app.route("/confirmpoint", methods=["POST"])
def confirmPoint():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    team = Team.query.filter_by(name=json_handle['name']).first()
    team.lives = json_handle['lives']
    trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
    if json_handle['lives'] == 0:
        nb = len(trip.beacons) - 1
        ret = getPoint(trip.idTrip, nb)
    else:
        team.Checkpoint += 1
        db.session.commit()
        if team.Checkpoint <= len(trip.beacons):
            ret = getPoint(trip.idTrip, team.Checkpoint)
        else:
            reponse = "False"
    reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    db.session.commit()
    return reponse


def getPoint(idTrip, Checkpoint):
    trip = Trip.query.get(idTrip)
    riddle = Riddle.query.get(trip.beacons[Checkpoint].Riddle_idRiddle)
    test = Checkpoint + 1
    check = (test == len(trip.beacons))
    beacon = trip.beacons[Checkpoint]
    ret = ObjDict()
    ret['latitude'] = beacon.latitude
    ret['longitude'] = beacon.longitude
    ret['statement'] = riddle.statement
    ret['answer'] = riddle.answer
    ret['name'] = beacon.name
    ret['iconURL'] = beacon.iconUrl
    ret['lastBeacon'] = check
    ret = jsonify(ret)
    reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    return reponse


@app.route("/firstpoint", methods=["POST"])
def firstpoint(idTeam):
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    team = Team.query.filter_by(name=json_handle['name']).first()
    trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
    ret = getPoint(trip.idTrip, 0)
    reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    return reponse


@app.route("/refreshpos", methods=["PUT"])
def refreshpos():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    player = Player.query.filter_by(pseudonyme=json_handle['pseudonyme'])
    player.latitude = json_handle['latitude']
    player.longitude = json_handle['longitude']
    return "True"


@app.route("/<playercode>/teams", methods=["GET"])
def teams(playercode):
    if Game.query.filter_by(PlayerCode=playercode).first():
        game = Game.query.filter_by(PlayerCode=playercode).first()
        teams = Team.query.filter_by(Game_idGame=game.idGame).all()
        ret = teams_schema.jsonify(teams)
        reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    else:
        reponse = make_response("Code invalide!", 410)
    return reponse


@app.route("/<GameMasterCode>/getTeamsStats", methods=["GET"])
def getTeamsStats(GameMasterCode):
    if check_adm(GameMasterCode):
        game = Game.query.filter_by(GameMasterCode=json_handle['code']).first()
        teams = Team.query.filter_by(Game_idGame=game.idGame).all()
        data = ObjDict()
        data['teams'] = []
        for team in teams:
            ind = 0
            players = team.players
            ensemble = json.loads(team_schema.jsonify(team).data)
            ensemble['players'] = []
            if len(players) != 0:
                ensemble['players'].append(json.loads(
                    players_schema.jsonify(players).data))
                data['teams'].append(ensemble)
        ret = data.dumps()
    else:
        ret = "False"
    reponse = make_response(ret, 200, {'Content-Type': "application/json"})
    return reponse


@app.route("/<GameMasterCode>/BattleReady", methods=["GET"])
def BattleReady(GameMasterCode):
    if check_adm(GameMasterCode):
        Teams = Team.query.filter_by(
            GameMasterCode=GameMasterCode).all()
        for team in teams:
            players = team.players
            for player in players:
                headers = {'Authorization': 'key={AAAAwixAe04:APA91bEhaFFRoy9VpP7n2w9WjyaahFuRZCC_VPtHEo6DMrnN_gGVhMX-e9M6u0V_Kj9J7TKSlLiHRt2K6QhIgixHmJAwrVCR74WfsX-52QsWAA2jSEcip10JPahXgwced4Ep5H5V6l57}',
                           'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
                payload = {
                    "to": "\{{}\}".format(player.token),
                    "notification": {
                        "body": "startGameNow",
                        "title": "The game has started !"
                    }
                }
                print payload
                r = requests.POST(
                    'https://fcm.googleapis.com/fcm/send', payload=payload, headers=headers)
                print r
    reponse = make_response(True, 200)
    return reponse


def check_adm(code):
    if Game.query.filter_by(GameMasterCode=code).first():
        return True
    else:
        return False


if __name__ == "__main__":
    app.run(debug=True,
            ssl_context=(
                '/etc/letsencrypt/live/hikong.masi-henallux.be/fullchain.pem',
                '/etc/letsencrypt/live/hikong.masi-henallux.be/privkey.pem'),
            host='0.0.0.0')
