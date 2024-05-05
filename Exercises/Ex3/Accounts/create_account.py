"""
Esercizio 1
Creare un indirizzo algorand ed inviare 1 Algo all'indirizzo per l'esame mediante una transazione di 
pagamento con firma singola che riporti come nota la stringa “Ex. 1” seguita dal numero di matricola 
dello studente.
"""

from algosdk import account, mnemonic
import os
from algosdk import account, mnemonic


if __name__=='__main__':
    accountNames=["Alice","Bob","Charlie","Frank"]

    for accountName in accountNames:
        privateKey, address = account.generate_account()

        if not os.path.exists(accountName):
            os.makedirs(accountName)

        with open(accountName+"/"+accountName+".addr",'w') as f:
            f.write(address)
            
        with open(accountName+"/"+accountName+".mnem",'w') as f:
            f.write(mnemonic.from_private_key(privateKey))


    print("Addresses Created!\n")

        

