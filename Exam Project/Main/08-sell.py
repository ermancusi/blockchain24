from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAssetIdFromName, getSellingPrice, DAOtokenName
from algosdk.transaction import ApplicationNoOpTxn, AssetTransferTxn, calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress = "https://testnet-api.algonode.cloud"  # Algorand test node
algodToken = ""  # free service does not require tokens

def sell(MnemFile, appIndex, nAssets):
    """
    The `sell` function is used by a user to sell an asset to the DAO.
    
    :param MnemFile: It is a file containing the mnemonic phrase of the account that asks for the price update.
    :param appIndex: The `index` parameter in the `startApp` function is an identifier for the application.
    :param nAssets: The `nAssets` parameter in the `buy` function represents the number of assets that
    a user wants to buy. 

    :return: The `sell` function returns the transaction ID (`txId`) of the transactions that were sent
    to the Algorand blockchain for selling the specified assets.
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
    wait_for_confirmation(algodClient, txId, 4)  

if __name__ == '__main__':
    mnemFile="Accounts/Frank/Frank.mnem"

    appIndex=0
    with open("AppID.txt", 'r') as file:
        appIndex = int(file.read())

    nAssets=1
    
    sell(mnemFile, appIndex, nAssets)
