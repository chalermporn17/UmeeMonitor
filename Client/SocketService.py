import websocket
import json
import ssl
import time
import requests
def TimeDelta( ServerAddress ):
    Time1 = requests.get( ServerAddress + "serverTime" )
    TripTime    = Time1.elapsed.total_seconds() / 2
    ReceiveTime = float( Time1.text ) + TripTime
    TimeDelta   = ReceiveTime - time.time()

    return TimeDelta

TimeDeltas = [ ]
Results    = [ ]
    
def start( SOCKET , Id , secret , ServerAddress , rpc_address ):

    TimeDeltas.append( TimeDelta( ServerAddress )  )

    print( TimeDeltas )
    params = {
        "jsonrpc": "2.0",
        "method": "subscribe",
        "id": 0,
        "params": {
            "query": "tm.event='NewRoundStep'"
        }
    }

    def on_open(ws):
        print('Opened Connection')
        ws.send(json.dumps(params))

    def on_close(ws,err1,err2):
        print('Closed Connection')

    def on_message(ws, message):
        global TimeDeltas
        global Results

        data = json.loads(message)
        step = data['result']['data']['value']['step']
        height = data['result']['data']['value']['height']
        
        if step == "RoundStepPropose":
            stage = 1
        elif step == "RoundStepPrevote":
            stage = 2
        elif step == "RoundStepPrecommit":
            stage = 3
        elif step == "RoundStepCommit":
            stage = 4
        elif step == "RoundStepNewHeight":
            stage = 5
        else:
            stage = -1
            
        delta = TimeDeltas[0]
        Results.append( [ height , stage , time.time() + delta ] )

        if stage == 5:
            TimeDeltas = [ TimeDelta( ServerAddress )  ]
            payload = { "Id" : Id , "secret" : secret , "Data" : json.dumps(Results) }
            Results = [ ]

            res = requests.post( f"{ServerAddress}UpdateStatus" , data = payload )
            if res.status_code != 200:
                raise Exception("Error with connection to main server ( Socket Service )")



    def on_error(ws, err):
        print("Got a an error: ", err)


    ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message = on_message,on_error=on_error)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

