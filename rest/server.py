# -*- coding: utf-8 -*-
from models import *
from db import *
from flask import render_template, make_response, request, jsonify, send_file
from math import sin, cos, sqrt, atan2, radians
from geojson import GeometryCollection, Point, LineString, MultiLineString
import geojson
import random
import string
import json
import base64
import os
from objdict import ObjDict
import requests
import datetime
import qrcode

app.config['JSON_AS_ASCII'] = False

# get all players


@app.route("/players", methods=["GET"])
def get_player():
    all_players = Player.query.all()
    return players_schema.jsonify(all_players)

# get all games


@app.route("/games", methods=["GET"])
def get_games():
    game = Game.query.all()
    return games_schema.jsonify(game)


@app.route("/games/<playercode>", methods=["GET"])
def get_game(playercode):
    game = Game.query.filter_by(PlayerCode=playercode).first()
    team = Team.query.filter_by(Game_idGame=game.idGame).first_or_404()
    trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
    print trip.beacons
    for x in trip.beacons:
        print x.trips
    return game_schema.jsonify(game)

# get GeoJson of the game


@app.route("/map/<id_g>", methods=["GET"])
def map(id_g):
    game = Game.query.get(id_g)
    settings = Settings.query.get(game.Settings_idSettings)
    teams = Team.query.filter_by(Game_idGame=game.idGame).all()
    beacons_get = []
    beacons = []
    collection = []
    for team in teams:
        if Trip.query.filter_by(Team_idTeam=team.idTeam).first():
            trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
            beacons_get.append(trip.beacons)
            my_line = []
        for x in beacons_get:
            beacons += x
        for x in beacons:
            my_line.append((x.longitude, x.latitude))
        collection.append(my_line)
    geo_collection = MultiLineString(collection)
    response = geojson.dumps(geo_collection)
    rett = make_response(response, 200)
    return rett

# error Handler


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['Error'] = error
    return resp

# Calculate the boundary and center of shrink for Settings


def shrink(idGame):
    game = Game.query.get(idGame)
    settings = Settings.query.get(game.Settings_idSettings)
    teams = Team.query.filter_by(Game_idGame=game.idGame).all()
    beacons_get = []
    beacons = []
    for team in teams:
        if Trip.query.filter_by(Team_idTeam=team.idTeam).first():
            trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
            beacons_get.append(trip.beacons)
    for x in beacons_get:
        beacons += x
    center = beacons[-1]
    settings.center_x = center.latitude
    settings.center_y = center.longitude
    Nord = center.longitude
    Est = center.latitude
    Ouest = center.latitude
    Sud = center.longitude
    for beacon in beacons:  # OUEST latitude moins   NORD longitude plus
        if beacon.latitude < Ouest:
            Ouest = beacon.latitude
        elif beacon.latitude > Est:
            Est = beacon.latitude
        elif beacon.longitude < Nord:
            Nord = beacon.longitude
        elif beacon.longitude > Sud:
            Sud = beacon.longitude
    # approximate radius of earth in km

    R = 6373.0
    lat1 = radians(Sud)
    lon1 = radians(Est)
    lat2 = radians(Nord)
    lon2 = radians(Ouest)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    # diamètre en KM ramené au rayon en mètres + 10%
    settings.radius = (distance * 0.55) * 1000
    db.session.commit()


# upload a picture and return the link for her


@app.route("/upload", methods=["POST"])
def upload():
    randomisation = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(9))
    randomisation += ".png"
    image = open(randomisation, "wb")
    image.write(base64.b64decode(request.get_data()))
    image.close()
    command = "mv {} images/".format(randomisation)
    os.popen(command)
    return "https://hikong.masi-henallux.be:5000/image/{}".format(randomisation)

# getter for images


@app.route("/image/<name>", methods=["GET"])
def image(name):
    print name
    path = "images/{}".format(name)
    return send_file(path, mimetype='image/png')

