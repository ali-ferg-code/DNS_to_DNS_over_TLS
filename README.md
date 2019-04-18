# DNS to DNS-over-TLS proxy

The following guide explains the setup and running of a simple DNS to DNS-over-TLS proxy server written in python.

## Getting Started
This project contains two docker images:
- A **dns-proxy** container which listens acts as a DNS name server and sends traffic to cloudflare's DOT (DNS-over-TLS) server.
- A **dns-client-container** which runs in the same network and is configured to use the above **dns-proxy** as its default DNS server.


## Installation and running

### Create a docker network
This project uses a docker network to define which devices will have visibility to the DNS server. If the below subnet collides with one that has already been set up, you will need to update the IP addresses in these commands and in ```proxy/dnsconfig.py```
```
docker network create --subnet 172.140.1.0/16 barcelona
```
### Set up the dns-proxy container
For the remainder of the steps it is assumed you are running these commands in the top level project directory.
```
docker build -t dns-proxy proxy/
docker run --net barcelona --ip 172.140.1.2 dns-proxy
```
### Set up the client container
The below steps open an interactive shell in a small alpine container which has access to some basic networking tools. There is also a small throughput-testing script ```/loadtester.sh``` which can be used to measure performance and latency. More details below.
```
docker build -t dns-client-container client/
docker run -it --net=barcelona --dns=172.140.1.2 dns-client-container
```
To test the DNS server, you can run  ```dig google.com``` or ```nslookup yahoo.com```


### Assumptions and limitations

There is currently a lot of room for improvement! See the Future plans section for more info.

- This assumes that the request that hits the **dns-proxy** will be a valid single UDP DNS packet.
- This implementation is currently singly-threaded, which impacts scalability. For more information on the performance, see the next section.
- This implementation does not perform DNSSEC validation or pad the outbound TLS packet as per EDNS(0)

### Performance

As this implementation is singly-threaded, only one query can be performed at a time. Therefore depending on the client-side timeouts used and the peak DNS request load requests may be dropped. Capacity calculations are detailed below.

### Latency & Throughput 
The **dns-client-container** contains a simple test script ```/loadtester.sh``` which will query the internal DNS server in a loop as soon as it receives a response from the previous request. This gives an estimate of the maximum throughput of the server.
```
> time sh loadtester.sh 1000
```
This gives us an average response time (including the recursive dns query over WiFi) of **111.3ms** and a max throughput of **~9 queries/s**.

#### Additional container metrics

Under max load the container uses **~2.9Mb**  and has an average network I/O of **~1.4Mb**. Idle, the container memory usage stays **~500Kb** and negligeable I/O
Logging verbosity is defined in the ```proxy/dnsconfig.py``` file, and will print to STDOUT where it can be redirected at your discretion.
VERBOSITY 0: Log on startup
VERBOSITY 1: +Log a line for each incoming request ( size of the request )
VERBOSITY 2: +Log the local IP sending the request
VERBOSITY 3: +Log the packet you are sending to the DOT server
VERBOSITY 4: +Log the response packet

### Ports
The dns-router container recieves packets from within the network on UDP port 53, and connects to 1.1.1.1 (configurable) via TCP on port 853


## Microservice Deployment
As we are using docker containers, it is trivial to define the default nameserver of other containers on startup. At a larger scale - beyond the scalability benefits of multi-threading - we would employ load-balancing techniques to share the traffic from this one node and increase overall resiliency. A simple example would be to have a dedicated **dns-proxy** container *in each docker sub-network*. Alternatively we could have a dedicated load-balancer to select a local **dns-proxy** instance based on a load-balancing strategy of our choosing ( eg. round-robin ).

## Future plans and improvements
- Improved logging: Heartbeat logging, logging *the four golden signals* metrics.
- A cache layer. As very little interfering with the incoming packets happens in this implementation, there is currently no functionality to implement this nice-to-have feature. This would be a simple set of cached objects containing a known request and response with a TTL (time-to-live) defined. Before sending the DNS request downstream, we would first check our in-memory cache of known responses and their TTL state. If there is a valid response, we would generate our own valid response UDP packet and reset the TTL value. If we didn't have a valid local copy of the response, we would first check our DOT server, and save a copy of the response IP with a suitable TTL value.
- Resiliency: As mentioned in the Assumptions and Limitations section, we assume that we are receiving valid DNS packets. For reliability and improved throughput ( no point sending an invalid packet downstream ) we should first validate the DNS query.
- Complete unit and regression test suite. Incomplete tests were not added to this project.

##### Author

* **Alexander (Ali) Ferguson**
https://github.com/ali-ferg-code


