import sys
import base64
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def getSellingPrice(appIndex,algodClient):
    app=algodClient.application_info(appIndex)
    for kk in app['params']['global-state']:
        key=kk['key']
        key=base64.b64decode(key)
        key=key.decode('utf-8')
        if key=="scurrentPrice":
            return kk['value']['uint']

if __name__=='__main__':
    if len(sys.argv)!=2:
        print("usage: python3 "+sys.argv[0]+"<app index>")
        exit()


    appIndex=int(sys.argv[1])


    algodClient=algod.AlgodClient(algodToken,algodAddress)


    print(getSellingPrice(appIndex,algodClient)+3)
    

