import sys
from algosdk.transaction import ApplicationDeleteTxn
from utilities import wait_for_confirmation, getSKAddr
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def deleteApp(MnemFile,appId):

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    SK,Addr=getSKAddr(MnemFile)


    print("User addr:",Addr)

    appAddr=e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big')))
    accountInfo=algodClient.account_info(appAddr)
    print("App id:   ",appId)
    print("App addr: ",appAddr)
    
    utxn=ApplicationDeleteTxn(sender=Addr,sp=params,index=appId,foreign_assets=[106902214,106902215,106903591,106903592])
    stxn=utxn.sign(SK)
    txId=stxn.transaction.get_txid()
    print("Tx id:    ",txId)
    algodClient.send_transactions([stxn])
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)
    print("Deleted:  ",txResponse['txn']['txn']['apid'])  


if __name__=='__main__':
    if len(sys.argv)!=3:
        print("usage: python3 "+sys.argv[0]+" <mnem> <app index>")
        exit()

    MnemFile=sys.argv[1]
    appId=int(sys.argv[2])

    deleteApp(MnemFile,appId)
    
    
