import platform

# general:

VERBOSITY = 1

# connection info
# For the UDP connection listening for the DNS queries

UDPHOST = "172.140.1.2"
UDPPORT = 53

# For the TLS-secured TCP connection to a known DNS-over-TLS DNS server

TLSHOST = "1.1.1.1" # cloudflare
TLSPORT = 853
TLSCERT = '/etc/ssl/certs/ca-certificates.crt'
