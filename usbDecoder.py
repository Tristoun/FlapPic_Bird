import serial 
import threading
import time

class USBDecoder() :
    def __init__(self, port="COM7"):
        self.ser = serial.Serial(port, 9600, timeout=1)
        self.running = False

        self.thread = None
        self.last_value = 0

    def start(self) :
        self.running = True
        self.thread =  threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()


    def stop(self) :
        self.running = False
        self.thread.join()
        self.ser.close()

    def read_loop(self):
        while self.running:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode().strip()
                if data:
                    try:
                        self.last_value = int(data)
                    except ValueError:
                        print("Error while reading data")
            else :
                self.last_value = 0
            time.sleep(0.05)  

    
