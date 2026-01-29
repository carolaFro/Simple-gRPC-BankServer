import grpc
from concurrent import futures
import json
import sys
import banks_pb2_grpc
import branch


def serve(input_file):
    # Open the input file
    with open(input_file, "r") as f:
        data = json.load(f)

    # Get the branch events
    servers = []
    for entry in data:
        if entry["type"] == "branch":
            # Process and store branch events
            branch_id = entry["id"]
            balance = entry["balance"]
            branches = [b["id"] for b in data if b["type"] == "branch" and b["id"] != branch_id]

            # Init the branch class to start the rpcChannel with the proccessID as part of the channel number
            branch_instance = branch.Branch(branch_id, balance, branches)
            branch_instance.ProccessID()

            # Start server
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            banks_pb2_grpc.add_BranchServicer_to_server(branch_instance, server)

            port = 5000 + branch_id
            server.add_insecure_port(f"[::]:{port}")
            server.start()

            print(f"Branch {branch_id} server started on port {port}.")
            servers.append(server)

    try:
        for server in servers:
            server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server shutting down.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    serve(input_file)
