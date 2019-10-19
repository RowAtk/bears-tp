import sys
import getopt

import Checksum
from BasicSender import BasicSender
import Utils
from pprint import pprint

"""
spacket - packet to be sent
rpacket - packet received
"""

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug

    # Main sending loop.
    def start(self):
        # add things here

        packet_msgs = Utils.splitFile(self.infile, 1450) # split message into the bytes to be sent to receiver
        len_msg = len(packet_msgs) # length of split message to be sent
        #
        # initial syn
        seq_num = 0  # initial sequence number
        spacket = self.make_packet('syn',seq_num,'')
        self.send(spacket)
        rpacket = self.receive(500)
        sending = True
        while(sending):
            print rpacket
            seq_num += 1
            spacket = self.make_packet('dat',seq_num,packet_msgs[seq_num-1])
            rpacket = self.receive(500)
            print "hsdhdh"
            self.send(spacket)
            
        # if rpacket:
        #     print rpacket # Received packet indicating the next packet sequence to come next
        #     rmsg_type, rseqno, rdata, rchecksum = self.split_packet(rpacket) # gets the sequence number from the received packet to check for packet loss
            
        # self.send(spacket)


        
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
