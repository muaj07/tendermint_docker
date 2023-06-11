
# Docker container for Tendermint Testnet

---
```go

```
---

## Introduction
This document contains the steps for running docker containers for Tendermint testnet. Questions and comments to @ajmal.muhammad.

The tendermint testnet consists of a tendermint engine/core, application layer, and client (light node) modules, each of them being deployed in a docker container. The tendermint core provides the consensus and network layer of the blockchain while the application layer runs/deploys the smart contract (or application logic) to maintain the state machine for the blockchain. For instance, in the voltage regulation market case, the application layer will maintain the real-time status (in terms of voltage levels) of prime exchanges providing the voltage regulation services. The tendermint core and the application logic form a full blockchain node, which could be co-located (or deployed) on some `Prime Exchanges`. Finally, the client is a light node that uses the blockchain and sends transactions to blockchain. For instance, most of the `Prime Exchanges` participating in the voltage regulation market could be a client. 

The tendermint core establishes 4 TCP connections with the application layer for `Consensus`, `Info`, `Mempool`, and `Snapshot` related messages and method. More details about these methods and types can be found in https://github.com/tendermint/spec/blob/master/spec/abci/abci.md. The tendermint core exposes a port (26657) for its RPC module, which is used for listening to messages/transactions from the clients (or light node). More details about RPC client for tendermint can be found in https://docs.tendermint.com/v0.33/rpc/.

<img
src=“\tendermint_swarm\swarm\swarm\Tendermint.JPEG”
raw=true
alt=“Subject Tendermint core based blockchain architecture”
style=“margin-right: 10px;”
/>

In this simple testnet, we assume that the client (or light node) is a `Prime Exchange` that runs the `app/prime_exchange.py` program for communication with the tendermint core. The program enables the `Prime Exchange` to first Register itself on the tendermint node (tendermint core plus application) and later sends different types of messages to update its status (i.e., `Maintenance`, `Active`) and other parameters (e.g., voltage regulation level, power factor correction, etc.) on the tendermint node. Upon receiving the messages/transaction from the `Prime Exchange` (i.e., client), the tendermint core forwards them to the application layer via one of the proper connections (i.e., `Consensus`, `Info`, `Mempool`, and `Snapshot`). 

The application layer runs the `app/application_logic.py` for maintaining a state machine for all the `Prime Exchanges` registered with the application. It decodes the messages send by the clients (via tendermint core RPC) update the state machine (if needed) and response back to clients (via tendermint core). In our testnet, the application layer will update the status (and other related parameters) of the `Prime Exchange`.



<img
src=“\tendermint_swarm\swarm\swarm\PE_states.jpg”
raw=true
alt=“Subject Different states for a Prime Exchanger”
style=“margin-right: 10px;”
/>


## Images building and running containers
For the testnet, we will need to build two images, one for the tendermint core and the other for the application layer (which is also used for running client).

To build the tendermint core image `tendermint/tendermint`, we will use the following command:
---
```
docker build -f DOCKER/Dockerfile -t "tendermint/tendermint" .
```
---
Similarly, to build the application layer image `my_image`, we will use the following command:
---
```
docker build -t my_image .
```
---
Finally, we will run the `docker compose up` to deploy these images in the containers. To avoid the above process, we can simply run the `run.sh` file that contains all these commands.


## Running the testnet
Once all the containers are up and running, open a terminal and run the following command:
---
```
docker container exec -it client bash
```
---
we are now inside the client container and hence sends transactions/messages to the tendermint node. For instance, to register a `Prime Exchanges` with key `PE01` and address `address01`, we can run the following command:
---
```
python3 app/prime_exchange.py Register PE01 address01
```
---
This command will register a `Prime Exchanges` on the application layer of the tendermint node as shown in the `Response` message from the application layer as shown below:
<img
src=“\tendermint_swarm\swarm\swarm\PE01_register.png”
raw=true
alt=“Subject Registration message response”
style=“margin-right: 10px;”
/>


Later at some point if you want to switch the `Prime Exchanges` with key `PE01` and address `address01` to `Maintenance` mood, run the following command:
---
```
python3 /app/prime_exchange.py Maintenance PE01 address01
```
---
The application layer will update the status of `PE01` to `Maintenance` in its database as shown below:
<img
src=“\tendermint_swarm\swarm\swarm\PE01_Maintenance.png”
raw=true
alt=“Subject Maintenance message response”
style=“margin-right: 10px;”
/>

Similarly, the `PE01` can be moved back to `Active` state using the following command from the client terminal:
---
```
python3 /app/prime_exchange.py Active PE01 address01
```
---
<img
src=“\tendermint_swarm\swarm\swarm\PE01_Active.png”
raw=true
alt=“Subject Active message response”
style=“margin-right: 10px;”
/>

Finally, at some point you want to `Deregister` the `PE01`, use the following command in the client terminal:
---
```
python3 /app/prime_exchange.py Deregister PE01 address01
```
---
<img
src=“\tendermint_swarm\swarm\swarm\PE01_deregister.png”
raw=true
alt=“Subject Deregister message response”
style=“margin-right: 10px;”
/>


All these transactions will be executed in the application layer, which can be confirmed for the logs in the `node0-application` logs. To view the logs of the application layer, open a new terminal and run the following command:

---
```
docker logs -f node0-application
```
---
<img
src=“\tendermint_swarm\swarm\swarm\Application_logs.png”
raw=true
alt=“Subject Application layer logs”
style=“margin-right: 10px;”
/>