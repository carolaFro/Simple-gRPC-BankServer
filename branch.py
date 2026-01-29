import grpc
import banks_pb2
import banks_pb2_grpc


class Branch(banks_pb2_grpc.BranchServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # This branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches
        self.processedID = list()
        self.writeset = set()

    def ProccessID(self):
        for branch_id in self.branches:
            if branch_id != self.id:  # Skip this branch's own ID
                channel = grpc.insecure_channel(f"localhost:{5000 + branch_id}")
                stub = banks_pb2_grpc.BranchStub(channel)
                self.stubList.append(stub)

    # This function serves as Propagate_Deposit and Propagate_Withdraw
    def PropagateToBranches(self, request) -> None:
        # Add 'propagate_' to the interface so other branches know not to propagate further.
        request.interface = f"propagate_{request.interface}"

        # Include the operation ID in the writeset
        request.writeset.extend(self.writeset)

        # Get the stublist to be able to communicate with the remote branches using RPC
        for stub in self.stubList:
            res = stub.MsgDelivery(request)  # Call msgDelivery to proccess the request
            if res.result == "writeset mismatch":
                print(f"Branch {self.id}: Propagation failed for {request.id} due to writeset mismatch.")
        # Remove it since its no longer needed!
        request.interface = request.interface.replace("propagate_", "")

    def BranchToAnyProcess(self, request):
        from_customer = False
        # If we dont have 'propagate_' in the interface name, message must come from a customer!"
        if request.interface.lower() in ["query", "withdraw", "deposit"]:
            from_customer = True
        res = {}
        # Branch.Query
        if request.interface.lower() == "query":
            res = {"interface": request.interface, "result": "success", "balance": self.balance}
        # Branch.Withdraw
        elif "withdraw" in request.interface.lower() and request.money > 0:
            print("here")
            if self.balance >= request.money:
                self.balance -= request.money
                # If the message comes from a customer, propagate to other branches!
                if from_customer:
                    self.PropagateToBranches(request)
                res = {"interface": request.interface, "result": "success", "balance": self.balance}
            else:
                res = {"interface": request.interface, "result": "fail", "balance": self.balance}
        # Branch.Deposit
        elif "deposit" in request.interface.lower():
            self.balance += request.money
            # If the message comes from a customer, propagate to other branches!
            if from_customer:
                self.PropagateToBranches(request)
            res = {"interface": request.interface, "result": "success", "balance": self.balance}
        else:
            res = {"interface": request.interface, "result": "fail", "balance": self.balance}

        # Log the request result
        self.recvMsg.append(res)
        print(f"BRANCH {self.id}: {res}")
        # Return the response
        print("here2")
        return res

    def MsgDelivery(self, request, context):
        # Make sure writesets are propagated as well
        if request.interface.startswith("propagate_"):
            response = self.BranchToAnyProcess(request)
            if response["result"] == "success":
                self.writeset.add(request.id)  # Add to writeset for propagated requests
            return banks_pb2.Reply(**response)

        # Check writesets
        if not self.writeset.issuperset(request.writeset):
            return banks_pb2.Reply(
                interface=request.interface, 
                result="writeset mismatch", 
                balance=self.balance
                )

        # Process the customer request and branches requests
        response = self.BranchToAnyProcess(request)
        # Update writesets
        if request.interface in ["deposit", "withdraw"]:
            self.writeset.add(request.id)
        # Reply with the process result
        return banks_pb2.Reply(**response)
