from algosdk import account, mnemonic
import os
from algosdk import account, mnemonic


if __name__=='__main__':
    accountNames=["Alice","Bob","Charlie"]

    for accountName in accountNames:
        privateKey, address = account.generate_account()

        if not os.path.exists(accountName):
            os.makedirs(accountName)

        with open(accountName+"/"+accountName+".addr",'w') as f:
            f.write(address)
            
        with open(accountName+"/"+accountName+".mnem",'w') as f:
            f.write(mnemonic.from_private_key(privateKey))


    print("Addresses Created!\n")

        

