import socket
import json
import cryptograph
import sender
from receive import file_receiver

sock: socket
MAX_PAYCHECK: int

def get_file_data(file_data):
    result = b''

    for onePart in file_data:
        result += onePart

    return result


def confirmPacket(addr, identifier, fragmentNumber):
    sender.build_and_send(sock, identifier, 'OKE', fragmentNumber, 0, '', addr)

def requestFragment(addr, identifier, fragmentNumber):
    sender.build_and_send(sock, identifier, 'MSF', fragmentNumber, 0, '', addr)

def calculatePaycheck(message):
    paycheckCalculated = 0

    if (isinstance(message[0], int)):
        for byte in message:
            # result += int.from_bytes(byte, 'big') * int.from_bytes(byte, 'big')
            paycheckCalculated += byte * byte
    else:
        for byte in message:
            # result += int.from_bytes(byte, 'big') * int.from_bytes(byte, 'big')
            paycheckCalculated += ord(byte) * ord(byte)

    return paycheckCalculated % MAX_PAYCHECK

def validPaycheck(data) -> bool:
    paycheckPacket = data.get('paycheck')
    message = data.get('data')
    paycheckCalculated = 0

    if (message != b''):
        paycheckCalculated = calculatePaycheck(message)
    else:
        paycheckCalculated = 0

    if (paycheckCalculated == paycheckPacket):
        return True
    else:
        return False

def receive_file(addr, data):
    print('Reeiving file ... ')

    file_data = []
    expectedFragment = 0;
    fragmentNumber = data.get('fragmented')
    packet_flag = data.get('flag')
    identifier = data.get('identifier')

    if not (validPaycheck(data)):
        print('ERROR: INVALID PAYCHECK')
        print("Trying to request missing fragment ", fragmentNumber)
        requestFragment(addr, identifier, fragmentNumber)

    if not (fragmentNumber == expectedFragment):
        # TODO: REQUEST MISSING FRAGMENT
        print("Trying to request missing fragment ", fragmentNumber)
    else:
        expectedFragment += 1

    confirmPacket(addr, identifier, fragmentNumber)

    file_name = data.get('data')
    file = open(file_name, "wb+")

    while packet_flag != 'FIE':  # FILE END
        data, addr = sock.recvfrom(1024)
        data = cryptograph.decode(cryptograph, data)

        fragmentNumber = data.get('fragmented')

        if not (validPaycheck(data)):
            print('ERROR: INVALID PAYCHECK')
            print("Trying to request missing fragment ", fragmentNumber)
            requestFragment(addr, identifier, fragmentNumber)
            continue

        if (fragmentNumber != expectedFragment):
            # TODO: REQUEST MISSING FRAGMENT
            print("Trying to request missing fragment ", fragmentNumber)
            requestFragment(addr, identifier, fragmentNumber)
            continue
        else:
            identifier = data.get('identifier')
            expectedFragment += 1

        confirmPacket(addr, identifier, fragmentNumber)

        packet_flag = data.get('flag')
        file_data.insert(fragmentNumber, data.get('data'))
        # file_data += data.get('data')


    print('FIE received')

    # file_data += data.get('data')
    file_data.insert(fragmentNumber, data.get('data'))

    file.write(get_file_data(file_data))
    file.close()

def start_receiving():
    fileReceiver = None
    MAX_PAYCHECK = 65535

    UDP_PORT = 5006

    sock = socket.socket(socket.AF_INET,  # this specifies address family - IPv4 in this case
                         socket.SOCK_DGRAM)  # UDP

    sock.bind(('', UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        # print("This is ADDR: ", addr)
        # print(sys.getsizeof(data))

        # data = json.loads(data.decode())
        data = cryptograph.decode(cryptograph, data)

        packet_flag = data.get('flag')
        if (packet_flag == 'FIL' or packet_flag == 'FIE'):
            # receive_file(addr, data)
            if (fileReceiver == None):
                fileReceiver = file_receiver.FileReceiver()

            fileReceiver.receive_file_packet(sock, addr, data)

            if (packet_flag == 'FIE'):
                fileReceiver = None

        else:
            identifier = data.get('identifier')
            fragmentNumber = data.get('fragmented')
            confirmPacket(addr, identifier, fragmentNumber)

            print('Received data: ', data.get('data'))

