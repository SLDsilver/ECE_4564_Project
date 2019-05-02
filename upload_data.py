import requests
def send_game(server,data=None):
    if data == None:
        data = dict()
        data['player'] = "test_player"
        data['Shots_Fired'] = 20
        data['Eliminations'] = 1
        data['Asteroids_Destroyed'] = 7
        data['Place'] = 1
        data['Eliminated_By'] = "Asteroid"

    for key,value in data.items():
        if key == 'player':
            continue
        else:
            send_data(server,data['player'],key,value)

def send_data(server,player="new_test",feild="Empty_Feild",value="Empty_value",collection="game"):
	
    requests.post("Http://"+server+"/send_data?feild="+feild+"&value="+str(value)+"&player="+player+"&collection="+collection)


if __name__ == "__main__":
	server="192.168.1.106"
	send_game(server)
	
