import sys
from pyteal import *

t=ScratchVar(TealType.uint64)
arg=ScratchVar(TealType.uint64)
feeForOptin=10_0000
feeForDealer=10_000
feeForWinner=6_000_000 #Change to 1_000_000

examAddress="W27AKPRFKVCPMMABW5FALBA6UUDPY2WZRV7B67WGFVIRZMUCUSH6GZGFQU" #toChange

def approval_program(Alice,Bob,Dealer):
    handle_creation = Seq([
        App.globalPut(Bytes("turn"), Int(0)),
        App.globalPut(Bytes("heap"), Int(10)),
        App.globalPut(Bytes("max"), Int(5)),
        App.globalPut(Bytes("nofmoves"),Int(0)),
        Approve()
    ])
 
    handle_optin=If(And(Global.group_size()==Int(2),
                        Gtxn[0].type_enum()==TxnType.Payment,
                        Gtxn[0].receiver()==Addr(examAddress),
                        Gtxn[0].amount()>=Int(feeForOptin),
                    )).Then(Approve()).Else(Reject())
                    
    handle_closeout=If(Txn.sender()==Dealer).Then(Return(Int(1))).Else(Return(Int(0)))
    handle_updateapp=If(Txn.sender()==Dealer).Then(Return(Int(1))).Else(Return(Int(0)))
    handle_deleteapp=If(Txn.sender()==Dealer).Then(Return(Int(1))).Else(Return(Int(0)))

    handle_noop=If(Seq([arg.store(Btoi(Gtxn[1].application_args[0])),
                    And(Global.group_size()==Int(2),
                        Gtxn[0].type_enum()==TxnType.Payment,
                        Gtxn[0].receiver()==Dealer,
                        Gtxn[0].amount()>=Int(feeForDealer),
                        arg.load()<=App.globalGet(Bytes("max")),
                        arg.load()>Int(0),
                        arg.load()<=App.globalGet(Bytes("heap")),
                        Or(
                            And(Gtxn[1].sender()==Alice,App.globalGet(Bytes("turn"))==Int(0)),
                            And(Gtxn[1].sender()==Bob,App.globalGet(Bytes("turn"))==Int(1))
                          )
                    )
                ])
    ).Then(
        Seq([
            t.store(App.globalGet(Bytes("heap"))),
            App.globalPut(Bytes("heap"),Minus(t.load(),Btoi(Gtxn[1].application_args[0]))),
            t.store(App.globalGet(Bytes("turn"))),
            App.globalPut(Bytes("turn"),Minus(Int(1),t.load())),
            If(App.globalGet(Bytes("heap"))==Int(0)).Then(
                Seq([
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.amount: Int(feeForWinner),
                    TxnField.receiver: Txn.sender(),
                }),
                InnerTxnBuilder.Submit(),
                Approve()])
            ).Else(Approve())
           ])
    ).Else(
        Reject()
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return compileTeal(program, Mode.Application, version=5)

if __name__=='__main__':
    if len(sys.argv)!=4:
        print("Usage: ",sys.argv[0],"<Alice ADDR file> <Bob ADDR file> <Dealer ADDR file>")
        exit()

    with open(sys.argv[1]) as f:
        aliceA=f.read()
    alice=Addr(aliceA)

    with open(sys.argv[2]) as f:
        bobA=f.read()
    bob=Addr(bobA)

    with open(sys.argv[3]) as f:
        dealerA=f.read()
    dealer=Addr(dealerA)

    program=approval_program(alice,bob,dealer)
    
    with open("nim.teal","w") as f:
        f.write(program)
