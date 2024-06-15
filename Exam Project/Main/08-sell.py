from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAssetIdFromName, getSellingPrice, DAOtokenName
from algosdk.transaction import ApplicationNoOpTxn, AssetTransferTxn, calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress = "https://testnet-api.algonode.cloud"  # Algorand test node
algodToken = ""  # free service does not require tokens

def sell(MnemFile, appIndex, nAssets):
    """
    This Python function sells a specified number of assets associated with a particular application
    index using Algorand blockchain transactions.
    
    :param MnemFile: It seems like the code snippet you provided is a Python function for selling assets
    using Algorand blockchain. The parameters required for this function are:
    :param appIndex: The `appIndex` parameter in the `sell` function is used to specify the index of the
    application that you want to interact with. This index is typically a unique identifier assigned to
    an application on the Algorand blockchain. It helps the function identify which application it
    should send transactions to when performing
    :param nAssets: It seems like the definition of the `sell` function is missing the description of
    the `nAssets` parameter. The `nAssets` parameter likely represents the number of assets that the
    user wants to sell. This parameter specifies the quantity of assets to transfer from the sender's
    address to the application address
    :return: The `sell` function returns the transaction ID (`txId`) of the transactions that were sent
    to the Algorand blockchain for selling the specified assets through the application.
    """
    algodClient = algod.AlgodClient(algodToken, algodAddress)
    params = algodClient.suggested_params()

    SK, Addr = getSKAddr(MnemFile)
    print("User Addr:", Addr)

    appAddr = e.encode_address(e.checksum(b'appID' + appIndex.to_bytes(8, 'big')))
    print("App Addr: ", appAddr)

    price = getSellingPrice(appIndex, algodClient)  
    if price is None:
        print("Cannot find price")
        exit()
    print("Selling Price:    ", price)

    assetId = getAssetIdFromName(appAddr, DAOtokenName, algodClient)

    if assetId is None:
        print(f'Asset not found')

    print("Asset Id: ", assetId)

    atxn = AssetTransferTxn(sender=Addr, sp=params, receiver=appAddr, amt=nAssets, index=assetId)
    ctxn = ApplicationNoOpTxn(sender=Addr, sp=params, index=appIndex, app_args=["sell".encode(), nAssets.to_bytes(8, 'big')], foreign_assets=[assetId])
    gid = calculate_group_id([atxn, ctxn])
    atxn.group = ctxn.group = gid

    satxn = atxn.sign(SK)
    sctxn = ctxn.sign(SK)
    
    try:
        txId = algodClient.send_transactions([satxn, sctxn])
    except Exception as err:
        print("***********")
        print(err)
        return
    confirmed_txn = wait_for_confirmation(algodClient, txId, 4)  

if __name__ == '__main__':
    mnemFile="Accounts/Frank/Frank.mnem"

    appIndex=0
    with open("AppID.txt", 'r') as file:
        appIndex = int(file.read())

    nAssets=1
    
    sell(mnemFile, appIndex, nAssets)
