from algosdk.transaction import ApplicationUpdateTxn
from algosdk.v2client import algod
from utilities import wait_for_confirmation, getSKAddr
import base64

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def update_application(mnemFile, app_id, approvalFile):
    """
    The function `update_application` compiles and sends an update transaction for an Algorand smart
    contract application.
    
    :param MnemFile: The `MnemFile` parameter is used to specify the file containing the mnemonic phrase of the founder.
    :param appId: The `appId` parameter is used to specify the application ID that the founder wants to update.

    :param approvalFile: The `approvalFile` parameter in the `update_application` function is a file
    path that contains the source code for the updated approval program.

    :return: The function `update_application` is returning the transaction ID (`txid`) of the
    transaction that was sent to update the application on the Algorand blockchain.
    """
    # Get the suggested transaction parameters
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    private_key,sender=getSKAddr(mnemFile)


    # Create the update application transaction
    with open(approvalFile,'r') as f:
        approvalProgramSource=f.read()

    approvalProgramResponse=algodClient.compile(approvalProgramSource)
    approvalProgram=base64.b64decode(approvalProgramResponse['result'])

    clearProgramSource=b"""#pragma version 4"""
    clearProgramResponse=algodClient.compile(clearProgramSource.decode('utf-8'))
    clearProgram=base64.b64decode(clearProgramResponse['result'])


    # Create the transaction
    txn = ApplicationUpdateTxn(
        sender=sender,
        sp=params,
        index=app_id,
        approval_program=approvalProgram,
        clear_program=clearProgram
    )

    # Sign the transaction
    signed_txn = txn.sign(private_key)

    # Send the transaction
    txid = algodClient.send_transaction(signed_txn)
    print(f"Transaction ID: {txid}")

    # Wait for the transaction to be confirmed
    try:
        wait_for_confirmation(algodClient, txid, 4)
        print(f"Transaction confirmed")
    except Exception as err:
        print(f"Failed to confirm transaction: {err}")

    return txid

if __name__ == "__main__":
    mnemFile="Accounts/Alice/Alice.mnem"
    app_id=0
    with open("AppID.txt", 'r') as file:
        app_id = int(file.read())

    approvalFile="daoUpdated.teal"

    update_application(mnemFile, app_id, approvalFile)
