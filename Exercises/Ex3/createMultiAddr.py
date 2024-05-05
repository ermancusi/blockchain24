import sys
from algosdk.transaction import Multisig

def createMultiSig(accounts,outputFileName):
    version=1   #multisig version
    threshold=3 #how many signatures are necessary

    msig=Multisig(version,threshold,accounts)
    maddr=msig.address()
    
    print()
    print(f'{"Multisig Address:":20s}{maddr:s}')
    print("\nConsisting of accounts: ")

    for addr in accounts:
        print(f'{"":20s}{addr:s}')   
    print()            
    print(f'{"with threshold:":20s}{threshold:d}')

    with open(outputFileName+".addr",'w') as f:
        f.write(maddr)

if __name__=='__main__':
    if len(sys.argv)!=6:
        print("usage: python",sys.argv[0]," <file P1 addr path> <file P2 addr path> <file P3 addr path> <file P4 addr path> <file Multi addr path>")
        exit()

    accounts=[]

    for filename in sys.argv[1:5]:
        with open(filename,'r') as f:
            account=f.read()
        accounts.append(account)

    outputFileName=sys.argv[5]

    createMultiSig(accounts, outputFileName)

