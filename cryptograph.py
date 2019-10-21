import random
import bitarray

MAX_PAYCHECK = 65535

flag_dict = dict(
        KIA='00000',
        MSG='00001',
        FGM='00010',
        MSF='00011',
        OKE='00100',
        FIL='00101',
        FIE='00110',
        FGE='00111'
    )

def calculatePayCheck(message) -> int:
    result = 0

    if (message == b'' or message == ''):
        return 0

    if (isinstance(message[0], int)):
        for byte in message:
            # result += int.from_bytes(byte, 'big') * int.from_bytes(byte, 'big')
            result += byte * byte
    else:
        for byte in message:
            # result += int.from_bytes(byte, 'big') * int.from_bytes(byte, 'big')
            result += ord(byte) * ord(byte)


    return result % MAX_PAYCHECK

def generateIdentifier():
    identifier = ''

    for i in range(4):
        randomNum = random.randint(33, 126) #the range of numbers is set 33 - 126 cause i need to skip characters like new line, space, del ...
        identifier += chr(randomNum)

    return identifier

def get_bits_from_flag(flag) -> bitarray:
    return flag_dict.get(flag)

def get_flag_from_bits(flag_bits):
    flag_bits = flag_bits.unpack(zero=b'0', one=b'1')
    flag_bits = flag_bits.decode()

    for key, value in flag_dict.items():
        if (value == flag_bits):
            return key

def encode(self, tcpDict) -> bytes:
    bits = bitarray.bitarray()
    encodedMessage = bitarray.bitarray()

    identifier = tcpDict.get('identifier')
    flag = tcpDict.get('flag')
    frgmtd = tcpDict.get('fragmented')
    paycheck = tcpDict.get('paycheck')
    data = tcpDict.get('data')

    get_bits_from_flag(flag)

    # identifier
    encodedMessage.frombytes(identifier.encode())
    # encodedMessage.extend(bits)

    # flag
    encodedMessage.extend(get_bits_from_flag(flag))

    # reserved
    encodedMessage.extend('000')

    # fragmented
    encodedMessage.frombytes(frgmtd.to_bytes(4, 'big'))
    # encodedMessage.extend(bits)

    # paycheck
    encodedMessage.frombytes(paycheck.to_bytes(2, 'big'))
    # encodedMessage.extend(bits)

    if (isinstance(data, str)):         # encode data as well, if they ARE string
        data = data.encode()

    bits.frombytes(data)
    encodedMessage.extend(bits)

    return encodedMessage.tobytes()

def decode(self, codedMessage) -> dict:
    message_bits = bitarray.bitarray()
    message_bits.frombytes(codedMessage)

    identifier = message_bits[0:32].tostring()
    flag = get_flag_from_bits(message_bits[32:37])
    message_bits[37:40] # reserved not used
    fragmented = int.from_bytes(message_bits[40:72].tobytes(), 'big')
    paycheck = int.from_bytes(message_bits[72:88].tobytes(), 'big')


    if not (flag == 'FIL' or flag == 'FIE'):
        data = message_bits[88:].tostring()
    else:
        data = message_bits[88:].tobytes()

    tcpDict = dict(
        identifier=identifier,
        flag=flag,
        fragmented=fragmented,
        paycheck=paycheck,
        data=data
    )

    return tcpDict