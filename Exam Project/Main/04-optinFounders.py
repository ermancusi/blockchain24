from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAssetIdFromName, DAOGovName, DAOtokenName
from algosdk.transaction import ApplicationOptInTxn, AssetTransferTxn, calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def optInDAO(MnemFile,appId):
    """
    The `optInDAO` function is used to get DAO founders to opt-in.
    
    :param MnemFile: The `MnemFile` parameter in the `optInDAO` function is used to specify the file
    containing the mnemonic phrase of the founder.
    :param appId: The `appId` parameter in the `optInDAO` function represents the application ID that is
    being used for a decentralized autonomous organization (DAO). 
    """

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()

    SK,Addr=getSKAddr(MnemFile)
    print("User addr:       ",Addr)

    appAddr=e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big')))
    algodClient.account_info(appAddr)
    print("App id:          ", appId)
    print("App addr:        ", appAddr)

    assetId1=getAssetIdFromName(appAddr,DAOGovName,algodClient)
    assetId2=getAssetIdFromName(appAddr,DAOtokenName,algodClient)

    if assetId1 is None or assetId2 is None:
        print("Could not find assets")
        exit()
        
    print("Asset id1:       ",assetId1)
    print("Asset id2:       ",assetId2)

    txn1=AssetTransferTxn(sender=Addr,sp=params,receiver=Addr,amt=0,index=assetId1)
    txn2=AssetTransferTxn(sender=Addr,sp=params,receiver=Addr,amt=0,index=assetId2)
    txn3=ApplicationOptInTxn(sender=Addr,sp=params,index=appId,foreign_assets=[assetId1,assetId2])
    gid=calculate_group_id([txn1,txn2,txn3])

    txn1.group=txn2.group=txn3.group=gid

    stxn1=txn1.sign(SK)
    stxn2=txn2.sign(SK)
    stxn3=txn3.sign(SK)
    txId=algodClient.send_transactions([stxn1,stxn2,stxn3])
    print("Transaction id:  ",txId)
    wait_for_confirmation(algodClient,txId,4)



if __name__=='__main__':  
    index=0
    with open("AppID.txt", 'r') as file:
        index = int(file.read())

    founders=["Accounts/Alice/Alice.mnem","Accounts/Bob/Bob.mnem","Accounts/Charlie/Charlie.mnem"]

    for MnemFile in founders:          
       optInDAO(MnemFile, index)
    
    
