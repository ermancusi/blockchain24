import sys
from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAssetIdFromName, getSellingPrice, DAOtokenName
from algosdk.transaction import ApplicationNoOpTxn, AssetTransferTxn, calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress = "https://testnet-api.algonode.cloud"  # Algorand test node
algodToken = ""  # free service does not require tokens

def sell(MnemFile, appIndex, nAssets):
    algodClient = algod.AlgodClient(algodToken, algodAddress)
    params = algodClient.suggested_params()

    SK, Addr = getSKAddr(MnemFile)
    print("User Addr:", Addr)

    appAddr = e.encode_address(e.checksum(b'appID' + appIndex.to_bytes(8, 'big')))
    print("App Addr: ", appAddr)

    price = getSellingPrice(appIndex, algodClient)  # Use a new function to get the buying price
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
    if len(sys.argv) != 4:
        print("usage: python3 " + sys.argv[0] + " <mnem> <app index> <nAssets>")
        exit()

    mnemFile = sys.argv[1]
    appIndex = int(sys.argv[2])
    nAssets = int(sys.argv[3])
    
    sell(mnemFile, appIndex, nAssets)
