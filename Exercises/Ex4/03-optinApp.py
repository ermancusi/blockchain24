import sys
import algosdk.encoding as e
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from algosdk.transaction import ApplicationOptInTxn, PaymentTxn, write_to_file


algodAddress="https://testnet-api.algonode.cloud"
algodToken=""


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


def main(MnemFile,index,algodClient):

    params=algodClient.suggested_params()

    appAddr=e.encode_address(e.checksum(b'appID'+index.to_bytes(8, 'big')))
    print(f'{"app id:":32s}{index}')
    print(f'{"app Addr:":32s}{appAddr}')

    with open(MnemFile,'r') as f:
        Mnem=f.read()

    SK=mnemonic.to_private_key(Mnem)
    playerAddr=account.address_from_private_key(SK)
    print(f'{"User address: ":32s}{playerAddr:s}')

    note="Opt in fee"
    feeForOptin=10_0000 #Change to 10_000_000

    optinReceiver="VRGBBHHZX6K5F4LO5DBDWJAWQPGSWKCRIIEEWZXLLR6HNE7ZDLPYAFGFW"
    optinReceiver=appAddr #To be deleted after testing

    payTx=PaymentTxn(playerAddr,params,optinReceiver,feeForOptin,None,note)
    optTx=ApplicationOptInTxn(playerAddr,params,index)
    gid=transaction.calculate_group_id([payTx, optTx])

    payTx.group=gid
    optTx.group=gid
    write_to_file([payTx],"TX/PayOpt.utx")
    write_to_file([optTx],"TX/Opt.utx")
    sPayTx=payTx.sign(SK)
    sOptTx=optTx.sign(SK)
    write_to_file([sPayTx],"TX/PayOpt.stx")
    write_to_file([sOptTx],"TX/Opt.stx")


    txId=algodClient.send_transactions([sPayTx,sOptTx])
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)


if __name__=='__main__':
    if len(sys.argv)!=3:
        print("usage: python3 "+sys.argv[0]+" <mnem> <app index>")
        exit()

    MnemFile=sys.argv[1]
    index=int(sys.argv[2])
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    main(MnemFile,index,algodClient)
    
    
