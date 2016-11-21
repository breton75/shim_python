import sys
import socket
import array
import argparse
import struct
import _shim_main as shim

from _defs import *

e_mode_one = 0
e_mode_loop = 1


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', '--host', type=int, required=False)
    parser.add_argument('-port', '--port', type=int, required=False)
    parser.add_argument('-mode', '--exec_mode', type=int, required=False)
    parser.add_argument('-fn', '--file_name', type=str, required=False)

    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.host == None or namespace.port == None or
        namespace.exec_mode == None or namespace.file_name == None):

        return None
    
    else:
        return namespace



def send(config):

    try:
        host = config[c_host]
        port = config[c_port]
        mode = config[c_mode]
        file_name = get_path(config, 'shim')
    
        if not sendSTOP(host, port):
            return False
    
        if not sendDATA(host, port, file_name):
            return False
    
        if mode == e_mode_loop:
            if not sendLOOP(host, port, file_name):
                return False
    
        elif mode == e_mode_one:
            if not sendONE(host, port, file_name):
                return False

    except Exception as E:
        print('error in func _socket_main.send(): %s' % E, sys.stderr)
        return False

    return True


def connect(host, port):
    
    s = None

    try:
    
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
    
            af, socktype, proto, canonname, sa = res
    
            try:
                
                s = socket.socket(af, socktype, proto)
                
            except OSError as msg:
                s = None
                continue
    
            try:
                s.settimeout(2)
                s.connect(sa)
                
            except OSError as msg:
                print(msg, file=sys.stderr)
                s.close()
                s = None
                continue
    
            break
        
        if s is None:
            raise Exception('could not open socket')

    except Exception as E:
        print('error in func _socket_main.connect(): %s' % E, sys.stderr)

    finally:
        return s

def send_cmd(host, port, cmd):

    s = connect(host, port)
    if s == None: return False
    
    try:
        print('<< %s' % cmd)
        s.sendall(cmd)

        data = s.recv(4096)
        if len(data) < 2: return False
        print('>> %s' % (str(data[:2])))

        s.close()
        
        return data[:2] == b'OK'
    
    except OSError as msg:
        print(msg, file=sys.stderr)
        s.close()
        return False


def sendSTOP(host, port):
    return send_cmd(host, port, b'STOP:')

        
def sendDATA(host, port, fileName):

    try:

        arr = open(fileName, 'rb')
        
    except OSError as msg:
        print(msg, file=sys.stderr)
        return False
    
    offset = struct.calcsize(shim.HEADER_PACK)
    
    b = send_cmd(host, port, b'DATA:')
    if not b: return False

    sz = 0
    while True:
        try:
            s = connect(host, port)
            if s == None: return False

            cnt = s.sendfile(arr, offset, 1024)
            if not cnt: break

            data = s.recv(4096)
            if not data:
                s.close()
                return False

            print('.', end='')

            sz = struct.unpack('<I', data[:4])[0]
            offset += 1024

            s.close()

        except OSError as msg:
            print(msg, file=sys.stderr)
            return False

    print('\n%d bytes received' % sz)
    
    return send_cmd(host, port, b'END:')


def sendLOOP(host, port, fileName):

    try:

        arr = open(fileName, 'rb')
        
    except OSError as msg:
        print(msg, file=sys.stderr)
        return False

    #читаем заголовок файла, чтобы найти значение R
    header = struct.unpack(shim.HEADER_PACK, arr.read(struct.calcsize(shim.HEADER_PACK)))
    arr.close

    # отправляем команду и выходим
    return send_cmd(host, port, b'LOOP:' + struct.pack('<I', int(header[shim.HEADER_PACK_KEYS.index('shim_R')])))
    

def sendONE(host, port, fileName):

    try:

        arr = open(fileName, 'rb')
        
    except OSError as msg:
        print(msg, file=sys.stderr)
        return False

    #читаем заголовок файла, чтобы найти значение R
    header = struct.unpack(shim.HEADER_PACK, arr.read(struct.calcsize(shim.HEADER_PACK)))
    arr.close

    # отправляем команду и выходим
    return send_cmd(host, port, b'LOOP:' + struct.pack('<I', int(header[shim.HEADER_PACK_KEYS.index('shim_R')])))


###############################################        

if __name__ == "__main__":

    parser = createParser()
    
    if parser == None:

        host = '172.16.4.55'
        port = 35580
        mode = e_mode_loop
        file_name = "d:/c++/AME/Generators/test_main.shim"
        
    else:

        host = parser.host
        port = parser.port
        mode = parser.exec_mode
        file_name = parser.file_name
    
    print(host)
    send(host=host,
         port=port,
         mode=mode,
         fn=file_name)
