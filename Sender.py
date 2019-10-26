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
    TIMEOUT = 0.05
    WINDOW_SIZE = 7
    INIT_SEQ = 0
    CONNECTED = False
    PACKET_SIZE = 1450
    # 
    packets = dict()
    fin = -1
    data = [None]*2 # current data and lookahead data


    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug
        self.data[1] = self.infile.read(self.PACKET_SIZE)

    def make_data_packets(self,filename, packet_size, init_seq):
        messages = Utils.splitFile(filename,packet_size)
        packets = [len(messages)]
        for i, message in enumerate(messages[:-1], start=init_seq):
            packets.append(self.make_packet('dat',i,message))
        packets.append(self.make_packet('fin',len(messages),messages[-1]))
        return packets

    def make_window_packets(self):
        self.packets = [None] * WINDOW_SIZE
        seq = 0
        data = self.infile.read(self.PACKET_SIZE)
        ndata = self.infile.read(self.PACKET_SIZE)
        while data and seq < self.WINDOW_SIZE:
            if ndata:
                self.packets[seq] = self.make_packet("dat",seq,data)
            else:
                self.packets[seq] = self.make_packet("fin", seq, data)
            data = ndata
            ndata =  self.infile.read(self.PACKET_SIZE)
            seq += 1
    
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

    def validate(self, packet):
        return Checksum.validate_checksum(packet)        

    def timeouts(self):
        now = time.time()
        for seq, packet in self.packets.items():
            if now - packet["time"] > self.TIMEOUT:
                return seq
        

    # Main sending loop.
    def start(self):
        """ 
        main sending function
        spacket - packet to be sent
        rpacket - packet received 
        tpacket - timed out packet
        seq - current sequence number
        ack - most recent ack number received
        window_start - seq number of first expected packet in window
        fin - sequence # of the final packet
        """
        
        # establish connection
        rpacket = None
        spacket = self.make_packet('syn', self.INIT_SEQ, '')
        while(not self.CONNECTED):
            self.send(spacket)
            print "SENT SYN" 
            rpacket = self.receive(self.TIMEOUT)
            if rpacket:
                print rpacket
                if self.validate(rpacket):
                    self.CONNECTED = True

        # send data
        seq = self.INIT_SEQ + 1
        window_start = seq
        while self.CONNECTED:
            # SENDING PACKETS
            if seq - window_start < self.WINDOW_SIZE or True:  # check if window is full
                msg_type, data = self.getData()
                if msg_type == "fin":   # is this packet the final packet?
                    self.fin = seq
                spacket = self.make_packet(msg_type, seq, data)
                self.packets[seq] = {"packet": spacket, "time": time.time()} # store packet for retransmission
                self.send(spacket)
                seq += 1


            # TIMEOUT HANDLING
            tpacket = self.timeouts()
            if tpacket:
                # retransmit files from tpacket to end of window
                pass

            # RECEIVED PACKET HANDLING
            rpacket = self.receive()
            if self.validate(rpacket):
                print rpacket
                ack = int(self.split_packet(rpacket)[1])
                print(ack)
                del self.packets[ack-1]
                window_start = ack

            # has fin packet been acknowledged? - Connection closing condition
            if self.fin != -1 and ack > self.fin:
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
