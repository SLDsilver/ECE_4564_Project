from flask import Flask, request, Response, render_template
from functools import wraps

app = Flask(__name__)

@app.route("/")
def handle_default():
    player_name = "Test_User"
    player_data = dict()
    player_data["Most Time Survived"] = 23.5
    player_data["Career Eliminations"] = 18
    player_data["Career Asteroids Destroyed"] = 502
    player_data["Wins"] = 2
    player_data["Top 3 Placements"] = 5

    game_data = dict()
    game_data["Time Survived"] = 8.32
    game_data["Eliminations"] = 1
    game_data["Asteroids Destroyed"] = 27
    game_data["Place"] = 2

    return render_template('test.html', player = player_data, game = game_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
