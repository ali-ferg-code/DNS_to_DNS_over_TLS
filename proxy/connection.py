import socket
import ssl
import dnsconfig as config
import binascii

 # These classes handle the sending and receiving of messages to and from the dns-proxy.



class Connection:
    # This class is not instantiated, but provides the base setup, teardown and constructor methods for its children.

    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.sock = None
        self.setup(verbose=True)

    def setup(self,verbose=False):
        self.sock = socket.socket()
        self.sock.connect((self.host,self.port))

    def tearDown(self):
        self.sock.close()


class UDPConnection(Connection):
    # This connection provides the functionality for the UDP connection

    def setup(self,verbose=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.host,self.port)
        self.sock.bind(server_address)

    def receive(self,length=512):
        return self.sock.recvfrom(length)

    def sendto(self,content,address):
        self.sock.sendto(content,address)



class TLSTCPConnection(Connection):
    # This connection class provides the functionality to wrap the UDP messages
    # as TLS-secured TCP messages to send to a known DOT server.

    def setup(self,verbose=False):
        # create and set up the 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(20)
        wrapper = ssl.create_default_context()
        wrapper = ssl.SSLContext(ssl.PROTOCOL_TLS)
        wrapper.verify_mode = ssl.CERT_REQUIRED
        wrapper.load_verify_locations(config.TLSCERT)
        tls_socket = wrapper.wrap_socket(self.sock, server_hostname=self.host)
        tls_socket.connect((self.host, self.port))
        if(verbose):
            print(tls_socket.getpeercert())
        self.sock = tls_socket

    def wrap_udp(self,udp_request):
        a =  "00"
        b = hex(len(udp_request))[2:]
        c = udp_request
        return bytes.fromhex(a) + bytes.fromhex(b) + c

    def unwrap_tcp(self,tcp_request):
        return tcp_request[2:]

    def query(self,request):            
        request = self.wrap_udp(request)
        if(config.VERBOSITY > 1 ):
            print(request)
        self.sock.send(request)
        data = self.sock.recv(2048)
        if(config.VERBOSITY > 2 ):
            print(request)
        return self.unwrap_tcp(data)

    def refresh(self):
        self.tearDown()
        self.setup()
