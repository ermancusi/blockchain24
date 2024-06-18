import sys
import json
import base64
from algosdk.v2client import algod
from algosdk import transaction, account, mnemonic
from algosdk.transaction import AssetConfigTxn, PaymentTxn, write_to_file

algodAddress="https://testnet-api.algonode.cloud"
algodToken=""

AssetName="DISAMIS24"
AssetUnit="DSMS24u"


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


def createAsset(AssetName,creatorMNEMFile,managerADDRFile,algodClient):
    
    params=algodClient.suggested_params()
    creatorSK,creatorAddr=getSKAddr(creatorMNEMFile)
    
    with open(managerADDRFile,'r') as f:
        managerAddr=f.read()
    reserveAddr=managerAddr
    freezeAddr=managerAddr
    clawbackAddr=managerAddr
    
    print(f'{"Creator Addr:":32s}{creatorAddr:s}')
    print(f'{"Manager Addr:":32s}{managerAddr:s}')
    print(f'{"Reserve Addr:":32s}{reserveAddr:s}')
    print(f'{"Freeze  Addr:":32s}{freezeAddr:s}') 
    print(f'{"ClawbackAddr: ":32s}{clawbackAddr:s}')

    txn=AssetConfigTxn(
        sender=creatorAddr,
        sp=params,
        total=1000,
        default_frozen=False,
        asset_name=AssetName,
        unit_name=AssetUnit,
        manager=managerAddr,
        reserve=reserveAddr,
        freeze=freezeAddr,
        clawback=clawbackAddr,
        url="https://github.com/giuper/Blockchain24",
        decimals=0)

    transaction.write_to_file([txn],"TX/01-assetCreation.utxn")

    stxn=txn.sign(creatorSK)
    transaction.write_to_file([stxn],"TX/01-assetCreation.stxn")
    txid=algodClient.send_transaction(stxn)
    print(f'{"TX id:":32s}{txid:s}')
    
    confirmed_txn=wait_for_confirmation(algodClient,txid,4)
    try:
        ptx=algodClient.pending_transaction_info(txid)
        assetId=ptx["asset-index"]
        print(f'{"Created an asset with id:":32s}{assetId:d}')
    except Exception as e:
        print(e)

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn,indent=4)))

    return assetId

def payTX(sKey,sAddr,rAddr,amount,algodClient, note):

    params = algodClient.suggested_params()

    unsignedTx=PaymentTxn(
        sender=sAddr,
        sp=params,
        receiver=rAddr,
        amt=amount,
        note=note,
    )
    write_to_file([unsignedTx],"TX/Pay.utx")

    signedTx=unsignedTx.sign(sKey)
    write_to_file([signedTx],"TX/Pay.stx")

    txid=algodClient.send_transaction(signedTx)
    print(f'{"Signed transaction with txID:":32s}{txid:s}')
    print()

    # wait for confirmation 
    try:
        confirmed_txn=wait_for_confirmation(algodClient,txid,4)  
    except Exception as err:
        print(err)
        return

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    
    print("Decoded note: {}".format(base64.b64decode(
        confirmed_txn["txn"]["txn"]["note"]).decode()))

    account_info = algodClient.account_info(sAddr)
    print("Balance of the sender after the transaction: {} microAlgos".format(account_info.get('amount')) + "\n")

if __name__=="__main__":
    if (len(sys.argv)!=3):
        print("Usage: python3",sys.argv[0],"<creator MNEM file> <manager ADDR>")
        exit()

    creatorMNEMFile=sys.argv[1]
    managerADDRFile=sys.argv[2]

    receiverAddr="VRGBBHHZX6K5F4LO5DBDWJAWQPGSWKCRIIEEWZXLLR6HNE7ZDLPYAFGFWE"
    receiverAddr="W27AKPRFKVCPMMABW5FALBA6UUDPY2WZRV7B67WGFVIRZMUCUSH6GZGFQU"

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    assetId= createAsset(AssetName,creatorMNEMFile,managerADDRFile,algodClient)
    
    print("Asset with ID: ",str(assetId)," created successfully!")

    senderSK,senderAddr=getSKAddr(creatorMNEMFile)


    payTX(senderSK,senderAddr,receiverAddr,0,algodClient,bytes("Asset ID: " + str(assetId), 'utf-8'))

    print("Transaction Executed successfully!")

