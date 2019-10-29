import sys
import getopt

import Checksum
from BasicSender import BasicSender
import Utils
import time

"""
spacket - packet to be sent
rpacket - packet received
"""

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender):

    # constants
    TIMEOUT = 0.5
    WINDOW_SIZE = 7
    INIT_SEQ = 0
    CONNECTED = False
    PACKET_SIZE = 1450

    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug
        self.data = [None, self.infile.read(self.PACKET_SIZE)]  # current data and lookahead data
        self.seq = self.INIT_SEQ    # sequence number of next packet to be sent
        self.ack = None             # ack number of most recently acknowledged packet
        self.spacket = None         # packet to be sent
        self.rpacket = None         # packet last receieved - may be None if no packets in receive buffer
        self.packets = dict()       # collection of stored unacknowledged packets
        self.fin = -1               # sequence number of final packet sent
        self.ack_count = [None, 0]  # counter for duplicate ack numbers received

    def getData(self):
        self.data[0] = self.data[1]
        self.data[1] = self.infile.read(self.PACKET_SIZE)
        if self.data[1]:
            return 'dat', self.data[0]
        return 'fin', self.data[0]

    def see_packet(self, packet, mode='s'):
        msg_type, seqno, data, checksum = self.split_packet(packet)
        try:
            seqno = int(seqno)
        except:
            raise ValueError
        if mode == 's':
            print "packet: %s|%d|%s|%s" % (msg_type, seqno, data[:5], checksum)
        else:
            print "packet: %s|%d|%s|%s" % (msg_type, seqno, data, checksum)

    def stored_packets(self):
        print "\nPACKET STORE"
        for packet in self.packets.values():
            self.see_packet(packet["packet"])
        print "\n"

    def validate(self, packet):
        return Checksum.validate_checksum(packet)        

    def timeouts(self):
        now = time.time()
        for seq, packet in self.packets.items():
            if now - packet["time"] > self.TIMEOUT:
                print("PACKET TIMED OUT")
                return seq
        return None
    
    def store_packet(self):
        """ store packet for retransmission """
        self.packets[self.seq] = {"packet": self.spacket, "time": time.time()}

    def connect(self):
        """ connect to receiver """
        self.spacket = self.make_packet('syn', self.INIT_SEQ, '')
        while not self.CONNECTED:
            self.send(self.spacket)
            self.rpacket = self.receive(self.TIMEOUT)
            if self.rpacket:
                print self.rpacket
                if self.validate(self.rpacket):
                    self.CONNECTED = True
        print "CONNECTED !!!!!!"

    def send_data(self):
        """ send packets to receiver """
        if self.seq - self.window_start < self.WINDOW_SIZE:   # check if window is full
            msg_type, data = self.getData()
            if data:
                if msg_type == 'fin':   # is this the final packet?
                    self.fin = self.seq
                self.spacket = self.make_packet(msg_type, self.seq, data)
                self.store_packet()
                self.send(self.spacket)
                self.seq += 1

    def gbn_retransmit(self, start):
        print "TIMEOUT"
        for i in range(start, self.seq):
            self.spacket = self.packets[i]["packet"]
            self.send(self.spacket)
    
    def handle_duplicates(self):
        if self.ack != self.ack_count[0]:
            self.ack_count[0] = self.ack
            self.ack_count[1] = 1
        else:
            self.ack_count[1] += 1
            if self.ack_count[1] >= 4:
                print("FAST RETRANSMISSION")
                self.send(self.packets[self.ack])

    def receive_packet(self):
        try:    
            self.rpacket = self.receive(0)
            if self.validate(self.rpacket):
                self.ack = int(self.split_packet(self.rpacket)[1])
                self.handle_duplicates()    # handle any fast retransmission triggers

                if self.ack > self.window_start and self.ack < self.seq:    # delete ack'd packets from storage
                    while self.window_start < self.ack:
                        del self.packets[self.window_start]
                        self.window_start += 1
        except:
            self.rpacket = None

        
    # Main sending loop.
    def start(self):
        """ main sending function """
    
        self.connect()  # establish connection
        self.ack = int(self.split_packet(self.rpacket)[1])
        self.seq = self.ack
        self.window_start = self.seq
        while self.CONNECTED:
            # SEND #
            self.send_data()

            # TIMEOUT #
            tseq = self.timeouts()
            if tseq:
                # retransmit files from tpacket to current packet
                self.gbn_retransmit(tseq)

            # RECEIVE #
            self.receive_packet()

            # has fin packet been acknowledged? - Connection closing condition
            if self.fin != -1 and self.ack > self.fin:
                print("CLOSE CONNECTION")
                self.CONNECTED = False

        
        
'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest,port,filename,debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
