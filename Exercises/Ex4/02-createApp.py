import sys
import base64
import algosdk.encoding as e
from algosdk.v2client import algod
from algosdk.transaction import write_to_file, ApplicationCreateTxn, OnComplete, StateSchema
from algosdk import mnemonic, account

algodAddress="https://testnet-api.algonode.cloud"
algodToken=""

def getSKAddr(MnemFile):
    with open(MnemFile,'r') as f:
        Mnem=f.read()
    SK=mnemonic.to_private_key(Mnem)
    Addr=account.address_from_private_key(SK)
    return [SK,Addr]

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

def compile_program(client: algod.AlgodClient, source_code: str):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])

def main(creatorMnemFile,approvalFile,algodClient):

    creatorSK,creatorAddr=getSKAddr(creatorMnemFile)
    print(f'{"Creator address: ":32s}{creatorAddr:s}')

    on_complete=OnComplete.NoOpOC.real

    # declare application state storage (immutable)
    # define global schema
    global_ints=5
    global_bytes=1
    globalSchema=StateSchema(global_ints,global_bytes)

    # define local schema
    local_ints=3
    local_bytes=1
    localSchema=StateSchema(local_ints,local_bytes)

    print(f'{"Compiling the clear program:"}')
    with open("TEAL/clear.teal",'r') as f:
        clearProgramSource=f.read()
    compile_response=algodClient.compile(clearProgramSource)
    clearProgram=base64.b64decode(compile_response["result"])
    
    print(f'{"Reading approval file:":32s}{approvalFile:s}')
    with open(approvalFile,'r') as f:
        approvalProgramSource=f.read()
    print(f'{"Compiling approval file:":32s}')
    approvalProgramResponse=algodClient.compile(approvalProgramSource)
    approvalProgram=base64.b64decode(approvalProgramResponse['result'])

    params=algodClient.suggested_params()
    utx=ApplicationCreateTxn(
        creatorAddr,
        params,
        OnComplete.NoOpOC,
        approval_program=approvalProgram,
        clear_program=clearProgram,
        global_schema=globalSchema,
        local_schema=localSchema,
    )
    write_to_file([utx],"TX/create.utx")


    stx=utx.sign(creatorSK)
    write_to_file([stx],"TX/create.stx")

    txId=stx.transaction.get_txid()
    print(f'{"Transaction id:":32s}{txId:s}')
    txId=algodClient.send_transactions([stx])
    wait_for_confirmation(algodClient,txId,4)
    txResponse=algodClient.pending_transaction_info(txId)
    appId=txResponse['application-index']
    print(f'{"App id:":32s}{appId:d}');
    appaddr=e.encode_address(e.checksum(b'appID'+appId.to_bytes(8, 'big')))
     
    print(f'{"App address:":32s}{appaddr:32}')

if __name__=='__main__':
    if len(sys.argv)!=3:
        print("usage: python3 "+sys.argv[0]+" <creator mnem> <approval file>")
        exit()

    creatorMnemFile=sys.argv[1]
    approvalFile=sys.argv[2]
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    main(creatorMnemFile,approvalFile,algodClient)

    

    
