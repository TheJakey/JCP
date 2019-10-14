import socket
import json
import cryptograph
import sender
from receive import file_receiver

class receiver():
    sock: socket
    MAX_PAYCHECK: int

    def __init__(self):
        pass

    def get_file_data(file_data):
        result = b''

        for onePart in file_data:
            result += onePart

        return result


    def confirmPacket(self, addr, identifier, fragmentNumber):
        sender.build_and_send(self.sock, identifier, 'OKE', fragmentNumber, 0, '', addr)

    def requestFragment(self, addr, identifier, fragmentNumber):
        sender.build_and_send(self.sock, identifier, 'MSF', fragmentNumber, 0, '', addr)

    def calculatePaycheck(self, message):
        paycheckCalculated = 0

        if (isinstance(message[0], int)):
            for byte in message:
                # result += int.from_bytes(byte, 'big') * int.from_bytes(byte, 'big')
                paycheckCalculated += byte * byte
        else:
            for byte in message:
                # result += int.from_bytes(byte, 'big') * int.from_bytes(byte, 'big')
                paycheckCalculated += ord(byte) * ord(byte)

        return paycheckCalculated % self.MAX_PAYCHECK

    def validPaycheck(self, data) -> bool:
        paycheckPacket = data.get('paycheck')
        message = data.get('data')
        paycheckCalculated = 0

        if (message != b''):
            paycheckCalculated = self.calculatePaycheck(message)
        else:
            paycheckCalculated = 0

        if (paycheckCalculated == paycheckPacket):
            return True
        else:
            return False

    def receive_file(self, addr, data):
        print('Reeiving file ... ')

        file_data = []
        expectedFragment = 0;
        fragmentNumber = data.get('fragmented')
        packet_flag = data.get('flag')
        identifier = data.get('identifier')

        if not (self.validPaycheck(data)):
            print('ERROR: INVALID PAYCHECK')
            print("Trying to request missing fragment ", fragmentNumber)
            self.requestFragment(addr, identifier, fragmentNumber)

        if not (fragmentNumber == expectedFragment):
            # TODO: REQUEST MISSING FRAGMENT
            print("Trying to request missing fragment ", fragmentNumber)
        else:
            expectedFragment += 1

        self.confirmPacket(addr, identifier, fragmentNumber)

        file_name = data.get('data')
        file = open(file_name, "wb+")

        while packet_flag != 'FIE':  # FILE END
            data, addr = self.sock.recvfrom(1024)
            data = cryptograph.decode(cryptograph, data)

            fragmentNumber = data.get('fragmented')

            if not (self.validPaycheck(data)):
                print('ERROR: INVALID PAYCHECK')
                print("Trying to request missing fragment ", fragmentNumber)
                self.requestFragment(addr, identifier, fragmentNumber)
                continue

            if (fragmentNumber != expectedFragment):
                # TODO: REQUEST MISSING FRAGMENT
                print("Trying to request missing fragment ", fragmentNumber)
                self.requestFragment(addr, identifier, fragmentNumber)
                continue
            else:
                identifier = data.get('identifier')
                expectedFragment += 1

            self.confirmPacket(addr, identifier, fragmentNumber)

            packet_flag = data.get('flag')
            file_data.insert(fragmentNumber, data.get('data'))
            # file_data += data.get('data')


        print('FIE received')

        # file_data += data.get('data')
        file_data.insert(fragmentNumber, data.get('data'))

        file.write(self.get_file_data(file_data))
        file.close()

    def get_fileReceiver_index(self, fileReceivers, packet_identifier):
        print('get file_receive_index triggered')
        result: int

        if (fileReceivers == None):
            result = -1
        else:
            for index, fileReceiver in fileReceivers:
                if (packet_identifier == fileReceivers[index].get_indentifier()):
                    file_receiver_index = index
                    return index

            result = -1

        if (result == -1):
            fileReceivers.appened(file_receiver.FileReceiver())
            return len(fileReceivers) - 1

    def start_receiving(self):
        fileReceivers = None
        MAX_PAYCHECK = 65535

        UDP_PORT = 5005

        self.sock = socket.socket(socket.AF_INET,  # this specifies address family - IPv4 in this case
                             socket.SOCK_DGRAM)  # UDP

        self.sock.bind(('', UDP_PORT))

        while True:
            data, addr = self.sock.recvfrom(1024)
            # print("This is ADDR: ", addr)
            # print(sys.getsizeof(data))

            # data = json.loads(data.decode())
            data = cryptograph.decode(cryptograph, data)

            packet_identifier = data.get('identifier')
            packet_flag = data.get('flag')
            if (packet_flag == 'FIL' or packet_flag == 'FIE'):
                file_receiver_index = self.get_fileReceiver_index(fileReceivers, packet_identifier)

                fileReceivers[file_receiver_index].receive_file_packet(self.sock, addr, data)

                if (packet_flag == 'FIE'):
                    fileReceiver = None

            elif (packet_flag == 'KIA'):


            else:
                identifier = data.get('identifier')
                fragmentNumber = data.get('fragmented')
                self.confirmPacket(addr, identifier, fragmentNumber)

                print('Received data: ', data.get('data'))

