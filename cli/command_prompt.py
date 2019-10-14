from cmd import Cmd
from message_sender import message_sender
from file_sender import file_sender
import socket
import cryptograph
import threading
import receive.receiver
from settings import settings

class MyPrompt(Cmd):
    soc = None
    prompt = socket.gethostname() + '> '
    intro = "Welcome! Type ? to list commands"

    def open_socket(self) -> socket:
        '''
        Opens socket IF needed, if socket is already opened, returns that one
        :return: socket
        '''
        try:
            self.soc.send( bytes('testing connection', 'UTF-8') )
        except socket.error:
            self.soc = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
            # to ensure, that the recvfrom won't be endless, if nothing is received (but ju still need to block it yourself)
            # or use settimeout() - argument is time until timeout_exception is thrown
            self.soc.setblocking(False)

        return self.soc

    def do_exit(self, inp):
        '''exit the application'''
        self.soc.shutdown(socket.SHUT_RDWR)
        self.soc.close()
        print('Exiting.. Bye!')
        return True

    def do_add(self, inp):
        '''if you read this. U shouldn't this thing should be gone by the time u get here'''
        print("Adding '{}'".format(inp))

    def do_default(self, inp):
        '''
        Serves for changing the default values.
        To display current defaults, just leave it WITHOUT arguments

        maxFragSize = maximum size of fragment
        ipAddress = destination IP address
        port = destination PORT
        savelocation = location where you want to save your downloaded files
        timeOutKeepAlive = Time until first KeepAlive packet is send

        :param inp: -<parameter you want to change> -<it's new value>
        :return:
        '''
        arguments = inp.split(' -')
        print(len(arguments))
        if (len(arguments) == 1):
            defaultValues = settings.get_all(settings)

            for value in defaultValues:
                print(value)


    def help_exit(self):
        print('exit the application. Shorthand: Ctrl-D.')

        def do_mama(self, inp):
            '''if you read this. U shouldn't this thing should be gone by the time u get here'''
            cryptograph.generateIdentifier()
            halaluja = 'mama'
            print("String: ", halaluja.__sizeof__())
            halaluja_bytes = halaluja.encode()
            print("Bytes: ", halaluja_bytes.__sizeof__())
            print(len(halaluja))

        # print("Default: {}

    def do_receive(self, inp):
        receiverInstance = receive.receiver.receiver()
        receive_thread = threading.Thread(target=receiverInstance.start_receiving)
        receive_thread.start()

    def do_message(self, inp):
        '''
        send message
        valid formats:  message <your_message>
                        message <your_message> -<target_IP>
                        message <your_message> -<target_IP> -<target_PORT>
        If any argument is missing, it will be replaced with a default value (you can change default values)
        DONT MISS THE '-' !!!
        '''
        self.open_socket()

        arguments = inp.split(' -')
        message_sender(self.soc, arguments).send_message()

    def do_file(self, inp):
        '''
        Function will send a file
        :param inp: location of a file you want to send (use 'a' for default)
        :return: none
        '''
        self.open_socket()

        fileSender = file_sender(self.soc, inp)
        fileThread = threading.Thread(target=fileSender.send_file)
        fileThread.start()
        # file_sender(self.soc, inp).send_file()

    do_EOF = do_exit
    help_EOF = help_exit

MyPrompt().cmdloop()

print("after")