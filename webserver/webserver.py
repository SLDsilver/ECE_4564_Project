from flask import Flask, request, Response, render_template, send_file, redirect, url_for
from functools import wraps
from pymongo import MongoClient

app = Flask(__name__)

@app.route("/background.png")
def handle_background():
    return send_file("background.png")

@app.route("/",methods=['GET','POST'])
def handle_login():
    if request.method == "POST":
        #if the user exists
        return redirect(url_for('handle_player',player=request.form["username"]))
    return render_template("login.html")

@app.route("/player_info/<player>")
def handle_player(player = "test"):
    if player == "background.png":
        return redirect(url_for('handle_background'))
    game_data = get_game_data(player)
    player_data = get_player_data(player)

    return render_template('main.html', player = player_data, game = game_data)

def get_game_data(player_name = "test"):
    game_data = dict()
    
    if(player_name == "test"):
        game_data["Time Survived"] = 8.32
        game_data["Eliminations"] = 1
        game_data["Asteroids Destroyed"] = 27
        game_data["Place"] = 2
    else:
        client = MongoClient('127.0.0.1', 27017)
        db = client['asteroids']
        collection = db['game']
        cursor = collection.find({'name':player_name})
        for key,val in cursor:
            game_data[key]=val

    return game_data

def get_player_data(player_name = "test"):
    player_data = dict()
    
    if(player_name == "test"): 
        player_data["Most Time Survived"] = 23.5
        player_data["Career Eliminations"] = 18
        player_data["Career Asteroids Destroyed"] = 502
        player_data["Wins"] = 2
        player_data["Top 3 Placements"] = 5
    else:
        client = MongoClient('127.0.0.1', 27017)
        db = client['asteroids']
        collection = db['players']
        cursor = collection.find({'name':player_name})
        for key,val in cursor:
            game_data[key]=val

    return player_data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
