from cmd import Cmd
from message_sender import message_sender
from file_sender import file_sender
import socket
import threading
import receive.receiver
import settings

class MyPrompt(Cmd):
    # Socket that is used to send data
    soc = None
    host_name = socket.gethostname() + '> '
    intro = "Welcome! Type ? to list commands"
    # TODO: reconsider this
    # stores instance of receiver
    receiver_instance = None

    def open_socket(self) -> socket:
        '''
        Opens socket IF needed, if socket is already opened, returns that one
        :return: socket
        '''
        if (self.soc == None):
            self.soc = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )

        try:
            self.soc.send( bytes('testing connection', 'UTF-8') )
        except socket.error:
            self.soc = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )

        return self.soc

    def do_exit(self, inp):
        '''exit the application'''
        self.soc.shutdown(socket.SHUT_RDWR)
        self.soc.close()
        print('Exiting.. Bye!')
        return True

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
            defaultValues = settings.get_all()

            for value in defaultValues:
                print(value)

        elif (len(arguments) == 2):
            self.change_settinngs(arguments)


    def help_exit(self):
        print('exit the application. Shorthand: Ctrl-D.')


    def do_receive(self, inp):
        """
        Function creates and starts receiving thread
        :param inp:
        """
        if (self.receiver_instance == None):
            self.receiver_instance = receive.receiver.receiver()
            receive_thread = threading.Thread(target=self.receiver_instance.start_receiving)
            receive_thread.start()
        else:
            print('Receiver already running.')

    def do_message(self, inp):
        '''
        sends message taken as argument
        valid formats:  message <your_message>
                        message <your_message> -<target_IP>
                        message <your_message> -<target_IP> -<target_PORT>
        If any argument is missing, it will be replaced with a default value (you can change default values)
        DONT FORGET THE '-' !!!
        '''
        self.open_socket()

        arguments = inp.split(' -')
        message_sender(self.soc, arguments).send_message()

    def do_file(self, inp):
        '''
        Function will send a file from a separate thread
        :param inp: location of a file you want to send (use 'a' for default)
        :return: none
        '''
        self.open_socket()

        fileSenders.append(file_sender(self.soc, inp))
        file_threads.append(threading.Thread(target=fileSenders[len(fileSenders) - 1].send_file).start())
        # file_sender(self.soc, inp).send_file()
        print()

    def change_settinngs(self, arguments):
        """
        Function serves to change default values loaded in settings.py
        :param arguments: value you want to change and its new value
        :return:
        """

        #
        # TODO: make this to load settings from file
        #

        variable_name = arguments[0][1:]
        new_value = arguments[1]

        # this is just 'switch' for every value in settings
        if (variable_name == 'maxFragSize'):
            new_value = int(new_value)
            if (new_value > 0 and new_value < 1473):
                settings.maxFragSize = new_value
            else:
                print('Invalid value for maxFragSize. Value MUST be greater than 0 and lower then 1490...')
            return

        if (variable_name == 'ipAddress'):
            oktets = new_value.split('.')
            if (len(oktets) == 4):
                settings.ipAddress = new_value
            else:
                print('Invalid value for ipAddress. Value MUST be in format x.x.x.x')
            return

        if (variable_name == 'target_port'):
            new_value = int(new_value)

            if (new_value > 0 and new_value < 65535):
                settings.target_port = new_value
            else:
                print('Invalid value for target_port. Value MUST be greater than 0 and lower then 65535...')
            return

        if (variable_name == 'my_port'):
            new_value = int(new_value)

            if (new_value > 0 and new_value < 65535):
                settings.my_port = new_value
            else:
                print('Invalid value for my_port. Value MUST be greater than 0 and lower then 65535...')
            return

        if (variable_name == 'saveLocation'):
            settings.saveLocation = new_value
            return

        if (variable_name == 'timeOutKeepAlive'):
            new_value = int(new_value)

            if (new_value > 0 and new_value < 60):
                settings.timeOutKeepAlive = new_value
            else:
                print('Invalid value for timeOutKeepAlive. Value MUST be greater than 0 and lower then 60...')
            return

        if (variable_name == 'sent_faulty'):
            if (new_value == 'True' or new_value == 'true'):
                settings.sent_faulty = True
            elif (new_value == 'False' or new_value == 'false'):
                settings.sent_faulty = False
            return


    do_EOF = do_exit
    help_EOF = help_exit

# list of threads - every file is send in a separate one, these are stored here
file_threads = []
# TODO: is it even needed (now/future)?
# list of fileSender instances - may have use in future
fileSenders = []

# starts commandline
MyPrompt().cmdloop()
