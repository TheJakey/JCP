import sender
import cryptograph
import settings

MAX_PAYCHECK = 65535


class FileReceiver():
    def __init__(self):
        self.file_data = []
        self.expectedFragment = 0
        self.identifier = ''
        self.file = None
        self.stored_fragments = 0
        self.missing_fragments = []
        self.buffer = []

    def confirmPacket(self, addr, soc, identifier, fragmentNumber):
        sender.build_and_send(soc, identifier, 'OKE', fragmentNumber, 0, '', addr)

    def requestFragments(self, addr, soc, identifier):
        str_missing_fragments = self.get_string_of_missing_fragments()
        sender.build_and_send(soc, identifier, 'MSF', 0, 0, str_missing_fragments, addr)

    def get_string_of_missing_fragments(self):
        string_of_missing_fragments = ''

        for fragment in self.missing_fragments:
            string_of_missing_fragments += str(fragment) + '-'

        return string_of_missing_fragments[:-1]

    def add_fragment_number_to_missing_list(self, fragmentNumber):
        try:
            if (self.buffer[fragmentNumber] != None):
                pass
            print("Received fragment, thast not expected, was already stored in a buffer")
            return 1
        except IndexError:
            self.missing_fragments.append(fragmentNumber)
            print("Added to missing fragments: ", fragmentNumber)
            return 0


    def calculatePaycheck(self, message, data):
        paycheckCalculated = 0

        if message == '':
            return

        if (isinstance(message[0], int)):
            for byte in message:
                paycheckCalculated += byte * byte
        else:
            for byte in message:
                paycheckCalculated += ord(byte) * ord(byte)

        return paycheckCalculated % MAX_PAYCHECK

    def validPaycheck(self, data) -> bool:
        paycheckPacket = data.get('paycheck')
        message = data.get('data')
        paycheckCalculated = 0

        if (message != b''):
            if (message != ''):
                paycheckCalculated = self.calculatePaycheck(message, data)
            else:
                paycheckCalculated = 0
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

        if (self.file == None and packet_flag == 'MSF'):
            print('MSF prislo, no prvy fragment ne - file je none')
            return

        if (self.identifier == ''):
            # TODO: DELETE before release
            if (packet_flag == 'FIE'):
                print("PACKET FLAG FIE WHEN IT SHOUDLNT")
                # JUST this ^ part
            self.identifier = identifier_packet
            print('File receiving started!')

        if (self.identifier != identifier_packet):
            print('ERROR: IDENTIFIERS MISSMATCH in file_receive')

        # TODO: Pridaj sem pridanie do pozadovanych fragmentov
        if not (self.validPaycheck(data)):
            print('ERROR: INVALID PAYCHECK')
            print("Trying to request missing fragment ", fragmentNumber)
            self.missing_fragments.append(fragmentNumber)
            self.expectedFragment += 1
            self.stored_fragments += 1
            return

        if (packet_flag == 'MSF'):
            self.requestFragments(addr, soc, self.identifier)
            return

        self.expectedFragment += 1

        if (self.file == None):
            if ((self.expectedFragment - 1) != 0):
                print('ERROR: Could not open FILE ')
            else:
                file_name = data.get('data')
                self.save_to = settings.saveLocation + file_name.decode()
                self.file = open(self.save_to, "wb+")
                self.confirmPacket(addr, soc, self.identifier, fragmentNumber)
                self.stored_fragments += 1
                return

        self.buffer.insert(fragmentNumber, data.get('data'))

        if (self.stored_fragments == 49):
            if len(self.missing_fragments) == 0:
                print('Confirming packets')
                self.confirmPacket(addr, soc, self.identifier, fragmentNumber)
            else:
                self.requestFragments(addr, soc, self.identifier)
                data, addr = soc.recvfrom(1024)
                data = cryptograph.decode(cryptograph, data)
                fragmentNumber = data.get('fragmented')
                self.buffer.insert(fragmentNumber, data.get('data'))
                self.confirmPacket(addr, soc, self.identifier, 0)

            self.save_buffer()
            self.delete_old_buffer()
            self.missing_fragments = []
            self.stored_fragments = 0
        else:
            self.stored_fragments += 1

        if (packet_flag == 'FIE' and len(self.missing_fragments) == 0):
            self.save_buffer()
            self.confirmPacket(addr, soc, self.identifier, fragmentNumber)
            self.file.close()
            print('File Received Successfully....')
            print('save location: ', self.save_to)

    def get_indentifier(self):
        return self.identifier

    def save_buffer(self):
        file_data = b''

        for data in self.buffer:
            file_data += data

        self.file.write(file_data)

    def delete_old_buffer(self):
        self.buffer = []