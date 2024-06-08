import sys
import base64
from utilities import wait_for_confirmation, getSKAddr
from algosdk.transaction import ApplicationCreateTxn, OnComplete, StateSchema
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens


def main(creatorMnemFile,approvalFile):

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()

    creatorSK,creatorAddr=getSKAddr(creatorMnemFile)
    print("Creator address: ",creatorAddr)


    # declare application state storage (immutable)
    # define global schema
    global_ints=7
    global_bytes=2
    globalSchema=StateSchema(global_ints,global_bytes)

    # define local schema
    local_ints=0
    local_bytes=0
    localSchema=StateSchema(local_ints,local_bytes)

    clearProgramSource=b"""#pragma version 4"""
    clearProgramResponse=algodClient.compile(clearProgramSource.decode('utf-8'))
    clearProgram=base64.b64decode(clearProgramResponse['result'])
    
    with open(approvalFile,'r') as f:
        approvalProgramSource=f.read()

    approvalProgramResponse=algodClient.compile(approvalProgramSource)
    approvalProgram=base64.b64decode(approvalProgramResponse['result'])

    on_complete=OnComplete.NoOpOC.real
    utxn=ApplicationCreateTxn(creatorAddr,params,on_complete, \
                                        approvalProgram,clearProgram, \
                                        globalSchema,localSchema)
    stxn=utxn.sign(creatorSK)

    txId=stxn.transaction.get_txid()
    print("Transaction id:  ",txId)
    algodClient.send_transactions([stxn])
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)
    appId=txResponse['application-index']
    print("App id:          ",appId)
    print("App address:     ",e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big'))))

if __name__=='__main__':
    if len(sys.argv)!=3:
        print("usage: python3 "+sys.argv[0]+" <creator mnem> <approval file>")
        exit()

    creatorMnemFile=sys.argv[1]
    approvalFile=sys.argv[2]
    

    main(creatorMnemFile,approvalFile)
    
    
