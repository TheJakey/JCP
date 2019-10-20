import select
import socket
import json
import sys
import time
from settings import settings
import cryptograph
import sender



class message_sender:
    MESSAGE: str

    def __init__(self, soc, arguments):
        self.setting = settings()
        self.MESSAGE = arguments[0]
        self.soc = soc

        if (len(arguments) == 2):
            self.setting.set_ipAddress(arguments[1])
            return

        elif (len(arguments) == 3):
            self.setting.set_ipAddress(arguments[1])
            self.setting.set_port(arguments[2])
            return

    def send_message(self):
        # check if fragmenting is needed
        if (len(self.MESSAGE) + self.setting.get_header_size() > self.setting.get_maxFragSize()):
            print("Fragmenting . . .")
            self.sendFragmentedMsg(self.soc)
        else:
            self.sendNOTFragmentedMsg(self.soc)

    def sendNOTFragmentedMsg(self, soc):
        identifier = cryptograph.generateIdentifier()
        paycheck = cryptograph.calculatePayCheck(self.MESSAGE)

        completeMessage = sender.build_and_send(soc, identifier, 'MSG', 0, paycheck, self.MESSAGE)

        self.waitForConfirmation(soc)

    def sendFragmentedMsg(self, soc):
        sequenceNumber = 0
        # lastByte = self.setting.get_maxFragSize() - self.OFFSET - 1  # -1 'cause i need to get to LAST BYTE not the following one
        lastByte = 0
        unsentMessageSize = len(self.MESSAGE)
        identifier = cryptograph.generateIdentifier()
        fragmentNumber = 0

        while (unsentMessageSize > 0):
            newLastByte = lastByte + self.setting.get_maxFragSize() - self.setting.get_header_size()

            paycheck = cryptograph.calculatePayCheck(self.MESSAGE[lastByte:newLastByte])

            completeMessage = sender.build_and_send(soc, identifier, 'FGM', fragmentNumber, paycheck, self.MESSAGE[lastByte:newLastByte])

            unsentMessageSize -= newLastByte - lastByte
            lastByte += newLastByte

            self.waitForConfirmation(soc)

            fragmentNumber += 1

    def waitForConfirmation(self, soc):
        data, addr = soc.recvfrom(1024)
