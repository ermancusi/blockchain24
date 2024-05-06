0. Make sure that the “Accounts” and “Transaction” folders are created (even if empty).

1. Accounts/create_account.py

2. createMultiAddr.py

3. Once you have created the MultiSig address make sure you supply it with Algo via https://bank.testnet.algorand.network/

4. It is also necessary to supply the 4 individual addresses with Algo via https://bank.testnet.algorand.network/.
   This is necessary because the one that does not sign will be randomly selected,
   so to avoid one with 0 algo being selected, it is best to waste a few seconds at the beginning to supply them all.

5. Don't forget to enter your enrollment number and the transaction ID of Ex.2

6. multiPayTXComplete.py
