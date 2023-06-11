import struct
from tendermint.abci.types_pb2 import (  
    ResponseInfo,
    ResponseInitChain,
    ResponseCheckTx,
    ResponseDeliverTx,
    ResponseQuery,
    ResponseCommit,
)

from abci.server import ABCIServer
from abci.application import BaseApplication, OkCode, ErrorCode 

import json 
import pathlib 
from hashlib import sha256

thisdir = pathlib.Path(__file__).resolve().parent

def encode_number(value):
    return struct.pack(">I", value)


def decode_number(raw):
    return int.from_bytes(raw, byteorder="big")


class SimpleCounter(BaseApplication):
    def info(self, req) -> ResponseInfo:
        """Returns info on application"""
        r = ResponseInfo()
        r.version = req.version
        r.last_block_height = 0
        r.last_block_app_hash = b""
        return r

    def init_chain(self, req) -> ResponseInitChain:
        """Initializes Application"""
        self.data = {}
        return ResponseInitChain()

    def check_tx(self, tx: bytes) -> ResponseCheckTx:
        """
        Validate transactions before entry into the mempool

        Optional method for performing basic checks on a transaction.
        This method is optional, since it's not actually used in consensus.
        This method should only perform basic checks like formatting, signature, etc. 
        These checks should also be re-performed in deliver_tx.
        This method should not modify application state.
        """
        try:
            action,key,pub_address,timestamp = tx.decode("utf-8").split("=")
            print(f"check_tx | Action: {action}, Prime Exchange: {key}, Public Address:{pub_address}, Timestamp: {timestamp}")
        except Exception as e:
            return ResponseCheckTx(code=ErrorCode, log=f"Exception: {e}")
        return ResponseCheckTx(
            code=OkCode,
            log=f"Transaction check from Prime Exchange with key {key} and Public address {pub_address}"
            )

    def deliver_tx(self, tx: bytes) -> ResponseDeliverTx:
        """
        Validate transactions from clients (i.e. Prime Exchanges) to 
        be committed to blockchain.
        Perform all checks, verify transaction is valid, and modify 
        the application state, accordingly.
        """
        try:
            action, key, pub_address, timestamp = tx.decode("utf-8").split("=")
            print(f"deliver_tx | Action:{action}, key: {key}, address:{pub_address}, timestamp: {timestamp}")
            
            if action=='Register':
            #--- Register a new Prime Exchange with Application ---#
            #--- First check if the PE is already registered or not ---#
                if key not in self.data:
                # key does not exist in the database #
                    print(f"Prime Exchange:{key} not in the database")
                    #print(self.data)
                    self.data[key] = {
                     "address": pub_address,
                     "status": "active",
                     "timestamp": timestamp
                    }
                    return ResponseDeliverTx(
                    code=OkCode,
                    log=f"Register Prime Exchange with key {key} and Public address {pub_address}"
                     )
                else:
                    print(f"Prime Exchange:{key} already in the Database")
                    print(self.data)
                    return ResponseDeliverTx(
                    code=ErrorCode, 
                    log=f"Prime Exchange with key {key} and Public address {pub_address} is already registered"
                     )
                     
            elif action=='Maintenance':
            #--- Switch the "Active" state of a Prime Exchanger (PE) to "Maintenance" ---#
            #--- First check if the PE is already registered and active ---#
                 if key in self.data and self.data[key]["status"]=="active":
                     #--- PE is already registered and in "active" state ---#
                    self.data[key] = {
                     "address": pub_address,
                     "status": "maintenance",
                     "timestamp": timestamp
                     }
                    return ResponseDeliverTx(
                    code=OkCode, 
                    log=f"Prime Exchange with key {key} and Public address {pub_address} switched to maintenance state"
                    )
                 elif key not in self.data and self.data[key]["status"]!="active":
                    #--- PE is not in "active" state ---#
                    return ResponseDeliverTx(
                    code=ErrorCode,
                    log=f"Prime Exchange with key {key} and Public address {pub_address} is not in active state"
                    )
                 
                 else:
                     #--- PE is not even Registered ---#
                     return ResponseDeliverTx(
                    code=ErrorCode, 
                    log=f"Prime Exchange with key {key} and Public address {pub_address} is not even registered"
                    )
                    
            elif action=='Active':
                #---- To switch a PE to "Active" state, the PE must be registered and in "Maintenance" state ---#
                if key in self.data and self.data[key]["status"]=="maintenance":
                    self.data[key] = {
                     "address": pub_address,
                     "status": "active",
                     "timestamp": timestamp
                     }
                    return ResponseDeliverTx(
                    code=OkCode, 
                    log=f"Prime Exchange with key {key} and Public address {pub_address} switched to active state from maintenance state"
                    )
                elif key in self.data and self.data[key]["status"]!="maintenance":
                    #--- Not in the "Maintenance" state ---#
                    return ResponseDeliverTx(
                    code=ErrorCode, 
                    log=f"Prior status of Prime Exchange with key {key} and Public address {pub_address} is not Maintenance"
                    )
                else:
                     #--- PE is not even Registered ---#
                     return ResponseDeliverTx(
                    code=ErrorCode, 
                    log=f"Prime Exchange with key {key} and Public address {pub_address} is not even registered"
                    )   
        
            elif action=='Deregister':
                #--- Deregister a PE that is registered and is either in "Active" or "Maintenance" state ---#
                if key in self.data:
                     #--- Check that PE is already registered  ---#
                    del self.data[key]
                    return ResponseDeliverTx(
                    code=OkCode, 
                    log= f"Deregister Prime Exchange with key {key} and Public address {pub_address}"
                    )
                else:
                    return ResponseDeliverTx(
                    code=ErrorCode, 
                    log= f"Prime Exchange with key {key} and Public address {pub_address} does not exist"
                    )

            else:
                return ResponseDeliverTx(
                    code=ErrorCode, 
                    log=f"Unknown Action requested in a transaction from Prime Exchanger"
                )
                
        except Exception as e:
            return ResponseDeliverTx(
                code=ErrorCode
                #log=f"Exception: {e}"
            )
        return ResponseDeliverTx(code=OkCode)

    def query(self, req) -> ResponseQuery:
        """Return piece of application state 
        
        In this implementation, the query returns the current value for a 
        specified key or N/A if the key does not exist
        """
        key: str = req.data.decode("utf-8")
        return ResponseQuery(
            code=OkCode, value=self.data.get(key, {"value": "N/A"})["value"].encode("utf-8")
        )

    def commit(self) -> ResponseCommit:
        """Persist the application state"""
        json_str = json.dumps(self.data, indent=4)
        thisdir.joinpath("state.json").write_text(json_str)
        return ResponseCommit(data=sha256(json_str.encode("utf-8")).digest())


def main():
    app = ABCIServer(app=SimpleCounter())
    app.run()


if __name__ == "__main__":
    main()
