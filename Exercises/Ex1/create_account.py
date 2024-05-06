import sys
from algosdk import account, mnemonic


if __name__=='__main__':
    if (len(sys.argv)!=2):
        print("Usage: "+sys.argv[0]+" <account name>")
        exit()

    accountName = sys.argv[1]    

    privateKey, address = account.generate_account()

    with open("Account/"+accountName+".addr",'w') as f:
        f.write(address)
        
    with open("Account/"+accountName+".mnem",'w') as f:
        f.write(mnemonic.from_private_key(privateKey))


    print("Address Created!\n")

        

