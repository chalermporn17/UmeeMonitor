import requests
import json
import PeerService
import UsageService
import SocketService
from multiprocessing import Process

rpc_address = "http://localhost:26657/"
secret      = "12345678"
DataPath    = "/root"
ServerAddress = "http://localhost:5001/api/"
WebSocket     = "ws://127.0.0.1:26657/websocket"

NodeData = json.loads( requests.get(f"{rpc_address}status").text.replace("\n","") )
Moniker     = NodeData['result']['node_info']['moniker']
Id          = NodeData['result']['node_info']['id']
VotingPower = int( NodeData['result']['validator_info']['voting_power'] )
print( VotingPower )
payload     = { "Moniker" : Moniker , "Id" : Id , "Validator" : VotingPower != 0 , "secret" : secret }

res = requests.post( ServerAddress + "submitNode" , data = payload )

if res.status_code != 200:
    raise Exception("Error with connection to main server")

#UsageService.start( DataPath , Id , secret , ServerAddress , rpc_address )
#PeerService.start( Id , secret , ServerAddress , rpc_address )
#SocketService.start( WebSocket , Id , secret , ServerAddress , rpc_address )
Ps = {}
p1 = Process(target=UsageService.start,  args=( DataPath , Id , secret , ServerAddress , rpc_address ) )
p2 = Process(target=PeerService.start,   args=( Id , secret , ServerAddress , rpc_address ) )
p3 = Process(target=SocketService.start, args=( WebSocket , Id , secret , ServerAddress , rpc_address ) )

Ps['UsageService'] = p1
Ps['PeerService'] = p2
Ps['SocketService'] = p3

Ps['UsageService'].start()
Ps['PeerService'].start()
Ps['SocketService'].start()


