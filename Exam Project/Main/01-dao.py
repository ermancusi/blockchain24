from pyteal import *
from daoutilities import DAOtokenName, DAOGovName

cmd=ScratchVar(TealType.bytes)
total_DAO_token_assets=1_000_000
threshold1=int(total_DAO_token_assets * 1/2)
threshold2=int(total_DAO_token_assets * 3/4)
total_DAO_token_assets=Int(total_DAO_token_assets)
total_Gov_token_assets=Int(3)


def handle_start():     
    """
    The function `handle_start` creates and configures two new assets, i.e., Asset_UniSA and Token_Gov.
    :return: The function `handle_start` is returning a logic block that creates and configures two new assets and stores their asset IDs in global state. If the conditions are not met, it
    rejects the transaction.
    """
    h_start=If(And(Global.group_size()==Int(2),
                        Gtxn[0].type_enum()==TxnType.Payment,
                        Gtxn[0].receiver()==Global.current_application_address(),
                        Gtxn[0].amount()>=Int(500_000),
                    )).Then(
                         Seq([
                            InnerTxnBuilder.Begin(),
                            InnerTxnBuilder.SetFields({
                                TxnField.type_enum: TxnType.AssetConfig,                                
                                TxnField.config_asset_total: total_DAO_token_assets,
                                TxnField.config_asset_decimals: Int(0),
                                TxnField.config_asset_name: Bytes(DAOtokenName),
                                TxnField.config_asset_unit_name: Bytes("Asset"),
                                TxnField.config_asset_url: Bytes("https://www.diem.unisa.it/"),
                                TxnField.config_asset_manager: Global.current_application_address(),
                                TxnField.config_asset_reserve: Global.current_application_address(),
                                TxnField.config_asset_freeze: Global.current_application_address(),
                                TxnField.config_asset_clawback: Global.current_application_address()
                                }),
                                InnerTxnBuilder.Submit(),
                                App.globalPut(Bytes("assetIDToken"),InnerTxn.created_asset_id()),
                            InnerTxnBuilder.Begin(),
                            InnerTxnBuilder.SetFields({
                                TxnField.type_enum: TxnType.AssetConfig,
                                TxnField.config_asset_total: total_Gov_token_assets,
                                TxnField.config_asset_decimals: Int(0),
                                TxnField.config_asset_unit_name: Bytes("Token"),
                                TxnField.config_asset_name: Bytes(DAOGovName),
                                TxnField.config_asset_url: Bytes("https://web.unisa.it/"),
                                TxnField.config_asset_manager: Global.current_application_address(),
                                TxnField.config_asset_reserve: Global.current_application_address(),
                                TxnField.config_asset_freeze: Global.current_application_address(),
                                TxnField.config_asset_clawback: Global.current_application_address()
                            }),
                            InnerTxnBuilder.Submit(),
                            App.globalPut(Bytes("assetIDGov"),InnerTxn.created_asset_id()),
                            Approve()
                        ])).Else(Reject())
    return h_start

def handle_priceTok(prefix):
    """
    This function handles updating a price (sell or buy) and executing an asset transfer transaction based on
    certain conditions.
    
    :param prefix: The `prefix` parameter is a string which can be equal to "b" if it is a buy price update; equal to "s" if it is a sell price update. 
    :return: The `handle_priceTok` function is returning a sequence of operations that handle the price update logic for a token. The function checks certain conditions related to the token price and proposer, updates global state variables accordingly, performs an asset transfer, and then approves the transaction.
    """
    return Seq([
        If(Or(
           App.globalGet(Bytes(prefix+"pprice"))==Int(0),
           Btoi(Gtxn[1].application_args[1])!=App.globalGet(Bytes(prefix+"pprice")),
           Txn.sender()==App.globalGet(Bytes(prefix+"proposer"))
        )).
        Then(Seq([App.globalPut(Bytes(prefix+"pprice"),Btoi(Gtxn[1].application_args[1])),
                  App.globalPut(Bytes(prefix+"proposer"),Gtxn[1].sender())])).
        Else(Seq([App.globalPut(Bytes(prefix+"pprice"),Int(0)),
                  App.globalPut(Bytes(prefix+"currentPrice"),Btoi(Gtxn[1].application_args[1]))])),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_receiver: Txn.sender(),
            TxnField.asset_amount: Int(1),
            TxnField.xfer_asset: App.globalGet(Bytes("assetIDGov"))
        }),
        InnerTxnBuilder.Submit(),
        Approve()])

