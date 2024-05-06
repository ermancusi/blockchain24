import sys
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import ApplicationNoOpTxn, write_to_file

algodAddress="https://testnet-api.algonode.cloud"
algodToken=""

def wait_for_confirmation(client, transaction_id, timeout):
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


def main(MnemFile, index, move, algodClient):

    params=algodClient.suggested_params()

    with open(MnemFile,'r') as f:
        Mnem=f.read()

    SK=mnemonic.to_private_key(Mnem)
    Addr=account.address_from_private_key(SK)

    print(f'{"User address: ":32s}{Addr:s}')
    print(f'{"Calling in: ":32s}{index:d}')
    print(f'{"Move: ":32s}{move:d}')

    appArgs=[move.to_bytes(8,'big')]
    utx=ApplicationNoOpTxn(Addr,params,index,appArgs)
    write_to_file([utx],"TX/move.utx")

    stx=utx.sign(SK)
    write_to_file([stx],"TX/move.stx")

    txId=stx.transaction.get_txid()
    print(f'{"Transaction id:":32s}{txId:s}')

    algodClient.send_transactions([stx])
    wait_for_confirmation(algodClient, txId, 4)
    
    txResponse=algodClient.pending_transaction_info(txId)
    idfromtx=txResponse['txn']['txn']['apid']

    print(f'{"Calling app-id: ":32s}{idfromtx:d}')  

if __name__=='__main__':
    if len(sys.argv)!=4:
        print("usage: python3 "+sys.argv[0]+" <mnem> <app index> <move>")
        exit()

    MnemFile=sys.argv[1]
    index=int(sys.argv[2])
    move=int(sys.argv[3])

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    main(MnemFile,index,move,algodClient)
    
    
