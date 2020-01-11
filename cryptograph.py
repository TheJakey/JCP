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
    """
    Paycheck - something like checkSum implemented only on payload (first misunderstanding of this concept)
    Function calculates value and returns result as int

    Since it only calculates payCheck value from payload, it's kinda useless, it wont be able to detect a defect
    in header made during data transfer

    Also used approach to calculate a payCheck value is just stupid

    IMPORTANT!!
    This will be removed, feel free to ignore it's existence

    :param message: a message to be transferred to int in range 0 - MAX_PAYCHECK
    :return:
    """
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

def generateIdentifier() -> str:
    """
    Creates message identifier
    this is made to recognize message type

    identifier - few chars made to identify message, stays the same across all messages of one transfer (one file,
                longer text message, ...)

    :return: identifier
    """

    identifier = ''

    for i in range(4):
        # TODO: change range, so there is less waste of space OR more different identifiers !!
        randomNum = random.randint(33, 126) #the range of numbers is set 33 - 126 cause i need to skip characters like new line, space, del ...
        identifier += chr(randomNum)

    return identifier

def get_bits_from_flag(flag) -> bitarray:
    """
    Translates flag string to it's bits value
    :param flag: 3 char long name of flag
    :return: bits matching given flag
    """
    return flag_dict.get(flag)

def get_flag_from_bits(flag_bits):
    """
    Translates flag bits to corresponding string
    :param flag_bits: flag in bitarray variable
    :return: corresponding string to given bitarray
    """
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