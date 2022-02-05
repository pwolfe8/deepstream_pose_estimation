#!/usr/bin/python3

# import socket
import threading
import socketserver

def parse_byte_string_msg(byte_str):
  msg = byte_str.decode("utf-8")
  xy = [int(x) for x in msg.strip('()').split(',')]
  x,y = xy
  print(f'got x: {x} and y: {y}')

class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        # print(f'client {self.client_address}\n\twrote {data}\n\tto {self.server.server_address}')

        # send to another function for handling
        parse_byte_string_msg(data)

        # send back message in uppercase as confirmation (comment out if not needed)
        # socket.sendto(data.upper(), self.client_address)

def start_udpserv(port=6969):
  with socketserver.UDPServer(('127.0.0.1', port), MyUDPHandler) as server:
    print(f'now listening on {server.server_address}')
    server.serve_forever()


# test here
#testmsg =  b'[(801,374),(937,310),(769,325),(1176,439),(-1,-1),(1515,859),(751,1039),(2127,1261),(618,1615),(1707,2114),(197,1786),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(1131,950),]'
# testmsg = b'[(715,201),(-1,-1),(-1,-1),(1200,88),(-1,-1),(1594,677),(555,769),(2006,1397),(433,1516),(1936,1966),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(1074,722),]\n[(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(342,1722),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),]'
# parse_byte_string_msg(testmsg)
# exit(1)

# create udp server for each port in port_list
port_list = [6969]
threads = [threading.Thread(target=start_udpserv, args=(p,)) for p in port_list]

# start threads to listen
print(f"running port listening on threads:\n\t{port_list}\n")
for t in threads:
  t.start()