# join the game and returns data for admin and player


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
                ensemble = json.loads(beacon_schema.jsonify(beacon).data)
                if(game.GameMode != 1):
                    riddle = Riddle.query.filter_by(
                        idRiddle=beacon.Riddle_idRiddle).first()
                    ensemble['Riddle'] = json.loads(
                        riddle_schema.jsonify(riddle).data)
                test['trip']['beacons'].append(ensemble)
            data.teams.append(test)
        ret = data.dumps()
        response = make_response(
            ret, 200, {'Content-Type': "application/json"})
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
        response = make_response(
            ret, 200, {'Content-Type': "application/json"})
    else:
        response = make_response("code invalide", 403)
    return response

# joining a team an give team parameter


@app.route("/jointeam", methods=["POST"])
def add_player_team():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    ret = "False"
    if Game.query.filter_by(PlayerCode=json_handle['playercode']).first():
        game = Game.query.filter_by(
            PlayerCode=json_handle['playercode']).first()
        if Team.query.filter_by(Game_idGame=game.idGame, name=json_handle['name']).first():
            team = Team.query.filter_by(
                Game_idGame=game.idGame, name=json_handle['name']).first()
            if Player.query.filter_by(pseudonyme=json_handle['pseudonyme'], Team_idTeam=team.idTeam).first() is None:
                me = Player(pseudonyme=json_handle['pseudonyme'],
                            idTeam=team.idTeam, token=json_handle['token'], latitude=json_handle['latitude'], longitude=json_handle['longitude'])
                db.session.add(me)
                db.session.commit()
                team = Team.query.get(team.idTeam)
                ret = team_schema.jsonify(team)
                response = make_response(
                    ret, 200, {'Content-Type': "application/json"})
            else:
                response = make_response("pseudo déjà pris", 403)
        else:
            response = make_response("la team n'existe pas", 403)
    else:
        response = make_response("la game n'existe pas", 403)
    return response

# create the game with all parameter given and return player's and admin's
# codes


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
        index = 0
        for z in x['trip']['beacons']:
            beacon = Beacon(name=z['name'], latitude=z['latitude'], longitude=z[
                            'longitude'], iconUrl=z['iconURL'], qrCodeID=z['qrCodeID'])
            if(json_handle['gameMode'] != 1):
                riddle = Riddle(statement=z['riddle']['statement'], answer=z[
                    'riddle']['answer'], GameMode=json_handle['gameMode'])
                db.session.add(riddle)
                db.session.commit()
                trip.beacons.append(beacon)
                beacon.Riddle_idRiddle = riddle.idRiddle
            else:
                trip.beacons.append(beacon)
            db.session.add(beacon)
            db.session.commit()
            query = Beacon_has_Trip.update().where(Beacon_has_Trip.c.Trip_idTrip == trip.idTrip).where(
                Beacon_has_Trip.c.Beacon_idBeacon == beacon.idBeacon).values(ind=index)
            db.session.execute(query)
            print query
            print c
            index += 1
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
    shrink(game.idGame)
    db.session.commit()
    ret = {'PlayerCode': code_player, 'GameMasterCode': code_admin}
    ret = jsonify(ret)
    response = make_response(ret, 200, {'Content-Type': "application/json"})
    return response

# confirm point by a player and show him the next


