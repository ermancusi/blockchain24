from algosdk.transaction import ApplicationDeleteTxn
from utilities import wait_for_confirmation, getSKAddr
import algosdk.encoding as e
from daoutilities import getAssetIdFromName, DAOGovName, DAOtokenName
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

"""
Make a transaction that will delete an application
"""


def deleteApp(mnemFile,appId):
    """
    This function makes a transaction that will delete an application.
    The user who will receive the money after the DAO is deleted, must also be the last to return the GOV token to it.
    Only after that user can invoke the code to delete the DAO.

    
    :param mnemFile: It is a file containing the mnemonic phrase of the account requesting deletion.
    :param appId: The `index` parameter in the `startApp` function is an identifier for the application.
    """
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    SK,Addr=getSKAddr(mnemFile)


    print("User addr:",Addr)

    appAddr=e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big')))
    print("App id:   ",appId)
    print("App addr: ",appAddr)
    
    assetId1=getAssetIdFromName(appAddr,DAOGovName,algodClient)
    if assetId1 is None:
        print("Could not find asset",DAOGovName)
        exit()
    
    assetId2=getAssetIdFromName(appAddr,DAOtokenName,algodClient)
    if assetId2 is None:
        print("Could not find asset",DAOtokenName)
        exit()


    utxn=ApplicationDeleteTxn(sender=Addr,sp=params,index=appId,foreign_assets=[assetId1,assetId2])
    stxn=utxn.sign(SK)
    txId=stxn.transaction.get_txid()
    print("Tx id:    ",txId)
    algodClient.send_transactions([stxn])
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)
    print("Deleted:  ",txResponse['txn']['txn']['apid'])  


if __name__=='__main__':
    MnemFile="Accounts/Alice/Alice.mnem"
    appId=0
    with open("AppID.txt", 'r') as file:
        appId = int(file.read())
    
    deleteApp(MnemFile, appId)

    
