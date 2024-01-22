# Block Crawler

This program retrieves transactions from Ethereum Mainnet within a given block number range and persists them to an SQLite database.

### Requirements

Please make sure to have Python3 installed. The version used for this program is Python 3.10.9

This program uses the ```requests``` library. Install required packages:
```
pip install -r requirements.txt
```

### Running the Program

The program should be run from the command line and requires 3 input parameters: 

  1. A JSON-RPC endpoint to call an Ethereum client
  2. The path of the SQLite file to write to
  3. A block range, formatted as "{start}-{end}"

The command to run the program with a range 18908800-18909050 should be similar to the following:
```
$ python3 block_crawler.py https://wider-newest-brook.quiknode.pro/7b7535fb7a6c02a24def64ff2b54c769cefb113f/ db.sqlite3 18908800-18909050
```

### Querying the database

An SQL file is included that queries the populated database for the block that had the largest volume of ether transferred between 2024-01-01 00:00:00 and 2024-01-01 00:30:00. To return the block number and the total volume of ether transferred for that block, please run a command similar to the following:
```
$ sqlite3 db.sqlite3 < query.sql
```
