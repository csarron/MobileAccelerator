import platform
import math

import usb.core
import usb.util
import struct
from Monsoon import Operations as op

import numpy as np
# import pmapi
from Monsoon import pmapi


class Monsoon(object):

    def __init__(self, *args, **kwargs):
        self.DEVICE = None
        self.DEVICE_TYPE = None
        self.epBulkWriter = None
        self.epBulkReader = None
        self.Protocol = None
        self.statusPacket = op.statusPacket
        self.fineThreshold = 64000
        self.auxFineThreshold = 30000
        self.mainvoltageScale = 4
        self.usbVoltageScale = 2
        self.ADCRatio = (float)(62.5 / 1e6); #Each tick of the ADC represents this much voltage
        self.padding = np.zeros(64)
        pass

    def enumerateDevices(self):
        temp = pmapi.USB_protocol()
        return temp.enumerateDevices()

    def closeDevice(self):
        self.Protocol.closeDevice();

    def setup_usb(self,serialno=None,Protocol=pmapi.USB_protocol()):
        Protocol.Connect(op.HardwareModel.HVPM,serialno)
        self.Protocol = Protocol

    def amps_from_raw(self,raw):
        offset = 3840.0 # == 0x0F00
        scale = float((raw - offset) / (65535.0 - offset))
        result = 15.625 * scale
        return result

    def raw_from_amps(self,value):
        result = ((65535-0x0F00) * (value / 15.625)+0x0F00)
        return result

    def setVout(self,value):
        #Check for overvoltage issue.
        #We've identified an issue with some units where these values are not set properly at the factory.
        #This can cause wildly inaccurate vout settings.  
        #if this fails, update to firmware Rev 32, and run HVPM.calibrateVoltage()
        self.checkDacValues()
        #End check
        vout = value * op.Conversion.FLOAT_TO_INT
        self.Protocol.sendCommand(op.OpCodes.setMainVoltage,vout)
    def setPowerupTime(self,value):
        self.Protocol.sendCommand(op.OpCodes.setPowerupTime,value)
    def setPowerUpCurrentLimit(self, value):
        value = self.raw_from_amps(value)
        self.Protocol.sendCommand(op.OpCodes.SetPowerUpCurrentLimit,value)
    def setRunTimeCurrentLimit(self, value):
        value = self.raw_from_amps(value)
        self.Protocol.sendCommand(op.OpCodes.SetRunCurrentLimit,value)
    def setUSBPassthroughMode(self, USBPassthroughCode):
        self.Protocol.sendCommand(op.OpCodes.setUsbPassthroughMode,USBPassthroughCode)
    def setVoltageChannel(self, VoltageChannelCode):
        self.Protocol.sendCommand(op.OpCodes.setVoltageChannel,VoltageChannelCode)

    def setTemperatureLimit(self,value):
        """Sets the fan turn-on temperature limit.  Only valid in HVPM."""
        raw = self.raw_from_degrees(value)
        self.Protocol.sendCommand(op.OpCodes.setTemperatureLimit,raw)

    def getSerialNumber(self):
        """Get the device serial number"""
        serialNumber = self.Protocol.getValue(op.OpCodes.getSerialNumber,2)
        return serialNumber

    def setDefaultScaleValues(self):
        """Loads default scaling values into the Power Monitor.
        Warning:  This wipes away existing calibration data.  Use with Caution."""
        #Main channel
        self.Protocol.sendCommand(op.OpCodes.setMainFineScale, 36500)
        self.Protocol.sendCommand(op.OpCodes.SetMainFineZeroOffset, 15)
        self.Protocol.sendCommand(op.OpCodes.setMainCoarseScale,6400)
        self.Protocol.sendCommand(op.OpCodes.SetMainCoarseZeroOffset,15)
        #USB Channel
        self.Protocol.sendCommand(op.OpCodes.setUSBFineScale,14000)
        self.Protocol.sendCommand(op.OpCodes.SetUSBFineZeroOffset,0)
        self.Protocol.sendCommand(op.OpCodes.setUSBCoarseScale,600)
        self.Protocol.sendCommand(op.OpCodes.SetUSBCoarseZeroOffset,0)
        #Aux channel
        self.Protocol.sendCommand(op.OpCodes.setAuxFineScale,3100)
        self.Protocol.sendCommand(op.OpCodes.setAuxCoarseScale,250)
    
    def setMainFineScale(self,value):
        self.Protocol.sendCommand(op.OpCodes.setMainFineScale, value)

    def setMainFineZeroOffset(self,value):
        self.Protocol.sendCommand(op.OpCodes.SetMainFineZeroOffset, value)

    def setMainCoarseScale(self,value):
        self.Protocol.sendCommand(op.OpCodes.setMainCoarseScale,value)

    def setMainCoarseZeroOffset(self,value):
        self.Protocol.sendCommand(op.OpCodes.SetMainCoarseZeroOffset,value)


    def setUSBFineScale(self,value):
         self.Protocol.sendCommand(op.OpCodes.setUSBFineScale,value)

    def setUSBFineZeroOffset(self,value):
        self.Protocol.sendCommand(op.OpCodes.SetUSBFineZeroOffset,value)

    def setUSBCoarseScale(self,value):
        self.Protocol.sendCommand(op.OpCodes.setUSBCoarseScale,value)

    def setUSBCoarseZeroOffset(self,value):
        self.Protocol.sendCommand(op.OpCodes.SetUSBCoarseZeroOffset,value)

    def setAuxFineScale(self,value):
        self.Protocol.sendCommand(op.OpCodes.setAuxFineScale,value)

    def setAuxCoarseScale(self,value):
        self.Protocol.sendCommand(op.OpCodes.setAuxCoarseScale,value)


    def getVoltageChannel(self):
        return(self.Protocol.getValue(op.OpCodes.setVoltageChannel,1))

    def StartSampling(self,calTime=1250,maxTime=0xFFFFFFFF):
        self.fillStatusPacket()
        self.Protocol.startSampling(calTime,maxTime)
    def stopSampling(self):
        self.Protocol.stopSampling()

    def raw_from_degrees(self, value):
        """For setting the fan temperature limit.  Only valid in HVPM."""
        lowbyte = int(math.floor(value))
        highbyte = int(min(0xFF,(value-lowbyte) * 2**8)) #Conversion into Q7.8 format
        raw = struct.unpack("H",struct.pack("BB",highbyte,lowbyte))[0]
        return raw


    def degrees_from_raw(self, value):
        """For setting the fan temperature limit.  Only valid in HVPM"""
        value = int(value)
        bytes_ = struct.unpack("BB",struct.pack("H",value)) #Firmware swizzles these bytes_.
        result = bytes_[1] + (bytes_[0] * 2**-8)
        return result

    def calibrateVoltage(self):
        self.Protocol.sendCommand(op.OpCodes.calibrateMainVoltage,0)
    
    def checkDacValues(self):
        #Check for overvoltage issue.
        #We've identified an issue with some units where these values are not set properly at the factory.
        #This can cause wildly inaccurate vout settings.  
        #if this fails, update to firmware Rev 32, and run HVPM.calibrateVoltage()
        dacCalHigh = self.Protocol.getValue(op.OpCodes.dacCalHigh,2)
        dacCalLow = self.Protocol.getValue(op.OpCodes.dacCalLow,2)
        self.__checkDacCalHigh(dacCalHigh)
        self.__checkDacCalLow(dacCalLow)

    def __checkDacCalLow(self, value):
        #Note, these tolerances may be too tight, but due to the severe nature of the bug, better safe than sorry.
        if(value <= 0xE000 or value >= 0xF000):
            raise ValueError("dacCalLow out of tolerance.  Recommend running HVPM.calibrateVoltage()")

    def __checkDacCalHigh(self,value):
        #Note, these tolerances may be too tight, but due to the severe nature of the bug, better safe than sorry.
        if(value <= 0xC000 or value >= 0xD000):
            raise ValueError("dacCalHigh out of tolerance.  Recommend running HVPM.calibrateVoltage()")

    def fillStatusPacket(self):

        #Misc Status information.
        self.statusPacket.firmwareVersion = self.Protocol.getValue(op.OpCodes.FirmwareVersion,2)
        self.statusPacket.protocolVersion = self.Protocol.getValue(op.OpCodes.ProtocolVersion,1)
        self.statusPacket.temperature = -1 #Not currently supported.
        self.statusPacket.serialNumber = self.Protocol.getValue(op.OpCodes.getSerialNumber,2)
        self.statusPacket.powerupCurrentLimit = self.amps_from_raw(self.Protocol.getValue(op.OpCodes.SetPowerUpCurrentLimit,2))
        self.statusPacket.runtimeCurrentLimit = self.amps_from_raw(self.Protocol.getValue(op.OpCodes.SetRunCurrentLimit,2))
        self.statusPacket.powerupTime = self.Protocol.getValue(op.OpCodes.setPowerupTime,1)
        self.statusPacket.temperatureLimit = self.degrees_from_raw(self.Protocol.getValue(op.OpCodes.setTemperatureLimit,2))
        self.statusPacket.usbPassthroughMode = self.Protocol.getValue(op.OpCodes.setUsbPassthroughMode,1)
        self.statusPacket.hardwareModel = self.Protocol.getValue(op.OpCodes.HardwareModel,2)

        self.statusPacket.dacCalHigh = self.Protocol.getValue(op.OpCodes.dacCalHigh,2)
        self.statusPacket.dacCalLow = self.Protocol.getValue(op.OpCodes.dacCalLow,2)

        

        #Calibration data
        self.statusPacket.mainFineScale = float(self.Protocol.getValue(op.OpCodes.setMainFineScale,2))
        self.statusPacket.mainCoarseScale = float(self.Protocol.getValue(op.OpCodes.setMainCoarseScale,2))
        self.statusPacket.usbFineScale = float(self.Protocol.getValue(op.OpCodes.setUSBFineScale,2))
        self.statusPacket.usbCoarseScale = float(self.Protocol.getValue(op.OpCodes.setUSBCoarseScale,2))
        self.statusPacket.auxFineScale = float(self.Protocol.getValue(op.OpCodes.setAuxFineScale,2))
        self.statusPacket.auxCoarseScale = float(self.Protocol.getValue(op.OpCodes.setAuxCoarseScale,2))

        self.statusPacket.mainFineZeroOffset = float(self.Protocol.getValue(op.OpCodes.SetMainFineZeroOffset,2,True))
        self.statusPacket.mainCoarseZeroOffset = float(self.Protocol.getValue(op.OpCodes.SetMainCoarseZeroOffset,2,True))
        self.statusPacket.usbFineZeroOffset = float(self.Protocol.getValue(op.OpCodes.SetUSBFineZeroOffset,2,True))
        self.statusPacket.usbCoarseZeroOffset = float(self.Protocol.getValue(op.OpCodes.SetUSBCoarseZeroOffset,2,True))


    def BulkRead(self):
        """Read sample packets.
        Returns an array of 64 byte packets concatenated together.
        Number of packets depends on the protocol selected."""
        return self.Protocol.BulkRead()

    def swizzlePacket(self, packet):
        length = len(packet)
        packet = np.array(packet)
        evenBytes = packet[4::2]
        oddBytes = packet[5::2]
        swizzledBytes = np.insert(evenBytes,np.arange(len(oddBytes)),oddBytes)
        swizzledPacket = np.hstack([packet[0:4],swizzledBytes[:],self.padding[0:(58-length)]])
        swizzledPacket = np.array(swizzledPacket).astype('B')
        swizzledPacket = swizzledPacket[0:58]
        packetLength = len(swizzledPacket)
        rawBytes = struct.pack('B'*packetLength,*swizzledPacket)
        measurements = struct.unpack("HBBHHHHHHHHBBHHHHHHHHBBHHHHHHHHBB",rawBytes)
        measurements = list(measurements)
        return measurements
    def Reconnect(self):
        self.Protocol.reconnect(op.HardwareModel.HVPM,self.statusPacket.serialNumber)
    def resetToBootloader(self):
        """
        Programmatically reset to bootloader mode.  
        Reconnect using the interface in reflash.py"""
        self.Protocol.resetToBootloader()
        



