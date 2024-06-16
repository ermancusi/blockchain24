import sys
from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAssetIdFromName, DAOGovName
from algosdk.transaction import ApplicationNoOpTxn, AssetTransferTxn, calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def proposePrice(MnemFile,appIndex,price,prefix):
    """
    The function `proposePrice` serves to propose a price (buy or sell) for a specific asset.
    The parameters required by the function are:
    
    :param MnemFile: It is a file containing the mnemonic phrase of the account that asks for the price update.
    :param appIndex: The `index` parameter in the `startApp` function is an identifier for the application.
    :param price: The `price` parameter in the `proposePrice` represents the price
    value that you want to propose. 
    :param prefix: The `prefix` parameter is a string which can be equal to "b" if it is a buy price update; equal to "s" if it is a sell price update. 

    
    :return: The function `proposePrice` does not explicitly return any value. If the code execution is
    successful without any exceptions, it will print the confirmation message
    "wait_for_confirmation(algodClient,txId,4)" after waiting for the transaction to be
    confirmed. If there is an exception during the transaction sending process, it will print the error
    message and return without any further action.
    """

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()

    SK,Addr=getSKAddr(MnemFile)
    print("User addr:       ",Addr)

    appAddr=e.encode_address(e.checksum(b'appID'+appIndex.to_bytes(8, 'big')))
    print("App addr:        ",appAddr)

    assetId=getAssetIdFromName(appAddr,DAOGovName,algodClient)
    if assetId==None:
        print("Could not find asset")
        exit()
    print("Asset Id:        ",assetId)
    print("AssetName:       ",DAOGovName)

    ttxn=AssetTransferTxn(sender=Addr,sp=params,receiver=appAddr,amt=1,index=assetId)
    ctxn=ApplicationNoOpTxn(sender=Addr,sp=params,index=appIndex,app_args=[prefix.encode(),price.to_bytes(8,'big')],foreign_assets=[assetId])
    gid=calculate_group_id([ttxn,ctxn])

    ttxn.group=ctxn.group=gid
    
    
    sttxn=ttxn.sign(SK)
    sctxn=ctxn.sign(SK)
    
    try:
        txId=algodClient.send_transactions([sttxn,sctxn])
    except Exception as err:
        print("***********")
        print(err)
        return
    
    wait_for_confirmation(algodClient,txId,4)  


if __name__=='__main__':
    if len(sys.argv)!=4:
        print("usage: python3 "+sys.argv[0]+" <mnem> <price> s/b")
        exit()

    appIndex=0
    with open("AppID.txt", 'r') as file:
        appIndex = int(file.read())

    MnemFile=sys.argv[1]    
    price=int(sys.argv[2])
    prefix=sys.argv[3]+"p"
   
    proposePrice(MnemFile,appIndex,price,prefix)
    

