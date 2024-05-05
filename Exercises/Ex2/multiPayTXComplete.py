import random
import os
import json
import base64
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import Multisig, MultisigTransaction, PaymentTxn, write_to_file
from utilities import *

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
    receiverAddress="VRGBBHHZX6K5F4LO5DBDWJAWQPGSWKCRIIEEWZXLLR6HNE7ZDLPYAFGFW"
    receiverAddress="P5DMG5UCQKSBVYQRJ5S6WLWVDQDVWEFNFXSEEUIDPFNFH4Q7VFYGDSGAAE"
    enrollmentNumber="0622701668"

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
