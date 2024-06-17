from algosdk.v2client import algod
from algosdk.transaction import AssetCloseOutTxn, AssetDestroyTxn
from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAllAssets, getAssetCreator, getAmountAssetFromAddrIndex

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens


def removeAllAssets(MnemFile): 
    """
    The function `removeAllAssets` makes a transaction that will send all of an ASA away, and opt out of it

    :param MnemFile: It is a file containing the mnemonic phrase of the user

    """

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    SK,Addr=getSKAddr(MnemFile)

    listAssets=getAllAssets(Addr,algodClient)
    print(f'Found {len(listAssets)} assets for address {Addr}')

    for index in listAssets:
        creator=getAssetCreator(index,algodClient)
        if creator is None:
            print(f'Asset {index} non-existing')
            continue

        print(f'Removing asset {index} created by {creator:s}')
        if creator!=Addr:
            utxn=AssetCloseOutTxn(sender=Addr,sp=params,receiver=creator,index=index)
        else:
            if algodClient.asset_info(index)['params']['total']==getAmountAssetFromAddrIndex(Addr,index,algodClient):
                print(f'\tCreator holding all assets')
                utxn=AssetDestroyTxn(sender=Addr,sp=params,index=index)
            else:
                print(f'\tCreator not holding all assets')
                continue
        stxn=utxn.sign(SK)
        txId=algodClient.send_transaction(stxn)
        try:
            wait_for_confirmation(algodClient,txId,4)  
        except Exception as err:
            print(f'Error in {txId}')
            continue
        print(txId)


if __name__=='__main__':
    MnemFile="Accounts/Frank/Frank.mnem"
  
    removeAllAssets(MnemFile)
