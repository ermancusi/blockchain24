from algosdk.transaction import AssetTransferTxn
import algosdk.encoding as e
from utilities import wait_for_confirmation,getSKAddr
from daoutilities import getAssetIdFromName, DAOGovName
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def transfer(senderMNEMFile,appId):
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    senderSK,senderAddr=getSKAddr(senderMNEMFile)

    appAddr=e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big')))

    assetId=getAssetIdFromName(appAddr,DAOGovName,algodClient)
    if assetId==None:
        print("Could not find asset")
    print("Asset id: ",assetId)
    
    txn=AssetTransferTxn(sender=senderAddr,sp=params,receiver=appAddr,amt=1,index=assetId)
    stxn=txn.sign(senderSK)
    txid=algodClient.send_transaction(stxn)
    print("Tx id:    ",txid)

    wait_for_confirmation(algodClient,txid,4)
    exit()


if __name__=="__main__":
    senderMNEMFile="Accounts/Bob/Bob.mnem"
    appId=0
    with open("AppID.txt", 'r') as file:
        appId = int(file.read())

    transfer(senderMNEMFile,appId)
