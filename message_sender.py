import settings
import cryptograph
import sender


class message_sender:
    MESSAGE: str

    def __init__(self, soc, arguments):
        self.MESSAGE = arguments[0]
        self.soc = soc

    def send_message(self):
        # check if fragmenting is needed
        if (len(self.MESSAGE) + settings.MY_HEADER > settings.maxFragSize):
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
        lastByte = 0
        unsentMessageSize = len(self.MESSAGE)
        identifier = cryptograph.generateIdentifier()
        fragmentNumber = 0

        while (unsentMessageSize > 0):
            newLastByte = lastByte + settings.maxFragSize

            paycheck = cryptograph.calculatePayCheck(self.MESSAGE[lastByte:newLastByte])

            # completeMessage = sender.build_and_send(soc, identifier, 'FGM', fragmentNumber, paycheck, self.MESSAGE[lastByte:newLastByte])

            new_flag = 'FGM'
            if (unsentMessageSize - newLastByte - lastByte <= 0):
                new_flag = 'FGE'

            if (fragmentNumber % 2 == 0):
                completeMessage = sender.build_and_send(soc, identifier, new_flag, fragmentNumber, paycheck,
                                                        self.MESSAGE[lastByte:newLastByte])
                self.waitForConfirmation(soc)



            unsentMessageSize -= newLastByte - lastByte
            lastByte = newLastByte


            fragmentNumber += 1

    def waitForConfirmation(self, soc):
        data, addr = soc.recvfrom(1024)