@app.route("/confirmpoint", methods=["POST"])
def confirmPoint():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    ret = getTrip(json_handle['playercode'], json_handle['nameTeam'])
    if isinstance(ret, int):
        trip = Trip.query.get(ret)
        game = Game.query.filter_by(
            PlayerCode=json_handle['playercode']).first()
        team = Team.query.filter_by(
            name=json_handle['nameTeam'], Game_idGame=game.idGame).first()
        team.lives = json_handle['lives']
        if json_handle['lives'] == 0:
            team.Checkpoint = len(trip.beacons) - 1
            payload = getPoint(trip.idTrip, team.Checkpoint)
        else:
            team.Checkpoint += 1
            db.session.commit()
            if team.Checkpoint <= len(trip.beacons):
                payload = getPoint(trip.idTrip, team.Checkpoint)
        db.session.commit()
        players = Player.query.filter_by(Team_idTeam=team.idTeam).all()
        for p in players:
            print p.pseudonyme
            if p.token is None:
                if(p.pseudonyme != json_handle['namePlayer']):
                    data = dict()
                    data['confirmPoint'] = "true"
                    data['lives'] = team.lives
                    r = firebase(p.idPlayer, data)
                    print r.content
        response = make_response(
            payload, 200, {'Content-Type': "application/json"})
        db.session.commit()
    else:
        response = ret
    return response

# request for launch message from Firebase


