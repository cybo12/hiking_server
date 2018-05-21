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

app.config['JSON_AS_ASCII'] = False


@app.route("/player", methods=["GET"])
def get_player():
    all_players = Player.query.all()
    return players_schema.jsonify(all_players)


@app.route('/player/id/<id>', methods=["GET"])
def player_detail(id):
    player = Player.get(id).first_or_404()
    return player_schema.jsonify(player)


@app.route('/player/<pseudonyme>', methods=["GET"])
def player_detail_pseudonyme(pseudonyme):
    player = Player.query.filter_by(pseudonyme=pseudonyme).first_or_404()
    return player_schema.jsonify(player)


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['Error'] = error
    return resp


@app.route("/player", methods=["POST"])
def add_player():
    if Player.query.filter_by(pseudonyme=request.form['pseudonyme']).first() is None:
        me = Player(pseudonyme=request.form['pseudonyme'])
        db.session.add(me)
        db.session.commit()
        ret = str(me.idPlayer)
    else:
        ret = "shit happens - name already used"
        print ret
    return ret


@app.route("/del_player", methods=["DELETE"])
def del_player():
    print request.form
    if Player.query.filter_by(pseudonyme=request.form['pseudonyme']).first():
        p = Player.query.filter_by(pseudonyme=request.form[
                                   'pseudonyme']).first()
        db.session.delete(p)
        db.session.commit()
        ret = "player" + p.pseudonyme + "delete"
    else:
        ret = "shit happens - name already used"
        print ret
    return ret

"""
    me = Game(name=request.form['name'],
              joindCode=code_player,
              gmCode=code_admin,
              type=request.form['type'],
              isStarted=False,
              Settings_idSettings=request.form['settings'])
    db.session.add(me)
    db.session.commit()
"""


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
        teams = Team.query.order_by(Team.Checkpoint).all()
        data = ObjDict()
        data.teams = []
        for team in teams:
            test = team.__dict__
            trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
            beacons = trip.beacons
            test['trip'] = trip.__dict__
            test['trip']['beacons'] = []
            for beacon in beacons:
                riddle = Riddle.query.filter_by(
                    idRiddle=beacon.Riddle_idRiddle).first()
                ensemble = beacon.__dict__
                ensemble['Riddle'] = riddle.__dict__
                test['trip']['beacons'].append(ensemble)
            data.teams.append(test)

        ret = data.dumps()
    elif Game.query.filter_by(PlayerCode=json_handle['code']).first():
        ret = "booh je ne sais plus ce que je dois mettre"
    else:
        ret = "False"
    return ret


@app.route("/jointeam", methods=["POST"])
def add_player_team():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    ret = "False"
    if Player.query.filter_by(pseudonyme=json_handle['pseudonyme']).first() is None:
        if Team.query.get(json_handle['idTeam']):
            me = Player(pseudonyme=json_handle['pseudonyme'],
                        idTeam=json_handle['idTeam'], token=json_handle['token'], latitude=json_handle['latitude'], longitude=json_handle['longitude'])
            db.session.add(me)
            db.session.commit()
            ret = "True"
    else:
        ret = "Pseudo déjà prit"
    print ret
    return ret


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
                Settings_idSettings=settings.idSettings, isStarted=False)
    db.session.add(settings)
    game.Settings_idSettings = settings.idSettings
    db.session.add(game)
    db.session.commit()
    for x in teams:
        x.Game_idGame = game.idGame
    db.session.commit()
    ret = {'PlayerCode': code_player, 'GameMasterCode': code_admin}
    ret = jsonify(ret)
    print ret
    return ret


@app.route("/firstpoint", methods=["GET"])
def firstpoint():
    trip = Trip.query.filter_by(Team_idTeam=request.headers['idTeam']).first()
    riddle = Riddle.query.get(trip.beacons[0].Riddle_idRiddle)
    ret = {'latitude': trip.beacons[0].latitude, 'longitude': trip.beacons[
        0].longitude, 'statement': riddle.statement, 'answer': riddle.answer, 'GameMode': riddle.GameMode}
    ret = jsonify(ret)
    return ret


@app.route("/confirmpoint", methods=["POST"])
def confirmPoint():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    team = Team.query.get(json_handle['idTeam'])
    trip = Trip.query.filter_by(Team_idTeam=team.idTeam).first()
    print "Checkpoint : {}".format(team.Checkpoint)
    if team.lives == 0:
        ret = False
    else:
        team.Checkpoint += 1
        db.session.commit()
        if team.Checkpoint <= len(trip.beacons):
            riddle = Riddle.query.get(
                trip.beacons[team.Checkpoint].Riddle_idRiddle)
            ret = {'latitude': trip.beacons[team.Checkpoint].latitude, 'longitude': trip.beacons[
                team.Checkpoint].longitude, 'statement': riddle.statement, 'answer': riddle.answer, 'GameMode': riddle.GameMode}
            ret = jsonify(ret)
        else:
            ret = "False"
    return ret


@app.route("/refreshpos", methods=["PUT"])
def refreshpos():
    try:
        json_handle = json.loads(request.data)
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
    player = Player.query.get(json_handle['idPlayer'])
    player.latitude = json_handle['latitude']
    player.longitude = json_handle['longitude']
    return "True"


@app.route("/teams", methods=["GET"])
def teams():
    teams = Team.query.filter_by(Game_idGame=request.headers['idGame']).all()
    return teams_schema.jsonify(teams)   

@app.route("/adm/getTeamsStats", methods=["GET"])
def getTeamsStats():
    if check_adm(request.headers['code']):
        data = ObjDict()
        data['teams'] = []
        teams = Team.query.all()
        for team in teams:
            ind = 0
            players = team.players
            print len(team.players)
            ensemble = team.__dict__
            ensemble['players'] = []
            if len(players) != 0:
                for ind in xrange(0, len(players)):
                    print players[ind]
                    ensemble['players'].append(players[ind].__dict__)
                data['teams'].append(ensemble)
        ret = data.dumps()
    else:
        ret = "False"
    return ret


@app.route("/adm/BattleReady", methods=["GET"])
def BattleReady():
    if check_adm(request.headers['GameMasterCode']):
        Teams = Team.query.filter_by(
            GameMasterCode=request.headers['GameMasterCode']).all()
        for team in teams:
            players = team.players
            for player in players:
                headers = {'Authorization': 'key={AAAAwixAe04:APA91bEhaFFRoy9VpP7n2w9WjyaahFuRZCC_VPtHEo6DMrnN_gGVhMX-e9M6u0V_Kj9J7TKSlLiHRt2K6QhIgixHmJAwrVCR74WfsX-52QsWAA2jSEcip10JPahXgwced4Ep5H5V6l57}',
                          'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
                payload = {
                    "to": "\{{}\}".format(player.token),
                    "notification": {
                        "body": "hello",
                        "title": "world"
                    }
                }
                r = requests.POST('https://fcm.googleapis.com/fcm/send' , payload=payload, headers=headers)
                print r
    return "True"
"""
https://fcm.googleapis.com/fcm/send
Authorization:
Cache-Control:no-cache
Content-Type:application/json
Postman-Token:51d9246e-b208-4da0-85f3-32ab9a112e4b
{
    "to":"{Destination token}",
    "notification":{
        "body":"hello",
        "title":"world"
    }
}
"""


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
