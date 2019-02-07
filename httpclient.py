#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import urllib
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        u = urlparse(url)
        self.host = u.hostname
        self.port = u.port
        if u.path != None and u.path != '':
            self.path = u.path
        else:
            self.path = "/"
        if self.port == None:
            self.port = 80

    def connect(self, host, port):
        self.buffer_size = 1024
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        self.header = data.split("\r\n\r\n")[0]

        self.code = self.header.split()[1]
        return self.code

    def get_headers(self,data):
        self.header = data.split("\r\n\r\n")[0]
        return self.header

    def get_body(self, data):
        self.body = data.split("\r\n\r\n")[1]
        return self.body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        self.get_host_port(url)
        try:

            self.connect(self.host,self.port)
            self.payload = "GET {} HTTP/1.1\r\nHost: {}:{}\r\nConnection: close\r\n\r\n".format(self.path,self.host,self.port)
            self.sendall(self.payload) 
            self.buffer = self.recvall(self.socket)

        except:
            return HTTPResponse(code = 404)
        self.close()
        code = self.get_code(self.buffer)
        body = self.get_body(self.buffer)
        if code == '404':
            return HTTPResponse(code = 404)
        return HTTPResponse(int(code), body)

    def POST(self, url, args=None):

        self.get_host_port(url)
        self.connect(self.host,self.port)
        try:
            args = urllib.parse.urlencode(args)
            self.payload = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}".format(self.path,self.host,len(args),args)
            self.sendall(self.payload)
            self.buffer = self.recvall(self.socket)
        except:
            if args == None:
                
                self.payload = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".format(self.path,self.host)
                self.sendall(self.payload)
                self.buffer = self.recvall(self.socket)

        code = self.get_code(self.buffer)
        if code == '404':
            return HTTPResponse(code = 404)
        body = self.get_body(self.buffer)
        return HTTPResponse(int(code), body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))