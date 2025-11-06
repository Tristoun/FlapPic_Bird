import serial
import threading
import time

class USBDecoder():
    def __init__(self, port="COM8"):
        self.ser = serial.Serial(port, 9600, timeout=1)
        self.running = False
        self.thread = None
        self.last_value = 0
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.ser.close()
    
    def send_buzzer_signal(self):
        """Envoie un signal au PIC pour activer le buzzer"""
        try:
            self.ser.write(b'B\n')  # Envoie 'B' pour Buzzer
            self.ser.flush()  # Force l'envoi immédiat
        except Exception as e:
            print(f"Erreur envoi buzzer: {e}")
    
    def send_score(self, score):
        """Envoie le score au PIC pour l'afficher"""
        try:
            msg = f'S{score}\n'  # Format: S + score + retour ligne
            self.ser.write(msg.encode())
            self.ser.flush()
        except Exception as e:
            print(f"Erreur envoi score: {e}")
    
    def read_loop(self):
        while self.running:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode().strip()
                if data:
                    try:
                        self.last_value = int(data)
                    except ValueError:
                        print("Erreur lecture données")
            else:
                self.last_value = 0
            time.sleep(0.05)