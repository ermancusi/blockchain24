import sys
from algosdk import account, mnemonic
import sys
import json
import base64
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn, write_to_file

algodAddress="https://testnet-api.algonode.cloud"
algodToken="" #The above test algo node does not require a token

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

def payTX(sKey,sAddr,rAddr,amount,algodClient, note):

    params = algodClient.suggested_params()

    unsignedTx=PaymentTxn(
        sender=sAddr,
        sp=params,
        receiver=rAddr,
        amt=amount,
        note=note,
    )
    write_to_file([unsignedTx],"Transaction/Pay.utx")

    signedTx=unsignedTx.sign(sKey)
    write_to_file([signedTx],"Transaction/Pay.stx")

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



if __name__=='__main__':
    if (len(sys.argv)!=2):
        print("Usage: "+sys.argv[0]+" <path of the sender's mnem>")
        exit()

    senderMnemonicPath=sys.argv[1]
    receiverAddr="VRGBBHHZX6K5F4LO5DBDWJAWQPGSWKCRIIEEWZXLLR6HNE7ZDLPYAFGFW"
    receiverAddr="P5DMG5UCQKSBVYQRJ5S6WLWVDQDVWEFNFXSEEUIDPFNFH4Q7VFYGDSGAAE" #test address
    
    enrollmentNumber = "1111111111"      
    amountToTransfer=1_000_000

    
    
    algodClient = algod.AlgodClient(algodToken, algodAddress)

    with open(senderMnemonicPath,'r') as f:
        passphrase=f.read()

    senderSK=mnemonic.to_private_key(passphrase)
    senderAddr=account.address_from_private_key(senderSK)

 

    print(f'{"Sender address:":32s}{senderAddr:s}')
    print(f'{"Receiver address:":32s}{receiverAddr:s}')

    
    balance=algodClient.account_info(senderAddr).get('amount')
    print(f'{"Account balance:":32s}{balance} microAlgos')

    if (amountToTransfer<=balance):
        payTX(senderSK,senderAddr,receiverAddr,amountToTransfer,algodClient,bytes("Ex. 1 " + enrollmentNumber, 'utf-8'))
        print("\nTransaction Executed!")
    else:
        print("Insufficient Funds")

        




