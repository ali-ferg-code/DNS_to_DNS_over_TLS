import dnsconfig as config
from connection import *

# Set up sockets to listen and request 
listener = UDPConnection(config.UDPHOST,config.UDPPORT)
requester = TLSTCPConnection(config.TLSHOST,config.TLSPORT)

print(f"listening for requests on {config.UDPHOST}:{config.UDPPORT}...")

while True:
    data, addr = listener.receive() # block until a UDP message is received

    if(config.VERBOSITY > 0):
        logline = f"heard a dns request of length {len(data)}"
        if(config.VERBOSITY > 1):
            logline += f" from {addr}"
        print(logline)

    requester.refresh() # make sure the pipe is not broken
    response = requester.query(data) # query the DOT server
    listener.sendto(response,addr) # return the result to the responder
