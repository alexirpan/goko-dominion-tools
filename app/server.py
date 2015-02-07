import os
import sys

# to get import below working
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')
# this should be append instead of insert...except for some reason that isn't working
sys.path.insert(1, basedir)

from flask import Flask, Response, request, render_template
import requests
import parser.gokoparse
import parser.decktrack

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
        return render_template("index.html", msg="Request timed out - try again")
    except:
        return render_template("index.html", msg="Could not download log - are you sure the URL is correct?")
    # log obtained
    try:
        # full deck tracking
        text, game_states = parser.decktrack.generate_game_states(log.text, debug=True)
        game_states = [state.to_dict() for state in game_states]
        return render_template("deckreplay.html", log=text, states=game_states, logurl=logurl)
    except Exception as e:
        try:
            # hand tracking with strict card checks
            text, game_states = parser.gokoparse.generate_game_states(log.text, debug=True)
            game_states = [state.to_dict() for state in game_states]
            return render_template("replay.html", log=text, states=game_states, logurl=logurl)
        except Exception as e:
            # hand tracking with loose checks
            try:
                text, game_states = parser.gokoparse.generate_game_states(log.text, debug=False)
                game_states = [state.to_dict() for state in game_states]
                return render_template("replay.html", log=text, states=game_states, logurl=logurl)
            except Exception as e:
                return render_template("index.html", msg="Unfortunately, the parser was unable to process your log")

dev = False
host = '127.0.0.1' if dev else '0.0.0.0'
port = int(os.environ.get("PORT", 5000))
if __name__ == '__main__':
    app.run(host=host, port=port)
