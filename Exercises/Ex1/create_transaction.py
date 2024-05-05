"""
Esercizio 1
Creare un indirizzo algorand ed inviare 1 Algo all'indirizzo per l'esame mediante una transazione di 
pagamento con firma singola che riporti come nota la stringa “Ex. 1” seguita dal numero di matricola 
dello studente.
"""

import sys
from algosdk import account, mnemonic
import sys
import json
import base64
from utilities import algodAddress, algodToken, wait_for_confirmation
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn, write_to_file


def payTX(sKey,sAddr,rAddr,amount,algodClient, enrollmentNumber,note):

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
    if (len(sys.argv)!=3):
        print("Usage: "+sys.argv[0]+" <path of the sender's mnem> <path of the receiver's addr>")
        exit()

    senderMnemonicPath=sys.argv[1]
    receiverAddr=sys.argv[2]
    
    enrollmentNumber = "0622701668"      
    amountToTransfer=1_000_000

    
    
    algodClient = algod.AlgodClient(algodToken, algodAddress)

    with open(senderMnemonicPath,'r') as f:
        passphrase=f.read()

    senderSK=mnemonic.to_private_key(passphrase)
    senderAddr=account.address_from_private_key(senderSK)

    with open(receiverAddr,'r') as f:
        rAddr=f.read()

    print(f'{"Sender address:":32s}{senderAddr:s}')
    print(f'{"Receiver address:":32s}{rAddr:s}')

    
    balance=algodClient.account_info(senderAddr).get('amount')
    print(f'{"Account balance:":32s}{balance} microAlgos')

    if (amountToTransfer<=balance):
        payTX(senderSK,senderAddr,rAddr,amountToTransfer,algodClient,enrollmentNumber,bytes("Ex. 1 " + enrollmentNumber, 'utf-8'))
        print("\nTransaction Executed!")
    else:
        print("Insufficient Funds")

        

