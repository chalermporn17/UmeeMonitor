import json
import time
import json
import requests
from pythonping import ping
import tcp_latency

def ping_host(host):
    ping_result = ping(target=host, count=5, timeout=2)

    return {
        'host': host,
        'avg_latency': ping_result.rtt_avg_ms,
        'min_latency': ping_result.rtt_min_ms,
        'max_latency': ping_result.rtt_max_ms,
        'packet_loss': ping_result.packet_loss
    }

def start( Id , secret , ServerAddress , rpc_address ):
    AllPeers      = []

    # Send initialize request
    payload = { "Id" : Id , "secret" : secret }

    res = requests.post( f"{ServerAddress}clearPeers" , data = payload )
    if res.status_code != 200:
        raise Exception("Error with connection to main server ( Peer service )")

    FirstRound = True
    #while False:
    while 1:
        NetInfo = json.loads( requests.get(f"{rpc_address}net_info").text.replace("\n","") )
        ThisPeerRound = []
        for peer in NetInfo['result']['peers']:
            Moniker = peer['node_info']['moniker']
            ID      = peer['node_info']['id']
            IP      = peer['remote_ip']
            PORT    = peer['node_info']['listen_addr'].split(':')[-1]
            
            ThisPeerRound.append( [ ID , IP , PORT ] )
            AllPeers.append( [ ID , IP , PORT ] )
            

            if FirstRound:
                result = -1
            else:
                result1 = tcp_latency.measure_latency(host=IP, port=PORT, runs=4, timeout=2 )
                if( len(result1) > 0 ):
                    result = sum(result1)/len(result1)
                else:
                    result2 = ping_host( IP )['avg_latency']
                    result = -1 if result2 == 2000 else result2

            payload = { "Id" : Id , "secret" : secret , "Moniker" : Moniker , "PeerID" : ID  , "IP" : IP , "PORT":PORT , "Latency" : result }
            res = requests.post( f"{ServerAddress}submitPeer" , data = payload )
            if not FirstRound:
                time.sleep( 5 )
            
        for peer in AllPeers:
            if peer not in ThisPeerRound:
                payload = { "Id" : Id , "secret" : secret , "PeerID" : peer[0]  , "IP" : peer[1] , "PORT":peer[2] }
                res = requests.post( f"{ServerAddress}deletePeer" , data = payload )
                if res.status_code != 200:
                    raise Exception("Error with connection to main server ( Peer service )")
        if FirstRound:
            FirstRound = False
        else:
            time.sleep(30)
        