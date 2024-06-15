from algosdk.transaction import AssetTransferTxn
import algosdk.encoding as e
from utilities import wait_for_confirmation,getSKAddr
from daoutilities import getAssetIdFromName, DAOGovName
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def transfer(senderMNEMFile,appId):
    """
    The function `transfer` in Python sends an asset transfer transaction to a specified application
    address using Algorand blockchain.
    
    :param senderMNEMFile: It looks like the `senderMNEMFile` parameter is used as an input to the
    `getSKAddr` function to retrieve the sender's secret key and address. The sender's secret key is
    likely stored in a file in mnemonic format, which can be used to derive the sender's address
    :param appId: It looks like the `appId` parameter is being used in the `transfer` function, but its
    value is not provided in the code snippet. The `appId` parameter seems to be an identifier for an
    application. You need to pass a specific value for `appId` when calling the `transfer`
    """
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


if __name__=="__main__":
    appId=0
    with open("AppID.txt", 'r') as file:
        appId = int(file.read())

    founders=["Accounts/Bob/Bob.mnem","Accounts/Charlie/Charlie.mnem","Accounts/Alice/Alice.mnem"]

    for senderMNEMFile in founders:         
        transfer(senderMNEMFile,appId)