def firebase(idplayer, data):
    player = Player.query.get(idplayer)
    headers = {'Authorization': 'key=AAAAwixAe04:APA91bEhaFFRoy9VpP7n2w9WjyaahFuRZCC_VPtHEo6DMrnN_gGVhMX-e9M6u0V_Kj9J7TKSlLiHRt2K6QhIgixHmJAwrVCR74WfsX-52QsWAA2jSEcip10JPahXgwced4Ep5H5V6l57',
               'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
    payload = ObjDict()
    payload.to = player.token
    payload.notification = {
        "body": "hello", "title": "Point confirmed !"}
    payload.data = data
    payload = json.dumps(payload)
    r = requests.post(
        'https://fcm.googleapis.com/fcm/send', data=payload, headers=headers)
    return r


# return the lastpoint
@app.route("/lastpoint", methods=['POST'])
def lastpoint():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    ret = getTrip(json_handle['playercode'], json_handle['nameTeam'])
    if isinstance(ret, int):
        trip = Trip.query.get(ret)
        ind = len(trip.beacons) - 1
        payload = getPoint(trip.idTrip, ind)
        response = make_response(
            payload, 200, {'Content-Type': "application/json"})
    else:
        response = ret
    return response


def getTrip(playercode, nameTeam):
    game = Game.query.filter_by(PlayerCode=playercode).first()
    if game:
        team = Team.query.filter_by(
            name=nameTeam, Game_idGame=game.idGame).first()
        if team:
            trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
            response = trip.idTrip
        else:
            response = make_response("la team n'existe pas", 403)
    else:
        response = make_response("la game n'existe pas", 403)
    return response
# get only the essential data for players including Beacon and Riddle


def getPoint(idTrip, Checkpoint):
    trip = Trip.query.get(idTrip)
    riddle = Riddle.query.get(trip.beacons[Checkpoint].Riddle_idRiddle)
    test = Checkpoint + 1
    check = (test == len(trip.beacons))
    beacon = trip.beacons[Checkpoint]
    ret = ObjDict()
    ret['idBeacon'] = beacon.idBeacon
    ret['latitude'] = beacon.latitude
    ret['longitude'] = beacon.longitude
    ret['name'] = beacon.name
    ret['iconURL'] = beacon.iconUrl
    ret['qrCodeID'] = beacon.qrCodeID
    ret['lastBeacon'] = check
    if riddle is not None:
        ret['statement'] = riddle.statement
        ret['answer'] = riddle.answer
    ret = jsonify(ret)
    response = make_response(ret, 200, {'Content-Type': "application/json"})
    return response

# getting the first point with the name of the team


@app.route("/firstpoint", methods=["POST"])
def firstpoint():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    ret = getTrip(json_handle['playercode'], json_handle['nameTeam'])
    if isinstance(ret, int):
        trip = Trip.query.get(ret)
        payload = getPoint(trip.idTrip, 0)
        response = make_response(
            payload, 200, {'Content-Type': "application/json"})
    else:
        response = ret
    return response

# request after confirmPoint for another members of the team


@app.route("/nextpoint", methods=['POST'])
def nextpoint():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    ret = getTrip(json_handle['playercode'], json_handle['nameTeam'])
    if isinstance(ret, int):
        trip = Trip.query.get(ret)
        payload = getPoint(trip.idTrip, team.Checkpoint)
        response = make_response(
            payload, 200, {'Content-Type': "application/json"})
    else:
        response = ret
    return response

# method for give the final board of game


@app.route("/end", methods=['POST'])
def end():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    game = Game.query.filter_by(PlayerCode=json_handle['playercode']).first()
    team = Team.query.filter_by(
        Game_idGame=game.idGame, name=json_handle['name']).first()
    teams = Team.query.filter_by(
        Game_idGame=game.idGame).order_by("score desc").all()
    classement = 1
    time = datetime.datetime.now() - game.gameStartedTime
    for t in teams:
        if t == team:
            break
        else:
            classement += 1
    ret = dict()
    ret['score'] = team.score
    ret['totalTeams'] = len(teams)
    ret['classement'] = classement
    ret['time'] = str(time)[:7]
    ret = json.dumps(ret)
    response = make_response(ret, 200, {'Content-Type': "application/json"})
    return response

# refreshing position in DB


@app.route("/refreshpos", methods=["PUT"])
def refreshpos():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    player = Player.query.filter_by(
        pseudonyme=json_handle['pseudonyme']).first_or_404()
    player.latitude = json_handle['latitude']
    player.longitude = json_handle['longitude']
    db.session.commit()
    ret = dict()
    ret['answer'] = True
    payload = jsonify(ret)
    response = make_response(payload, 200, {'Content-Type': "application/json"})
    return response

# get all teams informations player side


@app.route("/<playercode>/teams", methods=["GET"])
def teams(playercode):
    if Game.query.filter_by(PlayerCode=playercode).first():
        game = Game.query.filter_by(PlayerCode=playercode).first()
        teams = Team.query.filter_by(Game_idGame=game.idGame).all()
        payload = teams_schema.jsonify(teams)
        response = make_response(
            payload, 200, {'Content-Type': "application/json"})
    else:
        response = make_response("Code invalide!", 410)
    return response

# get all teams informations admin side


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
        payload = data.dumps()
        x = 200
    else:
        payload = "False"
        x = 403
    response = make_response(payload, x, {'Content-Type': "application/json"})
    return response

# make a broadcast message for launch the battle


@app.route("/<GameMasterCode>/BattleReady", methods=["GET"])
def BattleReady(GameMasterCode):
    if check_adm(GameMasterCode):
        game = Game.query.filter_by(
            GameMasterCode=GameMasterCode).first()
        game.isStarted = True
        teams = Team.query.filter_by(Game_idGame=game.idGame).all()
        for team in teams:
            players = team.players
            for player in players:
                data = dict()
                data['startGameNow'] = True
                r = firebase(player.idPlayer, data)
                print r.content
        db.session.commit()
        payload = "ok"
        x = 200
    else:
        payload = "AdminCode invalide !"
        x = 403
        response = make_response(payload, x)
    return response


@app.route("/changeIndex", methods=["POST"])
def change_index():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    query = Beacon_has_Trip.update().where(Beacon_has_Trip.c.Trip_idTrip == json_handle['idTrip']).where(
        Beacon_has_Trip.c.Beacon_idBeacon == json_handle['idBeacon']).values(ind=json_handle['value'])
    r = db.session.execute(query)
    db.session.commit()
    return r

# check if it a admin code


def check_adm(code):
    if Game.query.filter_by(GameMasterCode=code).first():
        return True
    else:
        return False

# main parameter of Flask Application
if __name__ == "__main__":
    app.run(debug=True,
            ssl_context=(
                '/etc/letsencrypt/live/hikong.masi-henallux.be/fullchain.pem',
                '/etc/letsencrypt/live/hikong.masi-henallux.be/privkey.pem'),
            host='0.0.0.0')
