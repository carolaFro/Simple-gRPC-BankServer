# Distributed Banking System using gRPC (Python)

## Overview

This project implements a distributed banking system using gRPC in Python, where multiple customers interact with multiple bank branches that collectively maintain a **single shared account balance**. The system ensures real-time balance consistency and synchronization across all branches while supporting concurrent deposit, withdrawal, and query operations.

---

## System Architecture

* **Branches** act as gRPC servers and maintain account state
* **Customers** act as gRPC clients and issue transactions
* All branches propagate balance updates to one another
* gRPC ensures structured, efficient, and reliable communication

Each transaction processed by a branch is **propagated to peer branches**, guaranteeing that all branches reflect the same balance at all times.

---

## Technologies Used

* **Python 3**
* **gRPC**
* **Protocol Buffers**
* **JSON** (input/output configuration)

---

## Project Structure

```
.
├── protos/
│   └── banks.proto
├── server.py
├── branch.py
├── client.py
├── customer.py
├── input.json
├── output.json
└── README.md
```

---

## gRPC Interface

The `banks.proto` file defines the communication contract between customers and branches.

### Service

* **Branch**

  * `MsgDelivery(Request) returns (Reply)`

### Request Message

* `id`: Unique request identifier
* `interface`: Operation type (`deposit`, `withdraw`, `query`)
* `money`: Transaction amount (for deposits and withdrawals)

### Reply Message

* `interface`: Operation performed
* `result`: Success or failure
* `balance`: Updated account balance

---

## Setup Instructions

### 1. Environment Requirements

Ensure Python 3 is installed:

```bash
python3 --version
```

### 2. Install Dependencies

```bash
pip install grpcio==1.64.1 grpcio-tools==1.64.1 protobuf==5.27.2
```

### 3. Generate gRPC Code

```bash
python -m grpc_tools.protoc \
  -I=protos \
  --python_out=. \
  --grpc_python_out=. \
  protos/banks.proto
```

This generates:

* `banks_pb2.py`
* `banks_pb2_grpc.py`

---

## Running the Project

### 1. Start the Branch Servers

```bash
python server.py input.json
```

### 2. Run the Client (Customers)

In a separate terminal:

```bash
python client.py input.json
```

---

## Input and Output

### `input.json`

Defines:

* Initial branch balances
* Customers and their transaction sequences

### `output.json`

Captures:

* Transaction results
* Updated balances after each operation

This output verifies correct **balance propagation and synchronization** across all branches.

---

## Results

### Deposit Cycle

* Customers submit deposit requests to their assigned branches
* Branches update their balances and propagate changes
* Queries confirm consistent balances across all branches

### Withdrawal Cycle

* Customers withdraw funds
* Updated balances are propagated and verified
* System returns to the original balance after all withdrawals

These results demonstrate **correct distributed state management and real-time consistency**.

---

## References

* gRPC Python Quick Start: [https://grpc.io/docs/languages/python/quickstart/](https://grpc.io/docs/languages/python/quickstart/)


