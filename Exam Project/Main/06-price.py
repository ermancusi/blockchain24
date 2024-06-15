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
    The function `proposePrice` in Python interacts with the Algorand blockchain to propose a price for
    a specific application.
    
    :param MnemFile: It seems like the code snippet you provided is a function for proposing a price in
    a transaction. The parameters required by the function are:
    :param appIndex: The `appIndex` parameter in the `proposePrice` function appears to represent the
    index of the application for which you are proposing a price. This index is likely used to identify
    a specific application within the context of your Algorand smart contract or application. It could
    be an integer value that
    :param price: The `price` parameter in the `proposePrice` function seems to represent the price
    value that you want to propose. It is being converted to bytes using `price.to_bytes(8,'big')`
    before being passed as an argument in the `ApplicationNoOpTxn` transaction. This
    :param prefix: The `prefix` parameter in the `proposePrice` function seems to be a string that will
    be encoded before being passed as an argument in the `ApplicationNoOpTxn` transaction. This encoded
    string will be used as one of the application arguments along with the `price` value that is
    :return: The function `proposePrice` does not explicitly return any value. If the code execution is
    successful without any exceptions, it will print the confirmation message
    "confirmed_txn=wait_for_confirmation(algodClient,txId,4)" after waiting for the transaction to be
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
    
    confirmed_txn=wait_for_confirmation(algodClient,txId,4)  


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
    

