from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed
        self.receivedData = ""
        self.nextSeqNum = 0
        self.ackNum = 0
        self.unacked = {}
        self.sentAndNotAcked = {}
        self.windowSendBase = 0
        self.timeout = 15
        self.countSegmentTimeouts = 0

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self,data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # Identify the data that has been received...

        # ############################################################################################################ #
        return self.receivedData

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        # ############################################################################################################ #

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)

        # If there is no more data to send
        if self.nextSeqNum * self.DATA_LENGTH >= len(self.dataToSend):
            return

        # Only client sends data segments
        if self.dataToSend != "": 
            # While the next seq number is within the window and there is data left to send
            while (self.nextSeqNum < self.windowSendBase + self.FLOW_CONTROL_WIN_SIZE // self.DATA_LENGTH) and self.nextSeqNum * self.DATA_LENGTH < len(self.dataToSend):
                segmentSend = Segment()
                dataStartIndex = self.nextSeqNum * self.DATA_LENGTH
                dataEndIndex = min(dataStartIndex + self.DATA_LENGTH, len(self.dataToSend))  # Either next 4 char or remaining data
                data = self.dataToSend[dataStartIndex:dataEndIndex]

                # ############################################################################################################ #
                # Display sending segment
                segmentSend.setData(self.nextSeqNum, data)
                print("Sending segment: ", segmentSend.to_string())

                # Use the unreliable sendChannel to send the segment
                self.sendChannel.send(segmentSend)
                self.sentAndNotAcked[self.nextSeqNum] = (segmentSend, self.currentIteration)

                # Current seqNum still needs to be acked
                self.nextSeqNum += 1

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented

        for segment in listIncomingSegments:
            # If segment checksum fails
            if not segment.checkChecksum():
                continue
            
            # ############################################################################################################ #
            # How do you respond to what you have received?
            # How can you tell data segments apart from ack segemnts?

            # If data segment
            if segment.payload:
                print("Received data segment:", segment.to_string())

                # If correct segment order
                if segment.seqnum == self.ackNum:
                    self.ackNum += 1
                    self.receivedData += segment.payload
                else:
                    print(f"Dropping out of order segment {segment.seqnum}, expected {self.ackNum}")
                
                segmentAck = Segment()

                # ############################################################################################################ #
                # Display response segment
                segmentAck.setAck(self.ackNum - 1 if self.ackNum > 0 else 0)
                print("Sending ack:", segmentAck.to_string())

                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)
            
            # Else if ACK segment
            elif segment.acknum != -1:
                print("Received ack:", segment.to_string())       

                if segment.acknum >= self.windowSendBase:
                    # Move window
                    for i in range(self.windowSendBase, segment.acknum + 1):
                        if i in self.sentAndNotAcked:
                            del self.sentAndNotAcked[i]
                    self.windowSendBase = segment.acknum + 1