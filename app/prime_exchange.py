import argparse
import pathlib
import requests
import sys
from base64 import b64decode
from datetime import  datetime
from requests.exceptions import HTTPError
from abci.application import OkCode, ErrorCode

def get_value(args: argparse.Namespace) -> None:
    results= requests.get(f'http://{args.node_ip}:26657/abci_query?data="{args.key}"', timeout=10)
    if results.status_code==200:
        print(results)
        res_json= results.json()["result"]
        value=b64decode(res_json["response"]["value"].encode("utf-8")).decode("utf-8")
        print(value)
    else:
        print(results.status_code)
       # print(results.text)
        
def register_pe (args: argparse.Namespace) -> None:
    results= requests.get(f'http://{args.node_ip}:26657/broadcast_tx_commit?tx="{"Register"}={args.key}={args.value}={datetime.now()}"', timeout=500)
    if results.status_code== 200:
        #--- Got proper response from Application logic ---#
        print(results.json()['result']['deliver_tx']['code'])
        if results.json()['result']['deliver_tx']['code']==OkCode:
            print(results.json()['result']['deliver_tx']['log'])
            print (results.json()['result']['deliver_tx'])
        else:
            print(results.json()['result']['deliver_tx']['log'])
    else:
        print("Registration Request unsuccessful")
        print(results.status_code)
        print (results.text)
        
def maintenance_pe (args: argparse.Namespace) -> None:
    results= requests.get(f'http://{args.node_ip}:26657/broadcast_tx_commit?tx="{"Maintenance"}={args.key}={args.value}={datetime.now()}"')
    if results.status_code==200:
        print(results.json()['result']['deliver_tx']['code'])
        if results.json()['result']['deliver_tx']['code']==OkCode:
            print(results.json()['result']['deliver_tx']['log'])
            print (results.json()['result']['deliver_tx'])
        else:
            print(results.json()['result']['deliver_tx']['log'])
        
    else:
        print("Maintenance Request Unsuccessful")

        
def active_pe (args: argparse.Namespace) -> None:
    results= requests.get(f'http://{args.node_ip}:26657/broadcast_tx_commit?tx="{"Active"}={args.key}={args.value}={datetime.now()}"')
    if results.status_code== 200:
        print(results.json()['result']['deliver_tx']['code'])
        if results.json()['result']['deliver_tx']['code']==OkCode:
            print(results.json()['result']['deliver_tx']['log'])
            print (results.json()['result']['deliver_tx'])
        else:
            print(results.json()['result']['deliver_tx'])
            print(results.json()['result']['deliver_tx']['log'])
    else:
        print("Active state Request Unsuccessful")
        
def deregister_pe (args: argparse.Namespace) -> None:
    results= requests.get(f'http://{args.node_ip}:26657/broadcast_tx_commit?tx="{"Deregister"}={args.key}={args.value}={datetime.now()}"')
    if results.status_code== 200:
        if results.json()['result']['deliver_tx']['code']==OkCode:
            print(results.json()['result']['deliver_tx']['log'])
            print (results.json()['result']['deliver_tx'])
        else:
            print(results.json()['result']['deliver_tx'])
            print(results.json()['result']['deliver_tx']['log'])
             
    else:
        print("Issue with PE {} De-registration".format(args.node_ip) )
        
def get_parser() -> argparse.ArgumentParser:
    parser= argparse.ArgumentParser(description='Transaction type of Prime Exchanger (PE)')
    parser.add_argument("--node_ip", default="192.166.10.2", type=str, required=False)
    subparsers= parser.add_subparsers()
    
    #-------- Registering the Prime Exchanger (PE) ---------#
    reg_parser= subparsers.add_parser("Register")
    reg_parser.set_defaults(action=register_pe)
    #reg_parser.add_argument("action", help="Key for the PE to Register")
    reg_parser.add_argument("key", help="Key for the PE to Register")
    reg_parser.add_argument("value", help="Public address for the PE to Register")
    
    #--------- Fetching the current status of the Prime Exchanger (PE) ---------#
    get_parser= subparsers.add_parser("Status")
    get_parser.set_defaults(action=get_value)
    get_parser.add_argument("key", help="Key of the Already Register PE")
    
    #------------ Setting the Prime Exchanger (PE) to Maintenance Mood ----------#
    maintenance_parser= subparsers.add_parser("Maintenance")
    maintenance_parser.set_defaults(action=maintenance_pe)
    maintenance_parser.add_argument("key", help="Key for the PE to set in Maintenance Mood")
    maintenance_parser.add_argument("value", help="Public address of the PE")
    
    #------------ Setting the Prime Exchanger (PE) back to Active Mood ----------#
    active_parser= subparsers.add_parser("Active")
    active_parser.set_defaults(action=active_pe)
    active_parser.add_argument("key", help="Key for the PE to set in active Mood")
    active_parser.add_argument("value", help="Public address of the PE") 
    
     #------------ De-registration of the Prime Exchanger (PE) -----------#
    deregister_parser= subparsers.add_parser("Deregister")
    deregister_parser.set_defaults(action=deregister_pe)
    deregister_parser.add_argument("key", help="Key for the PE to deregister")
    deregister_parser.add_argument("value", help="Public address of the PE") 
    
    return parser


def main() -> None:
    parser= get_parser()
    print(parser)
    args= parser.parse_args()
    if hasattr(args, "action"):
        args.action(args)
    else:
        sys.argv.append("--help")
        parser.parse_args()
        
        
if __name__ == "__main__":
    #---- input() always returns a String ----#
    #sys.argv[0] = input("Enter Register/Status/Maintenance/Active for the action to taken: ")
    #sys.argv[1] = input("Enter the Key for the Prime Exchanger (PE): ")
    #sys.argv[2] = int(input("Enter the public Address the Prime Exchanger (PE): "))
    main()