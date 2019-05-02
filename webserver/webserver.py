from flask import Flask, request, Response, render_template, send_file, redirect, url_for
from functools import wraps
from pymongo import MongoClient

app = Flask(__name__)
mongoclient = None
mongodb = None

@app.route("/background.png")
def handle_background():
    return send_file("background.png")

@app.route("/send_data", methods=['POST'])
def handle_game_data():
    value = request.args.get("value")
    feild = request.args.get("feild")
    player = request.args.get("player")

    feilds = ['Asteroids_Destroyed','Eliminations','Shots_Fired']

    collection = mongodb["game"]
    collection2 = mongodb["players"]
    
    collection.update_one({"name":player},{'$set':{'stats.'+feild:value}},upsert=True)
    
    if feild in feilds:
        collection2.update_one({"name":player},{'$inc':{'stats.Career_'+feild:int(value)}},upsert=True)
    
    if feild == "Place":
        collection2.update_one({"name":player},{'$inc':{'stats.Career_Wins':int(int(value)==1)}},upsert=True)
        collection2.update_one({"name":player},{'$inc':{'stats.Career_Games':1}},upsert=True)

    

    return "Received"

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
        collection = mongodb['game']
        cursor = collection.find({'name':player_name})
        for document in cursor:
            if document['stats']:
                return document['stats']

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
        collection = mongodb['players']
        cursor = collection.find({'name':player_name})
        for document in cursor:
            if document['stats']:
                return document['stats']

    return player_data

if __name__ == "__main__":
    mongoclient = MongoClient('127.0.0.1', 27017)
    mongodb = mongoclient['asteroids']
    app.run(host='0.0.0.0', port=80, debug=False)
