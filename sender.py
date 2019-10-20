import cryptograph
from settings import settings

setting = settings()


def build_and_send(soc, identifier, flag, fragmentNumber, paycheck, message, *args):
    '''
    Builds and sends message as UDP packet.
    :param soc:
    :param identifier:
    :param flag:
    :param fragmentNumber:
    :param message:
    :return: encoded message that's ready to be send. Contains encoded dictionary with message
    '''

    tcpDict = dict(
        identifier=identifier,
        flag=flag,
        fragmented=fragmentNumber,
        paycheck=paycheck,
        data=message
    )

    completeMessage = cryptograph.encode(cryptograph, tcpDict)

    if (args.__len__() == 0):
        soc.sendto(completeMessage, (setting.get_ipAddress(), setting.get_target_port()))
    else:
        soc.sendto(completeMessage, (args[0]))

    return completeMessage


def send_message(soc, completeMessage, *args):
    if (args.__len__() == 0):
        soc.sendto(completeMessage, (setting.get_ipAddress(), setting.get_target_port()))
    else:
        soc.sendto(completeMessage, (args[0]))
