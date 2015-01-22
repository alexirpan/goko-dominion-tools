import os
import sys

# to get import below working
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')
# this should be append instead of insert...except for some reason that isn't working
sys.path.insert(1, basedir)

from flask import Flask, Response, request, render_template
import requests
from parser.gokoparse import generate_game_states

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')
sys.path.append(basedir)

app = Flask(__name__)
app.config.from_object('app.config')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response

@app.route('/')
def index():
    # just for developing
    return render_template("index.html")

@app.route('/replay')
@app.route('/replay/')
def parse_log():
    logurl = request.args.get('log_url')
    try:
        log = requests.get(logurl, timeout=1.0)
    except requests.exceptions.Timeout:
        return "TIMEOUT OH NOOO"
    except:
        return "Are you sure you gave a valid url?"
    try:
        text, game_states = generate_game_states(log.text, debug=False)
        game_states = [state.to_dict() for state in game_states]
        return render_template("replay.html", log=text, states=game_states, logurl=logurl);
    except Exception as e:
        print e
        return "An exception was raised when attempting to construct game states"


if __name__ == '__main__':
    app.run()