def handle_price(prefix):
    """
    The function `handle_price` checks certain conditions and calls `handle_priceTok(prefix)` if the
    conditions are met, otherwise it rejects the transaction.
    
    :param prefix: The `handle_price` function takes a `prefix` parameter as input. This parameter is
    used within the function to call the `handle_priceTok` function with the provided `prefix` value.
    The `prefix` parameter is a string which can be equal to "b" if it is a buy price update; equal to "s" if it is a sell price update.
    :return: The function `handle_price` is returning a sequence (`Seq`) that contains a conditional
    statement that checks if certain conditions are met using and, if so, it calls the function `handle_priceTok(prefix)`, otherwise it rejects the transaction.
    """
    h_price=Seq([
           If(And(Global.group_size()==Int(2),
                  Gtxn[0].type_enum()==TxnType.AssetTransfer,
                  Gtxn[0].asset_receiver()==Global.current_application_address(),
                  Gtxn[0].asset_amount()>=Int(1),
                  Gtxn[0].xfer_asset()==App.globalGet(Bytes("assetIDGov")))
           ).Then(handle_priceTok(prefix)).Else(Reject())])
    return h_price

def approval_program(Alice,Bob,Charlie):
    """
    The function `approval_program` defines the logic for handling different transaction scenarios in an
    Algorand smart contract application. The program defines different actions such as creating assets, opting in, closing out, updating the application, deleting the application, buying assets, selling assets, and handling no-op

    :param Alice: Alice is a variable representing a participant in the approval program
    :param Bob: Bob is a variable representing a participant in the approval program
    :param Charlie: Charlie is a variable representing a participant in the approval program
    
    :return: The `approval_program` function returns the compiled TEAL code for an Algorand smart contract application.
    """
    handle_creation=Seq([
                    App.globalPut(Bytes("bpprice"),Int(0)),                    
                    App.globalPut(Bytes("bcurrentPrice"),Int(900_000)),
                    App.globalPut(Bytes("spprice"),Int(0)),                    
                    App.globalPut(Bytes("scurrentPrice"),Int(1_000_000)),
                    App.globalPut(Bytes("assetIDGov"),Int(0)),
                    App.globalPut(Bytes("assetIDToken"),Int(0)),
                    App.globalPut(Bytes("assetSold"),Int(0)),
                    App.globalPut(Bytes("bproposer"),Alice),
                    App.globalPut(Bytes("sproposer"),Alice),
                    App.globalPut(Bytes("flagTh1"),Int(0)),
                    App.globalPut(Bytes("flagTh2"),Int(0)),
                    Approve()])

    handle_optin=If(Or(Txn.sender()==Alice,
                       Txn.sender()==Bob,
                       Txn.sender()==Charlie)).Then(
                    Seq([
                            InnerTxnBuilder.Begin(),
                            InnerTxnBuilder.SetFields({
                                TxnField.type_enum: TxnType.AssetTransfer,
                                TxnField.asset_receiver: Txn.sender(),
                                TxnField.asset_amount: Int(1),
                                TxnField.xfer_asset: App.globalGet(Bytes("assetIDGov"))
                            }),
                            InnerTxnBuilder.Submit(),
                            Approve()
                    ])).Else(Approve())

    handle_closeout=Approve()

    handle_updateapp=If(Or(Txn.sender()==Alice,
                           Txn.sender()==Bob,
                           Txn.sender()==Charlie)).Then(Approve()).Else(Reject())

    handle_deleteapp=If(Or(Txn.sender()==Alice,
                           Txn.sender()==Bob,
                           Txn.sender()==Charlie)).Then(
                             Seq([
                                InnerTxnBuilder.Begin(),
                                    InnerTxnBuilder.SetFields({
                                        TxnField.type_enum: TxnType.AssetConfig,
                                        TxnField.config_asset: App.globalGet(Bytes("assetIDGov"))
                                    }),
                                InnerTxnBuilder.Submit(),
                                InnerTxnBuilder.Begin(),
                                    InnerTxnBuilder.SetFields({
                                        TxnField.type_enum: TxnType.AssetConfig,
                                        TxnField.config_asset: App.globalGet(Bytes("assetIDToken"))
                                    }),
                                InnerTxnBuilder.Submit(),
                                InnerTxnBuilder.Begin(),
                                    InnerTxnBuilder.SetFields({
                                        TxnField.type_enum: TxnType.Payment,
                                        TxnField.amount: Int(0),
                                        TxnField.receiver: Alice,
                                        TxnField.close_remainder_to: Alice,
                                    }),
                                InnerTxnBuilder.Submit(),
                                Approve()])).Else(Reject())

    handle_buy=If(And(Global.group_size()==Int(2),
                  Gtxn[0].type_enum()==TxnType.Payment,
                  Gtxn[0].receiver()==Global.current_application_address(),
                  Gtxn[0].amount()>=Btoi(Gtxn[1].application_args[1])*App.globalGet(Bytes("bcurrentPrice")))
            ).Then(
                    Seq([App.globalPut(Bytes("assetSold"), App.globalGet(Bytes("assetSold")) + Int(1)),
                        If(
                            And(App.globalGet(Bytes("assetSold")) >= Int(threshold1), App.globalGet(Bytes("flagTh1")) == Int(0), App.globalGet(Bytes("assetSold")) < Int(threshold2))
                        ).Then(
                            Seq([App.globalPut(Bytes("bcurrentPrice"), App.globalGet(Bytes("bcurrentPrice")) * Int(2)),
                            App.globalPut(Bytes("flagTh1"), App.globalGet(Bytes("flagTh1")) + Int(1)),
                            ])
                        ),
                        If(
                            And(App.globalGet(Bytes("flagTh2")) == Int(0), App.globalGet(Bytes("assetSold")) >= Int(threshold2))
                        ).Then(
                            Seq([App.globalPut(Bytes("bcurrentPrice"), App.globalGet(Bytes("bcurrentPrice")) * Int(2)),
                                 App.globalPut(Bytes("flagTh2"), App.globalGet(Bytes("flagTh2")) + Int(1)),
                            ])
                        ),
                     InnerTxnBuilder.Begin(),
                     InnerTxnBuilder.SetFields({
                         TxnField.type_enum: TxnType.AssetTransfer,
                         TxnField.asset_receiver: Txn.sender(),
                         TxnField.asset_amount: Btoi(Gtxn[1].application_args[1]),
                         TxnField.xfer_asset: App.globalGet(Bytes("assetIDToken"))
                      }),
                      InnerTxnBuilder.Submit(),
                      Approve()
            ])

            ).Else(Reject())
    
    handle_sell= If(And(Global.group_size() == Int(2),
                  Gtxn[0].type_enum() == TxnType.AssetTransfer,
                  Gtxn[0].asset_receiver() == Global.current_application_address(),
                  Gtxn[0].xfer_asset() == App.globalGet(Bytes("assetIDToken")),
                  Gtxn[0].asset_amount() >= Btoi(Gtxn[1].application_args[1])
                  )
              ).Then(
                  Seq([
                      InnerTxnBuilder.Begin(),
                      InnerTxnBuilder.SetFields({
                          TxnField.type_enum: TxnType.Payment,
                          TxnField.receiver: Txn.sender(),
                          TxnField.amount: Btoi(Gtxn[1].application_args[1]) * App.globalGet(Bytes("scurrentPrice"))
                      }),
                      InnerTxnBuilder.Submit(),
                      Approve()
                  ])
              ).Else(Reject())


    handle_noop=Seq([
                cmd.store(Txn.application_args[0]),
                Cond([cmd.load()==Bytes("sp"), handle_price("s")],
                     [cmd.load()==Bytes("bp"), handle_price("b")],
                     [cmd.load()==Bytes("buy"),  handle_buy],
                     [cmd.load()==Bytes("sell"), handle_sell],
                     [cmd.load()==Bytes("start"),  handle_start()]
                ),Approve()]
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion()  == OnComplete.OptIn, handle_optin],
        [Txn.on_completion()  == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion()  == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion()  == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion()  == OnComplete.NoOp, handle_noop]
    )

    return compileTeal(program, Mode.Application, version=5)

if __name__=='__main__':
    with open("Accounts/Alice/Alice.addr") as f:
        aliceA=f.read()
    alice=Addr(aliceA)

    with open("Accounts/Bob/Bob.addr") as f:
        bobA=f.read()
    bob=Addr(bobA)
    
    with open("Accounts/Charlie/Charlie.addr") as f:
        charlieA=f.read()
    charlie=Addr(charlieA)

    program=approval_program(alice,bob,charlie)
    
    with open("dao.teal","w") as f:
        f.write(program)
