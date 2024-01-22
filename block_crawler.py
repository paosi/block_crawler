#!/usr/bin/env python3

"""
Author: Paolo Sidera
Date: 01/22/2024
Python version: 3.10.9
"""

import json
import requests
import sqlite3
import sys
from datetime import datetime


# Collect and verify 3 parameter inputs from command line
if len(sys.argv) != 4:
    print(
        "Usage: python3 block_crawler.py <JSON_RPC_ENDPOINT> <DB_FILE_PATH> <BLOCK_RANGE>"
    )
    sys.exit(1)

JSON_RPC_ENDPOINT = sys.argv[1]
DB_FILE_PATH = sys.argv[2]
BLOCK_RANGE = sys.argv[3]


def validate_inputs():
    url = JSON_RPC_ENDPOINT
    payload = json.dumps(
        {"method": "eth_blockNumber", "params": [], "id": 1, "json rpc": "2.0"}
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    # Validate JSON-RPC endpoint
    if response.status_code != 200:
        print(f"Error: Invalid JSON-RPC endpoint. Status code: {response.status_code}")
        sys.exit(1)

    # Validate valid block range
    results = json.loads(response.text)
    latest_number = int(results.get("result"), 16)

    try:
        index = int(BLOCK_RANGE.split("-")[0])
        end_range = int(BLOCK_RANGE.split("-")[1])

        if index > end_range or end_range > latest_number:
            raise ValueError

    except ValueError:
        print("Error: Invalid block range")
        sys.exit(1)

    return index, end_range


# Retrieve mainnet transactions
def get_block_by_number(block_number):
    url = JSON_RPC_ENDPOINT
    payload = json.dumps(
        {
            "method": "eth_getBlockByNumber",
            "params": [block_number, True],
            "id": 1,
            "jsonrpc": "2.0",
        }
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    response_text = json.loads(response.text)
    result = response_text.get("result")

    return result


# Parse block data from response
def get_block_data(result):
    number_hex = result.get("number")
    hash_hex = result.get("hash")
    timestamp_hex = result.get("timestamp")

    # Transform hex values into readable format
    number = str(int(number_hex, 16))
    hash = str(int(hash_hex, 16))
    timestamp = datetime.utcfromtimestamp(int(timestamp_hex, 16)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return number, hash, timestamp


# Parse transaction data from response
def get_transaction_data(result):
    transactions = result.get("transactions")
    transaction_data = []

    for transaction in transactions:
        details_dict = {}
        details_dict["hash"] = transaction.get("hash")
        details_dict["block_hash"] = transaction.get("blockHash")
        details_dict["block_number"] = transaction.get("blockNumber")
        details_dict["sender"] = transaction.get("from")
        details_dict["receiver"] = transaction.get("to")
        details_dict["value"] = transaction.get("value")
        transaction_data.append(details_dict)

    return transaction_data


def main():
    # Initiate database connection
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    # Create database schemas
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_number TEXT,
            hash TEXT,
            timestamp DATETIME
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT,
            block_hash TEXT,
            block_number TEXT,
            sender TEXT NULL,
            receiver TEXT NULL,
            value REAL,
            FOREIGN KEY (block_number) REFERENCES block(number)
        )
    """
    )

    # Populate the database with valid block range
    index, end_range = validate_inputs()

    while index <= end_range:
        result = get_block_by_number(hex(index))
        index += 1
        number, hash, timestamp = get_block_data(result)

        load_block = (
            "INSERT INTO blocks (block_number, hash, timestamp) VALUES (?, ?, ?)"
        )
        cursor.execute(load_block, (number, hash, timestamp))

        transactions = result.get("transactions")
        for transaction in transactions:
            trans_hash_hex = transaction.get("hash")
            block_hash_hex = transaction.get("blockHash")
            block_number_hex = transaction.get("blockNumber")
            sender_hex = transaction.get("from")
            receiver_hex = transaction.get("to")
            value_hex = transaction.get("value")

            # Transform hex values into readable format
            trans_hash = str(int(trans_hash_hex, 16))
            block_hash = str(int(block_hash_hex, 16))
            block_number = str(int(block_number_hex, 16))
            sender = str(int(sender_hex, 16)) if sender_hex else None
            receiver = str(int(receiver_hex, 16)) if receiver_hex else None
            value = float(int(value_hex, 16) / 10**18)  # Convert from wei to ether

            load_transaction = "INSERT INTO transactions (hash, block_hash, block_number, sender, receiver, value) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(
                load_transaction,
                (trans_hash, block_hash, block_number, sender, receiver, value),
            )

    conn.commit()
    conn.close()

    return


if __name__ == "__main__":
    main()
