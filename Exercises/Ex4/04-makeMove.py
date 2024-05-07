import sys
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud"
algodToken=""

def getSKAddr(MnemFile):
    with open(MnemFile,'r') as f:
        Mnem=f.read()
    SK=mnemonic.to_private_key(Mnem)
    Addr=account.address_from_private_key(SK)
    return [SK,Addr]

# utility function for waiting on a transaction confirmation
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


def makeMove(MnemFile,DealerFile,index,move,algodClient):

    params=algodClient.suggested_params()

    with open(MnemFile,'r') as f:
        Mnem=f.read()
    SK=mnemonic.to_private_key(Mnem)
    Addr=account.address_from_private_key(SK)

    with open(DealerFile,'r') as f:
        Dealer=f.read()

    appArgs=[move.to_bytes(8,'big')]
    
    feeForDealer=10_000
    ptxn=transaction.PaymentTxn(sender=Addr,sp=params,receiver=Dealer,amt=feeForDealer)
    mtxn=transaction.ApplicationNoOpTxn(Addr,params,index,appArgs)
    gid=transaction.calculate_group_id([ptxn, mtxn])

    ptxn.group=gid
    sptxn=ptxn.sign(SK)

    mtxn.group=gid
    smtxn=mtxn.sign(SK)
    
    atomic=[sptxn,smtxn]
    
    txId=algodClient.send_transactions(atomic)
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)
    print("Nim on Algorand")
    print("Player with address: ",Addr)
    print("\tMove:              ",move)
    print("\tInstance:          ",index)


if __name__=='__main__':
    if len(sys.argv)!=5:
        print("usage: python3 "+sys.argv[0]+" <player mnem> <dealer addr> <app index> <move>")
        exit()

    MnemFile=sys.argv[1]
    DealerFile=sys.argv[2]
    index=int(sys.argv[3])
    move=int(sys.argv[4])
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    makeMove(MnemFile,DealerFile,index,move,algodClient)
    