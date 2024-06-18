import os
import json
import base64
import random
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.transaction import Multisig, MultisigTransaction, PaymentTxn, write_to_file

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


def list_subfolders(path):
    subfolders = []
    # List all contents of the directory
    contents = os.listdir(path)
    # Iterate through each item in the directory
    for item in contents:
        # Check if the item is a directory
        if os.path.isdir(os.path.join(path, item)):
            subfolders.append(item)
    return subfolders

def multiPayTX(mnems, mSig, rAddr, amount, algodClient, enrollmentNumber):
    if len(mnems)<mSig.threshold:
        print("Error")
        exit()

    # build transaction
    params = algodClient.suggested_params()
    note = "Ex. 2 " + enrollmentNumber
    note = note.encode()

    mAddr=mSig.address()

    #create transaction
    unsignedTx=PaymentTxn(mAddr,params,rAddr,amount,None,note)
    write_to_file([unsignedTx],"Transaction/MultiPay.utx")
    mTx=MultisigTransaction(unsignedTx,mSig)
    write_to_file([mTx],"Transaction/MultiPayWithPK.utx")

    # sign transaction
    for i in range(mSig.threshold):
        sk=mnemonic.to_private_key(mnems[i])
        mTx.sign(sk)
        
    write_to_file([mTx],"Transaction/MultiPay.stx")

    # submit transaction
    txid=algodClient.send_transaction(mTx)
    print()
    print(f'{"Signed transaction with txID:":31s}{txid:s}')
    print()

    # wait for confirmation 
    try:
        confirmed_txn=wait_for_confirmation(algodClient,txid,4)  
    except Exception as err:
        print(err)
        return

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=2)))
    decodedNote=base64.b64decode(confirmed_txn["txn"]["txn"]["note"]).decode()
    print()
    print(f'{"Decoded note:":17s}{decodedNote:s}')
    

def main():

    amount=1_000_000
    version=1
    threshold=3
    accountPath = "Accounts"
    receiverAddress="VRGBBHHZX6K5F4LO5DBDWJAWQPGSWKCRIIEEWZXLLR6HNE7ZDLPYAFGFWE"
    receiverAddress="P5DMG5UCQKSBVYQRJ5S6WLWVDQDVWEFNFXSEEUIDPFNFH4Q7VFYGDSGAAE" #test address
    enrollmentNumber="1111111111"

    # Get list of available accounts
    filenames = list_subfolders(accountPath)
    filenames.sort()
    
    accounts=[]
    for filename in filenames:
        with open(accountPath+"/"+filename+"/"+filename+".addr",'r') as f:
            acc=f.read()
        accounts.append(acc)
            

    mSig=Multisig(version, threshold, accounts)
    print(f'{"Multisig Address: ":31s}{mSig.address():s}')
    print()

    mnems=[]
    for filename in filenames:
        with open(accountPath+"/"+filename+"/"+filename+".mnem",'r') as f:
            mnem=f.read()
        mnems.append(mnem)

    #random.sample uses sampling without replacement, i.e., it will not repeat the same mnemonic in the new mnems list
    mnems = random.sample(mnems, threshold) 

    
    algodClient = algod.AlgodClient(algodToken,algodAddress)
    account_info=algodClient.account_info(mSig.address())
    balance=account_info.get('amount')
    print(f'{"Multisig account balance:":31s}{balance:9d}{" microAlgos"}')

    multiPayTX(mnems, mSig, receiverAddress, amount, algodClient,enrollmentNumber)

    account_info=algodClient.account_info(mSig.address())
    balance=account_info.get('amount')
    print(f'{"Balance of the Multisig account after the transaction:":17s}{balance:9d}{" microAlgos"}')

if __name__=='__main__':
    main()
