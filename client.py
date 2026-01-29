import json
import sys
import customer


def main(input_file):
    # Load input file
    with open(input_file, "r") as f:
        data = json.load(f)

    output_data = []  # To store the final output

    # Process each customer
    for entry in data:
        if entry["type"] == "customer":
            customer_id = entry["id"]
            events = entry["events"]

            # Initialize and execute customer
            customer_instance = customer.Customer(customer_id, events)
            customer_instance.executeEvents()

            # Format the output with each event as a separate object
            for event in customer_instance.recvMsg:
                output_data.append({
                    "id": customer_id,
                    "recv": [event]
                })

    # Write output to JSON file
    with open("output.json", "w") as out_f:
        json.dump(output_data, out_f, indent=4)

    print("Responses written to output.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
