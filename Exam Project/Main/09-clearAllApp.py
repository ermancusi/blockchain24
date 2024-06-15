from algosdk.transaction import ApplicationClearStateTxn
from algosdk import transaction
from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAllApps
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

"""
Make a transaction that will clear a user's state for an application
"""
def main(MnemFile): 
    """
    The main function in the Python code interacts with Algorand blockchain to remove applications
    associated with a given address.
    
    :param MnemFile: It looks like the `main` function you provided is interacting with the Algorand
    blockchain to remove applications associated with a specific address. The function seems to be using
    Algorand's Python SDK
    """
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    SK,Addr=getSKAddr(MnemFile)

    listIndex=getAllApps(Addr,algodClient)
    print(f'Found {len(listIndex)} applications for {Addr}')

    while len(listIndex)>0:
        print("Removing applications",listIndex[:15])
        utxnL=[ApplicationClearStateTxn(Addr,params,index) for index  in listIndex[:15]]
        gid=transaction.calculate_group_id(utxnL)
        for t in utxnL:
            t.group=gid
        stxnL=[t.sign(SK) for t in utxnL]
        txId=algodClient.send_transactions(stxnL)
        wait_for_confirmation(algodClient,txId,4)
        txResponse=algodClient.pending_transaction_info(txId)
        listIndex=listIndex[15:]


if __name__=='__main__':
    MnemFile="Accounts/Alice/Alice.mnem"

    main(MnemFile)
    
    
