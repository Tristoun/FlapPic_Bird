import serial
import threading
import time

class USBDecoder():
    def __init__(self, port="COM10"):
        self.ser = serial.Serial(port, 115200, timeout=1)  # Vitesse du PIC !
        self.running = False
        self.thread = None

        self.last_value = 0
        self.table_active = False
        self.table_buffer = []
        self.table_expected = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.ser.close()
    
    # ======== COMMANDES ENVOI ======== #

    def request_click_table(self):
        try:
            self.ser.write(b'T')
            self.ser.flush()
        except Exception as e:
            print(f"Erreur envoi T: {e}")


    def send_buzzer_signal(self):
        try:
            self.ser.write(b'B\n')
            self.ser.flush()
        except Exception as e:
            print(f"Erreur envoi buzzer: {e}")
    
    def send_score(self, score):
        try:
            msg = f'S{score}\n'
            self.ser.write(msg.encode())
            self.ser.flush()
        except Exception as e:
            print(f"Erreur envoi score: {e}")

    def send_request_table(self):
        """Demande au PIC d'envoyer le tableau EEPROM"""
        try:
            print("➡️ Demande du tableau au PIC...")
            self.table_buffer = []
            self.table_active = False
            self.ser.write(b'T\n')
            self.ser.flush()
        except Exception as e:
            print(f"Erreur envoi requête T: {e}")

    # ======== LECTURE USB ======== #

    def read_loop(self):
        while self.running:
            if self.ser.in_waiting > 0:
                raw = self.ser.readline()
                try:
                    data = raw.decode(errors='ignore').strip()
                except:
                    continue

                if not data:
                    continue

                # --- Détection début tableau ---
                if data.startswith("TABLE "):
                    try:
                        self.table_expected = int(data.split(" ")[1])
                        self.table_buffer = []
                        self.table_active = True
                        print(f"📥 Début de la réception du tableau ({self.table_expected} valeurs)")
                    except:
                        pass
                    continue

                # --- Réception valeurs tableau ---
                if self.table_active:
                    if data.isdigit():
                        self.table_buffer.append(int(data))
                        print(f"[Valeur reçue] {data}")

                        # Si tableau terminé
                        if len(self.table_buffer) >= self.table_expected:
                            self.table_active = False
                            print("✅ Tableau complet reçu :", self.table_buffer)

                    continue

                # --- Sinon message normal ---
                if data.isdigit():
                    self.last_value = int(data)
                    print(f"[Valeur numérique reçue] {data}")
                else:
                    print(f"[Message texte] {data}")

            else:
                self.last_value = 0

            time.sleep(0.03)