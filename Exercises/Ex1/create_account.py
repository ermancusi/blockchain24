"""
Esercizio 1
Creare un indirizzo algorand ed inviare 1 Algo all'indirizzo per l'esame mediante una transazione di 
pagamento con firma singola che riporti come nota la stringa “Ex. 1” seguita dal numero di matricola 
dello studente.
"""

import sys
from algosdk import account, mnemonic
import sys
from algosdk import account, mnemonic


def create_address (accountName): 
    privateKey, address = account.generate_account()

    with open(accountName+".addr",'w') as f:
        f.write(address)

    with open(accountName+".mnem",'w') as f:
        f.write(mnemonic.from_private_key(privateKey))

    return privateKey, address



if __name__=='__main__':
    if (len(sys.argv)!=2):
        print("Usage: "+sys.argv[0]+" <account name>")
        exit()

    accountName = sys.argv[1]    

    privateKey, address = create_address(accountName)  

    with open("Account/"+accountName+".addr",'w') as f:
        f.write(address)
        
    with open("Account/"+accountName+".mnem",'w') as f:
        f.write(mnemonic.from_private_key(privateKey))


    print("Address Created!\n")

        

