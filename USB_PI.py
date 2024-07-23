import os
import subprocess


def readFile(fileDir):
    f = open(fileDir, "r")
    return f.read()

def setConfigTxt():
    text = readFile("/boot/firmware/config.txt")
    if text.find("dtoverlay=dwc2, dr_mode=peripheral") != -1:
        return
    index = text.index("[all]") + len("[all]")
    stringToAdd = "\ndtoverlay=dwc2, dr_mode=peripheral"
    text = text[ : index] + stringToAdd + text[index : ]
    f = open("/boot/firmware/config.txt", "w")
    f.write(text)
    f.close()

def setCmdLineTxt():
    text = readFile("/boot/firmware/cmdline.txt")
    if text.find("modules-load=dwc2,g_ether") != -1:
        return
    index = text.index("fsck.repair=yes ") + len("fsck.repair=yes ")
    stringToAdd = "modules-load=dwc2,g_ether "
    text = text[ : index] + stringToAdd + text[index : ]
    f = open("/boot/firmware/cmdline.txt", "w")
    f.write(text)
    f.close()

def setEtcModules():
    if(os.path.exists("/etc/modules")):
        return
    text = readFile("/etc/modules")
    if text.find("libcomposite") != -1:
        return
    f = open("/etc/modules", "a")
    f.write("\nlibcomposite")
    f.close()

def setEtcDhcpcd():
    if(os.path.exists("/etc/dhcpcd.conf")):
        return
    text = readFile("/etc/dhcpcd.conf")
    if text.find("denyinterfaces usb0") != -1:
        return
    f = open("/etc/dhcpcd.conf", "a")
    f.write("\ndenyinterfaces usb0")
    f.close()

def installDnsmasq():
    subprocess.Popen("sudo apt-get install -y dnsmasq", shell=True)

def setEtcDnsmasq():
    f = open("/etc/dnsmasq.d/usb", "w")
    f.write("interface=usb0\ndhcp-range=10.55.0.2,10.55.0.6,255.255.255.248,1h\ndhcp-option=3\nleasefile-ro")
    f.close() 

def setEtcNetworkInterfaces():
    f = open("/etc/network/interfaces.d/usb0", "w")
    f.write("auto usb0\nallow-hotplug usb0\niface usb0 inet static\naddress 10.55.0.1\nnetmask 255.255.255.248")
    f.close() 

def setRootUsb():
    f = open("/root/usb.sh", "w")
    f.write("#!/bin/bash\ncd /sys/kernel/config/usb_gadget/\nmkdir -p pi4\ncd pi4\necho 0x1d6b > idVendor # Linux Foundation\necho 0x0104 > idProduct # Multifunction Composite Gadget\necho 0x0100 > bcdDevice # v1.0.0\necho 0x0200 > bcdUSB # USB2\necho 0xEF > bDeviceClass\necho 0x02 > bDeviceSubClass\necho 0x01 > bDeviceProtocol\nmkdir -p strings/0x409\necho \"fedcba9876543211\" > strings/0x409/serialnumber\necho \"Ben Hardill\" > strings/0x409/manufacturer\necho \"PI4 USB Device\" > strings/0x409/product\nmkdir -p configs/c.1/strings/0x409\necho \"Config 1: ECM network\" > configs/c.1/strings/0x409/configuration\necho 250 > configs/c.1/MaxPower\nmkdir -p functions/ecm.usb0\nHOST=\"00:dc:c8:f7:75:14\" # \"HostPC\"\nSELF=\"00:dd:dc:eb:6d:a1\" # \"BadUSB\"\necho $HOST > functions/ecm.usb0/host_addr\necho $SELF > functions/ecm.usb0/dev_addr\nln -s functions/ecm.usb0 configs/c.1/\nudevadm settle -t 5 || :\nls /sys/class/udc > UDC\nifup usb0\nservice dnsmasq restart")
    f.close()
    subprocess.Popen("sudo chmod +x /root/usb.sh", shell=True)
    text = readFile("/etc/rc.local")
    if text.find("/root/usb.sh") != -1:
        return
    f = open("/etc/rc.local", "w")
    f.write("/root/usb.sh\n" + text)
    f.close()


setConfigTxt()
setCmdLineTxt()
setEtcModules()
setEtcDhcpcd()
installDnsmasq()
setEtcDnsmasq()
setEtcNetworkInterfaces()
setRootUsb()
