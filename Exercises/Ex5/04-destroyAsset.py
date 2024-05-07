import sys
import json
from algosdk.v2client import algod
from algosdk import transaction 
from algosdk.transaction import AssetConfigTxn
from algosdk import account, mnemonic

algodAddress="https://testnet-api.algonode.cloud"
algodToken=""

def getSKAddr(MnemFile):
    with open(MnemFile,'r') as f:
        Mnem=f.read()
    SK=mnemonic.to_private_key(Mnem)
    Addr=account.address_from_private_key(SK)
    return [SK,Addr]

def wait_for_confirmation(client,transaction_id,timeout):
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return 
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:  
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)                   
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))



def destroyAsset(managerMNEMFile,assetID,algodClient):

    params=algodClient.suggested_params()
    managerSK,managerADDR=getSKAddr(managerMNEMFile)

    txn=AssetConfigTxn(sender=managerADDR,
                       sp=params,
                       index=assetID,
                       strict_empty_address_check=False)
    transaction.write_to_file([txn],"TX/04-assetDestroy.utxn")
    stxn=txn.sign(managerSK)
    txid=algodClient.send_transaction(stxn)
    print(f'{"TX id:":32s}{txid:s}')
    transaction.write_to_file([stxn],"TX/04-assetDestroy.stxn")

    try:
        confirmed_txn=wait_for_confirmation(algodClient,txid,4)  
    except Exception as err:
        print(err)
        return

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))

    return 
    

if __name__=="__main__":
    if (len(sys.argv)!=3):
        print("Usage: python",sys.argv[0],"<manager MNEM file> <asset ID>")
        exit()

    managerMNEMFile=sys.argv[1]
    assetID=sys.argv[2]
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    destroyAsset(managerMNEMFile,assetID,algodClient)

