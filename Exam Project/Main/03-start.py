from utilities import wait_for_confirmation, getSKAddr
from algosdk.transaction import ApplicationNoOpTxn, PaymentTxn, calculate_group_id
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def startApp(mnemFile,index):

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()

    SK,Addr=getSKAddr(mnemFile)
    print("User address:    ",Addr)

   
    appAddr=e.encode_address(e.checksum(b'appID'+index.to_bytes(8, 'big')))
    ptxn=PaymentTxn(Addr,params,appAddr,2_000_000)

  
    ctxn=ApplicationNoOpTxn(sender=Addr,sp=params,index=index,app_args=["start".encode()])

    gid=calculate_group_id([ptxn,ctxn])
    ctxn.group=gid
    ptxn.group=gid
    
    sptxn=ptxn.sign(SK)
    sctxn=ctxn.sign(SK)
    txId=algodClient.send_transactions([sptxn,sctxn])
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)


if __name__=='__main__':
    MnemFile="Accounts/Alice/Alice.mnem"
    index=0
    with open("AppID.txt", 'r') as file:
        index = int(file.read())

    
    startApp(MnemFile,index)
    
