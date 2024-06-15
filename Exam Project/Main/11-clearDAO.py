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
    """
    The `clearDAO` function in Python clears a decentralized autonomous organization (DAO) by closing
    out its associated asset and clearing its application state.
    
    :param MnemFile: It seems like the `MnemFile` parameter is used as an input to retrieve a secret key
    and address. The function `getSKAddr(MnemFile)` likely reads the mnemonic file to obtain the secret
    key and address associated with it
    :param appId: The `appId` parameter in the `clearDAO` function is used to specify the ID of the
    application that you want to clear the state for. This function interacts with Algorand blockchain
    using the AlgodClient to clear the state of a specific application identified by its ID
    """
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
    
    
