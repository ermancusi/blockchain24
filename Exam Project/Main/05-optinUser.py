from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAssetIdFromName, DAOtokenName
from algosdk.transaction import ApplicationOptInTxn, AssetTransferTxn, calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def optInDAO(MnemFile,appId):
    """
    The function `optInDAO` facilitates opting into a decentralized autonomous organization (DAO) by
    transferring assets and opting into an application on the Algorand blockchain.
    
    :param MnemFile: It seems like the code snippet you provided is a Python function for opting into a
    Decentralized Autonomous Organization (DAO) using Algorand blockchain. The function takes two
    parameters: `MnemFile` and `appId`
    :param appId: The `appId` parameter in the `optInDAO` function is used to specify the application ID
    that the user wants to opt into. This function is designed to facilitate the process of opting into
    a Decentralized Autonomous Organization (DAO) by interacting with Algorand blockchain. The `appId`
    """

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()

    SK,Addr=getSKAddr(MnemFile)
    print("User addr:       ",Addr)

    appAddr=e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big')))
    accountInfo=algodClient.account_info(appAddr)
    print("App id:          ",appId)
    print("App addr:        ",appAddr)

    assetId=getAssetIdFromName(appAddr,DAOtokenName,algodClient)
    
    if assetId is None:
        print("Could not find asset",DAOtokenName)
        exit()

    print("Asset name:      ",DAOtokenName)
    print("Asset id:        ",assetId)

    txn1=AssetTransferTxn(sender=Addr,sp=params,receiver=Addr,amt=0,index=assetId)
    txn2=ApplicationOptInTxn(sender=Addr,sp=params,index=appId,foreign_assets=[assetId])
    gid=calculate_group_id([txn1,txn2])

    txn1.group=txn2.group=gid
    
    stxn1=txn1.sign(SK)
    stxn2=txn2.sign(SK)

    txId=algodClient.send_transactions([stxn1,stxn2])
    print("Transaction id:  ",txId)
    wait_for_confirmation(algodClient,txId,4)


if __name__=='__main__':
    index=0
    with open("AppID.txt", 'r') as file:
        index = int(file.read())

    MnemFile="Accounts/Frank/Frank.mnem"
   
    optInDAO(MnemFile,index)
    
    
