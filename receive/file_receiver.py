import sender
import cryptograph

MAX_PAYCHECK = 65535

class FileReceiver():
    def __init__(self):
        self.file_data = []
        self.expectedFragment = 0
        self.identifier = ''
        self.file = None
        self.stored_fragments = 0
        self.missing_fragments = []

    def confirmPacket(self, addr, soc, identifier, fragmentNumber):
        sender.build_and_send(soc, identifier, 'OKE', fragmentNumber, 0, '', addr)

    def requestFragment(self, addr, soc, identifier, fragmentNumber):
        sender.build_and_send(soc, identifier, 'MSF', fragmentNumber, 0, '', addr)

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

        return paycheckCalculated % MAX_PAYCHECK

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

    def get_file_data(self, file_data):
        result = b''

        for onePart in file_data:
            result += onePart

        return result

    def receive_file_packet(self, soc, addr, data):
        fragmentNumber = data.get('fragmented')
        packet_flag = data.get('flag')
        identifier_packet = data.get('identifier')

        if (self.identifier == ''):
            self.identifier = identifier_packet
            print('File receiving started!')

        if (self.identifier != identifier_packet):
            print('ERROR: IDENTIFIERS MISSMATCH in file_receive')

        if not (self.validPaycheck(data)):
            print('ERROR: INVALID PAYCHECK')
            print("Trying to request missing fragment ", fragmentNumber)
            self.requestFragment(addr, soc, self.identifier, fragmentNumber)

        if not (fragmentNumber == self.expectedFragment):
            # TODO: REQUEST MISSING FRAGMENT
            print("Trying to request missing fragment ", fragmentNumber)
            self.requestFragment(addr, soc, self.identifier, self.expectedFragment)
            return
        else:
            self.expectedFragment += 1

        if (self.stored_fragments == 4):
            self.confirmPacket(addr, soc, self.identifier, fragmentNumber)
            self.stored_fragments = 0
        else:
            self.stored_fragments += 1

        if (self.file == None):
            if ((self.expectedFragment - 1) != 0):
                print('ERROR: Could not open FILE ')
            else:
                file_name = data.get('data')
                self.file = open(file_name, "wb+")
                self.confirmPacket(addr, soc, self.identifier, fragmentNumber)
                return

        self.file_data.insert(fragmentNumber, data.get('data'))

        if (packet_flag == 'FIE'):
            self.file.write(self.get_file_data(self.file_data))
            self.file.close()
            print('File Received Successfully ')

    def get_indentifier(self):
        return self.identifier