# for privacy reasons I won't fill some gaps (such as my city), so you will have to put yours in

import hid
import time
import datetime
import requests
import sys
API_KEY = "Insert_API_KEY"   
CITY    = "Rome,IT"                          
UPDATE_INTERVAL = 1800                         # ogni ora

KEYBOARD_VID = 0x4C52
KEYBOARD_PID = 0x0001


# 0=sole 1=nuvola 2=pioggia 3=neve 4=temporale 5=nebbia
def weather_code(owm_id):
    if owm_id in range(200, 300): return 4  
    if owm_id in range(300, 600): return 2 
    if owm_id in range(600, 700): return 3  
    if owm_id in range(700, 800): return 5 
    if owm_id == 800:             return 0  
    if owm_id in range(801, 900): return 1  
    return 0
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        owm_id = data["weather"][0]["id"]
        temp   = round(data["main"]["temp"])
        desc   = data["weather"][0]["description"]
        code   = weather_code(owm_id)
        print(f"  Meteo: {desc} ({temp}°C) → codice {code}")
        return code
    except Exception as e:
        print(f"  ⚠️  errore: {e} — uso sole come default")
        return 0

def find_keyboard():
    for device in hid.enumerate():
        if device["vendor_id"] == KEYBOARD_VID and device["product_id"] == KEYBOARD_PID:
            if device["usage_page"] == 0xFF60 and device["usage"] == 0x61:
                return device["path"]
    return None

def send_to_keyboard(path, time_str, date_str, weather):
    """
    Invia i dati all'OLED della tastiera tramite RAW HID.
    Pacchetto 32 byte:
      [0]    = 0x01 (comando aggiorna display)
      [1..8] = ora  "HH:MM:SS"
      [9..18]= data "DD/MM/YYYY"
      [19]   = codice meteo
    """
    packet = [0x00] * 33  
    packet[1]  = 0x01     
    for i, c in enumerate(time_str[:8]):
        packet[2 + i] = ord(c)
    for i, c in enumerate(date_str[:10]):
        packet[10 + i] = ord(c)
    packet[20] = weather

    try:
        device = hid.device()
        device.open_path(path)
        device.write(packet)
        device.close()
        return True
    except Exception as e:
        print(f"  ⚠️  errore invio HID: {e}")
        return False


def main():
    print("Lorenzo's Hackpad — Aggiornamento OLED")
    print("=" * 40)
    current_weather = 0
    weather_last_update = 0

    print(f"Cercando tastiera (VID={hex(KEYBOARD_VID)}, PID={hex(KEYBOARD_PID)})...")

    while True:
        now  = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d/%m/%Y")
# ogni 10 min
        if time.time() - weather_last_update > 600:
            print(f"\n[{time_str}] Aggiornamento meteo...")
            current_weather = get_weather()
            weather_last_update = time.time()
        path = find_keyboard()
        if path:
            ok = send_to_keyboard(path, time_str, date_str, current_weather)
            status = "✓" if ok else "✗"
            print(f"[{time_str}] {date_str} | meteo={current_weather} | HID {status}")
        else:
            print(f"[{time_str}] Tastiera non trovata — riprovo tra {UPDATE_INTERVAL}s")

        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrotto.")
