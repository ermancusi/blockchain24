import sys
from algosdk.transaction import ApplicationClearStateTxn
from algosdk import transaction
from utilities import wait_for_confirmation, getSKAddr
from daoutilities import getAllApps
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def main(MnemFile): 
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
    if len(sys.argv)!=2:
        print("usage: python3 "+sys.argv[0]+" <mnem>")
        exit()

    MnemFile=sys.argv[1]

    main(MnemFile)
    
    
