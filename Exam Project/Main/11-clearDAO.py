from algosdk.transaction import ApplicationClearStateTxn, AssetCloseOutTxn
from utilities import wait_for_confirmation, getSKAddr
import algosdk.encoding as e
from daoutilities import getAssetIdFromName, getAssetCreator, DAOtokenName
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens


"""
-Make a transaction that will send all of an ASA away, and opt out of it

-Make a transaction that will clear a user's state for an application
"""
def clearDAO(MnemFile,appId):
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    SK,Addr=getSKAddr(MnemFile)

    print("User addr:",Addr)

    appAddr=e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big')))
    
    print("App id:   ",appId)
    print("App addr: ",appAddr)

    
    assetId=getAssetIdFromName(appAddr,DAOtokenName,algodClient)
    if assetId is None:
        print("Could not find asset",DAOtokenName)
    else:
        creator=getAssetCreator(assetId,algodClient)
        print(f'Asset {DAOtokenName} found with id {assetId}')
        if creator!=Addr:
            print("Creator:  ",creator)
            utxn=AssetCloseOutTxn(sender=Addr,sp=params,receiver=creator,index=assetId)
            stxn=utxn.sign(SK)
            txId=algodClient.send_transaction(stxn)
            wait_for_confirmation(algodClient,txId,4)
            txResponse=algodClient.pending_transaction_info(txId)
            print(f'Asset {DAOtokenName} cleared')
        else:
            print(f'You are the creator')
            exit()

    utxn=ApplicationClearStateTxn(Addr,params,appId)
    stxn=utxn.sign(SK)
    txId=algodClient.send_transaction(stxn)
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)
    print(f'Application {appId} cleared')


if __name__=='__main__':
    MnemFile="Accounts/Alice/Alice.mnem"
    appId=0
    with open("AppID.txt", 'r') as file:
        appId = int(file.read())

    clearDAO(MnemFile,appId)
    
    
