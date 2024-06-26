import base64
from utilities import wait_for_confirmation, getSKAddr
from algosdk.transaction import ApplicationCreateTxn, OnComplete, StateSchema
import algosdk.encoding as e
from algosdk.v2client import algod

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens


def main(creatorMnemFile,approvalFile):
    """
    The `main` function deploys an Algorand smart contract application using specified
    approval and clear programs, and then writes the application ID to a file.
    
    :param creatorMnemFile: The `creatorMnemFile` parameter is a file containing the mnemonic phrase
    of the creator's Algorand account. This mnemonic phrase is used to derive the private
    key and address of the creator's account for signing transactions
    :param approvalFile: The `approvalFile` parameter in the `main` function is a file path that
    contains the source code for the approval program. This file is read to compile the approval program
    that will be used in creating an Algorand smart contract application
    """

    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()

    creatorSK,creatorAddr=getSKAddr(creatorMnemFile)
    print("Creator address: ",creatorAddr)


    global_ints=12
    global_bytes=2
    globalSchema=StateSchema(global_ints,global_bytes)

    
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
    
    with open("AppID.txt", 'w') as file:
        file.write(str(appId))
    print(f"Successfully wrote appId '{appId}' to AppID.txt")
        
    print("App id:          ",appId)
    print("App address:     ",e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big'))))

if __name__=='__main__':
    creatorMnemFile="Accounts/Alice/Alice.mnem"
    approvalFile="dao.teal"
    

    main(creatorMnemFile,approvalFile)
    
    
