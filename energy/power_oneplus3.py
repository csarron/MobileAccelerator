import Monsoon.LVPM as LVPM
import Monsoon.pmapi as pmapi


def power_on(serial_no=None, protocol=pmapi.USB_protocol()):
    Mon = LVPM.Monsoon()
    Mon.setup_usb(serial_no, protocol)
    print("LVPM Serial number: " + repr(Mon.getSerialNumber()))
    Mon.fillStatusPacket()
    Mon.setVout(4.2)
    # Mon.closeDevice();


if __name__ == "__main__":
    power_on('09192')

