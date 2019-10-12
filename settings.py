class settings:
    maxFragSize = 1020
    ipAddress = '127.0.0.1'
    port = 5005
    saveLocation = './downloads'
    timeOutKeepAlive = 20
    UDP_HEADER = 8
    MY_HEADER = 14 + 28 + 14
    OFFSET = UDP_HEADER + MY_HEADER

    def __init__(self):
        print('new settings')

    def set_maxFragSize(self, maxFragSize):
        self.maxFragSize = maxFragSize

    def set_ipAddress(self, ipAddress):
        self.ipAddress = ipAddress

    def set_port(self, port):
        self.port = port

    def set_saveLocation(self, saveLocation):
        self.saveLocation = saveLocation

    def set_timeOutKeepAlive(self, timeOutKeepAlive):
        self.timeOutKeepAlive = timeOutKeepAlive

    def get_maxFragSize(self):
        return self.maxFragSize

    def get_ipAddress(self):
        return self.ipAddress

    def get_port(self):
        return int(self.port)

    def get_saveLocation(self):
        return self.saveLocation

    def get_timeOutKeepAlive(self):
        return self.timeOutKeepAlive

    def get_header_size(self):
        return self.OFFSET

    def get_all(self):
        list = []

        list.append("Maximum fragment size: " + str(self.maxFragSize))
        list.append("Default Target IP address: " + self.ipAddress)
        list.append("Default Target port: " + str(self.port))
        list.append("Downloaded files save location: " + self.saveLocation)
        list.append("TimeOut Before KeepAlive: " + str(self.timeOutKeepAlive))

        return list


