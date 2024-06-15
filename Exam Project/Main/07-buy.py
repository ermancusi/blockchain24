from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAssetIdFromName, getBuyingPrice, DAOtokenName
from algosdk.transaction import ApplicationNoOpTxn, PaymentTxn,calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def buy(MnemFile,appIndex,nAssets):
    """
    The `buy` function in Python interacts with the Algorand blockchain to purchase assets from a
    specified application using Algorand's Python SDK.
    
    :param MnemFile: It seems like the code snippet you provided is a function for buying assets in an
    Algorand blockchain application. The parameters required for this function are:
    :param appIndex: The `appIndex` parameter in the `buy` function seems to represent the index of the
    application you are interacting with. This index is used to identify a specific smart contract
    application on the Algorand blockchain. It is likely used to specify which smart contract
    application you want to interact with when performing
    :param nAssets: The `nAssets` parameter in the `buy` function represents the number of assets that
    you want to buy. It is used to calculate the total amount to be paid based on the buying price per
    asset
    :return: The `buy` function returns the transaction ID (`txId`) of the transactions sent to the
    Algorand blockchain for buying assets through an application.
    """
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()

    SK,Addr=getSKAddr(MnemFile)
    print("User Addr:",Addr)

    appAddr=e.encode_address(e.checksum(b'appID'+appIndex.to_bytes(8, 'big')))
    print("App Addr: ",appAddr)

    price=getBuyingPrice(appIndex,algodClient)
    if price is None:
        print("Cannot find price")
        exit()
    print("Buying Price:    ",price)

    assetId=getAssetIdFromName(appAddr,DAOtokenName,algodClient)

    if assetId is None:       
        print(f'Asset not found')

    print("Asset Id: ",assetId)

    ptxn=PaymentTxn(sender=Addr,sp=params,receiver=appAddr,amt=price*nAssets)
    ctxn=ApplicationNoOpTxn(sender=Addr,sp=params,index=appIndex,app_args=["buy".encode(),nAssets.to_bytes(8,'big')],foreign_assets=[assetId])
    gid=calculate_group_id([ptxn,ctxn])

    ptxn.group=ctxn.group=gid
   
    sptxn=ptxn.sign(SK)
    sctxn=ctxn.sign(SK)
    
    try:
        txId=algodClient.send_transactions([sptxn,sctxn])
    except Exception as err:
        print("***********")
        print(err)
        return
    confirmed_txn=wait_for_confirmation(algodClient,txId,4)  


if __name__=='__main__':
    mnemFile="Accounts/Alice/Alice.mnem"

    appIndex=0
    with open("AppID.txt", 'r') as file:
        appIndex = int(file.read())

    nAssets=1
    
    buy(mnemFile,appIndex,nAssets)
    
