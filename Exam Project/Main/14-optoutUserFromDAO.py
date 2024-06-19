from algosdk.transaction import ApplicationCloseOutTxn
from algosdk.v2client import algod
from utilities import wait_for_confirmation, getSKAddr

algodAddress="https://testnet-api.algonode.cloud" #Algorand test node
algodToken="" #free service does not require tokens

def optOutDAO(mnemFile, app_id):
    """
    The function `optOutDAO` function is used to get users to opt-out from the DAO.
    
    :param MnemFile: The `MnemFile` parameter in the `optOutDAO` function is used to specify the file
    containing the mnemonic phrase of the user.
    :param appId: The `appId` parameter in the `optOutDAO` function is used to specify the application ID
    from which the user wants to opt out.
    """
        
    # Get the suggested transaction parameters
    algodClient=algod.AlgodClient(algodToken,algodAddress)
    params=algodClient.suggested_params()
    private_key,sender=getSKAddr(mnemFile)

    # Create the close-out application transaction
    txn = ApplicationCloseOutTxn(
        sender=sender,
        sp=params,
        index=app_id
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
    mnemFile="Accounts/Mike/Mike.mnem"
    app_id=0
    with open("AppID.txt", 'r') as file:
        app_id = int(file.read())

    approvalFile="daoUpdated.teal"

    # Close out the application using Alice's credentials
    optOutDAO(mnemFile, app_id)
