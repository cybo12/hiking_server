# -*- coding: utf-8 -*-
from models import *
from db import *
from flask import render_template, make_response, request
# from sqlalchemy.exc import exc
import random


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
    print request.form
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
        p=Player.query.filter_by(pseudonyme=request.form['pseudonyme']).first()
        db.session.delete(p)
        db.session.commit()
        ret = "player" + p.pseudonyme + "delete"
    else:
        ret = "shit happens - name already used"
        print ret
    return ret

@app.route("/player_team", methods=["POST"])
def add_player_team():
    if Player.query.filter_by(pseudonyme=request.form['pseudonyme']).first() is None:
        if Team.query.filter_by(idTeam=request.form['idTeam']).first():
            me = Player(pseudonyme=request.form['pseudonyme'],
                        Team_idTeam=request.form['idTeam'])
            db.session.add(me)
            db.session.commit()
            ret = str(me.idPlayer)
        else:
            ret = "shit happens - team not exist"
    else:
        ret = "shit happens - name already used"
    print ret
    return ret


@app.route("/game", methods=["POST"])
def add_game():
    code_player = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(6))
    code_admin = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(6))
    me = Game(name=request.form['name'],
              joindCode=code_player,
              gmCode=code_admin,
              type=request.form['type'],
              isStarted=False,
              Settings_idSettings=request.form['settings'])
    db.session.add(me)
    db.session.commit()
    ret = game_schema.jsonify(me)
    print ret
    return ret


@app.route("/settings", methods=["POST"])
def add_settings():
    me = Settings(tresholdShrink=request.form['tresholdShrink'],
                  mapViewEnable=request.form['mapViewEnable'],
                  timerRiddle=request.form['timerRiddle'],
                  lives=request.form['lives'],
                  enableNextBeaconVisibility=request.form['enableNextBeaconVisibility'])
    db.session.add(me)
    db.session.commit()
    ret = settings_schema.jsonify(me)
    print ret
    return ret


@app.route("/team", methods=["POST"])
def add_team():
    me = Team(tresholdShrink=request.form['tresholdShrink'],
              mapViewEnable=request.form['mapViewEnable'],
              timerRiddle=request.form['timerRiddle'],
              lives=request.form['lives'],
              enableNextBeaconVisibility=request.form['enableNextBeaconVisibility'])
    db.session.add(me)
    db.session.commit()
    ret = game_schema.jsonify(me)
    print ret
    return ret

@app.route("/del_team", methods=["DELETE"])
def del_team():
    print request.form
    if Team.query.filter_by(idTeam=request.form['idTeam']).first():
        t=Team.query.filter_by(idTeam=request.form['idTeam']).first()
        db.session.delete(t)
        db.session.commit()
        ret = "Team delete"
    else:
        ret = "shit happens - name already used"
        print ret
    return ret

if __name__ == "__main__":
    app.run(debug=True,
            ssl_context=(
                '/etc/letsencrypt/live/hikong.masi-henallux.be/fullchain.pem',
                '/etc/letsencrypt/live/hikong.masi-henallux.be/privkey.pem'),
            host='0.0.0.0')
