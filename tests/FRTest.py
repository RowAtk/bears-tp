from BasicTest import *

class FRTest(BasicTest):
    """ test fast retransmission """
    def __init__(self, name, forwarder, input_file, droplist):
        super(FRTest, self).__init__(name, forwarder, input_file)

        self.dropCount = dict()
        self.droplist = droplist
        for seq in self.droplist:
            self.dropCount[seq] = 0
        print("count made")
        
    
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            print p
            print("IN FOR")
            
            pseq = int(p[0])
            if pseq not in self.droplist:
                print "dont drop"
                self.dropCount[pseq] += 1
            elif self.dropCount[pseq] >= 4:
                print "done dropping"
                self.forwarder.out_queue.append(p)
            else:
                print "drop and increment"
                self.dropCount[pseq] += 1
                
        
        # empty out the in_queue
        self.forwarder.in_queue = []