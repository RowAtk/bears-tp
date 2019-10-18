# bears-tp
COMP2190 Project 1


# Notes
Two parties - sender & receiver

making sender to be compatible with server(receiver)
END GOAL: Go back N protocol

windows size: 7 packets
1000 bytes < |packet| > 1472 bytes

use File read(size) or readlines(size) function to split file into adequate packets payloads


Message Dormat
syn|<sequence number>||<checksum>
dat|<sequence number>|<data>|<checksum>
fin|<sequence number>|<data>|<checksum>
ack|<sequence number>|<checksum>
