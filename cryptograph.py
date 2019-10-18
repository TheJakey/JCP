import random

MAX_PAYCHECK = 65535

def calculatePayCheck(message) -> int:
    result = 0

    if (message == b''):
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

    for i in range(8):
        randomNum = random.randint(33, 126) #the range of numbers is set 33 - 126 cause i need to skip characters like new line, space, del ...
        identifier += chr(randomNum)

    return identifier

def encode(self, tcpDict) -> bytes:
    encodedMessage: str

    identifier = tcpDict.get('identifier')
    flag = tcpDict.get('flag')
    frgmtd = tcpDict.get('fragmented')
    paycheck = tcpDict.get('paycheck')
    data = tcpDict.get('data')

    encodedMessage = identifier.encode('utf-8') + ' - '.encode('utf-8')
    encodedMessage += flag.encode('utf-8') + ' - '.encode('utf-8')
    encodedMessage += str(frgmtd).encode('utf-8') + ' - '.encode('utf-8')
    encodedMessage += str(paycheck).encode('utf-8') + ' - '.encode('utf-8')
    if (isinstance(data, str)):         # encode data as well, if they ARE string
        data = data.encode()
    encodedMessage += data

    return encodedMessage

def decode(self, codedMessage) -> dict:
    decodedMessage = codedMessage.decode('cp855')
    arguments = decodedMessage.split(' - ', 4)
    headerLength = len(arguments[0]) + len(arguments[1]) + len(arguments[2]) + len(arguments[3]) + 12       # 12 becase delimiter ' - ' inside header

    identifier = arguments[0]
    flag = arguments[1]
    fragmented = int(arguments[2])
    paycheck = int(arguments[3])
    data = codedMessage[headerLength:]

    if not (flag == 'FIL' or flag == 'FIE' or data == b''):
        data = data.decode('utf-8')

    tcpDict = dict(
        identifier=identifier,
        flag=flag,
        fragmented=fragmented,
        paycheck=paycheck,
        data=data
    )

    return tcpDict