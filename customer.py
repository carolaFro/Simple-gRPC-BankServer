import grpc
import banks_pb2
import banks_pb2_grpc
import time


class Customer:

    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # Stub dict
        self.stubs: dict[banks_pb2_grpc.BranchStub] = {}
        # Track operation IDs
        self.writeset = set()

    def createStub(self, id):
        # Create the gRPC channel to communicate with server
        channel = grpc.insecure_channel(f"localhost:{5000 + id}")
        self.stubs[id] = banks_pb2_grpc.BranchStub(channel)

    def send_request(self, event_id, interface, money, dest_branch):
        # If the destination branch is not on our stub dict. Create a stub for it.
        if dest_branch not in self.stubs.keys():
            self.createStub(dest_branch)
        # Send a request to the branch for the specified event and return the response.
        request = banks_pb2.Request(
            id=event_id, interface=interface, money=money
        )
        request.writeset.extend(self.writeset)

        print(f"Customer Request: {request}")

        response = self.stubs[dest_branch].MsgDelivery(request)

        if interface == "query":
            event_response = {
                "interface": interface,
                "branch": dest_branch,
                "balance": response.balance
            }
        else:
            event_response = {
                "interface": interface,
                "branch": dest_branch,
                "result": response.result,
            }

        if interface == "query":
            event_response["balance"] = response.balance

        self.recvMsg.append(event_response)

        # Update writeset for successful operations
        if response.result == "success" and interface in ["deposit", "withdraw"]:
            self.writeset.add(event_id)

        return event_response

    def executeEvents(self):
        for event in self.events:
            print(event)

            interface = event["interface"]
            money = event.get("money", 0)
            event_id = event["id"]
            dest_branch = event["branch"]
            result = self.send_request(event_id, interface, money, dest_branch)

            if result:
                self.recvMsg.append(result)
