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

    def make_data_packets(self,filename, packet_size, init_seq):
        messages = Utils.splitFile(filename,packet_size)
        packets = [len(messages)]
        for i, message in enumerate(messages[:-1], start=init_seq):
            packets.append(self.make_packet('dat',i,message))
        packets.append(self.make_packet('fin',len(messages),messages[-1]))
        return packets

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


    # Main sending loop.
    def start(self):
        # add things here
        timeout = 0.5
        connected = False
        window_size = 7
        seq = 0
        packets = self.make_data_packets(self.infile,1450,seq+1)
        # pprint(packets)
        max_seq = packets[0]
        print max_seq
        
        # initial syn
        rpacket = None
        spacket = self.make_packet('syn',seq,'')
        while(not rpacket):
            self.send(spacket)
            print("SEND SYN")
            rpacket = self.receive(timeout)

        connected = True
        # print self.split_packet(rpacket)
        ack = int(self.split_packet(rpacket)[1])
        window_end = (ack + window_size) - 1
        # print ack
        while(connected and ack <= max_seq):    # While connection established and all packets received
            print "SEQ: ", seq, "ACK: ", ack, "WINDOW END: ",window_end
            print rpacket
            # break
            if ack > window_end:
                window_end += window_size

            if ack <= seq:
                self.send(packets[ack])
                # print "\n"
                # self.see_packet(packets[ack])
            elif seq <= window_end:
                seq += 1
                self.send(packets[seq])
                # print "\n"
                # self.see_packet(packets[seq])
            print "DONE SEND"
            rpacket = self.receive(timeout)
            if Checksum.validate_checksum(rpacket):
                ack = int(self.split_packet(rpacket)[1])


        print "SEQ: ", seq, "ACK: ", ack, "WINDOW END: ",window_end

            
        
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
