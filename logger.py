import datetime
import serial
import time
import csv
import os
import argparse
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()

class logger:
    def __init__(self, **kwargs) -> None:
        self.out_file = kwargs.get("filename", str(datetime.date.today()) + ".csv")
        self.sample = kwargs.get("sample", 100)
        self.delimiter = kwargs.get("delimiter", '\t')
        self.serial_port = kwargs.get("port", None)
        self.baudrate = kwargs.get("baudrate", 115200)

        self.data = []

        self.available_ports = []

        if self.serial_port is None:
            self.list_ports()
            self.select_port()

        self.out_file_path = os.path.dirname(os.path.realpath(__file__)) + "\\" + self.out_file
        
    
    def list_ports(self):
        i = 0
        for port, desc, hwid in sorted(ports):
            self.available_ports.append(port)
            print("[{}] {}: {} [{}]".format(i, port, desc, hwid))
            i+=1
    
    def select_port(self):
        try:
            if len(self.available_ports) == 0:
                raise ValueError("Could not find available serial port.")
            port_index = int(input("> "))
            self.serial_port = self.available_ports[port_index]
            print("{} selected.".format(self.serial_port))
        except ValueError as e:
            print(e)
            exit()
        except:
            print("Port index must be integer.")

    def log(self):
        if (self.serial_port == None):
            print("Serial port must be selected.")
            return
        print("-- LOGGER STARTED --")

        ser = serial.Serial(port=self.serial_port, baudrate=self.baudrate)
        ser.flushInput()

        try:
            print("Out File Path: {}".format(self.out_file_path))
            with open(self.out_file_path, 'w', newline='') as file:
                writer = csv.writer(file, delimiter=self.delimiter)

                while True:
                    try:
                        ser_bytes = ser.readline()
                        result = ser_bytes.decode('utf-8')[1:]
                        raw_data = result.split(" ")

                        temp_data = []
                        for rdata in raw_data:
                            temp_data.append(float(rdata))
                        
                        print(temp_data)
                        
                        self.data.append(temp_data)

                    except Exception as e:
                        print(e)

                    if len(self.data) > self.sample:
                        writer.writerows(self.data)
                        self.data.clear()
                        print("Writed")

                    time.sleep(0.01)
        except KeyboardInterrupt as e:
            ser.close()
            print("-- LOGGER STOPPED --")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--delimiter", required=False, help="CSV Delimiter", default='\t')
    ap.add_argument("-s", "--sample", required=False, help="Save Frequency", default=100)
    ap.add_argument("-p", "--port", required=False, help="Device Port", default=None)
    ap.add_argument("-f", "--filename", required=False, help="CSV Filename", default=None)
    ap.add_argument("-b", "--baudrate", required=False, help="UART Baudrate", default=115200)
    args = vars(ap.parse_args())


    l = logger(filename=args["filename"], port=args["port"], delimiter=args["delimiter"], sample=args["sample"])
    l.log()

