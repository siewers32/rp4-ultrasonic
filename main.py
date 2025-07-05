from modules import jj_midi as midi
from modules import jj_ultrasonic as us
import time

def distance_to_midi_value(distance, min_distance=2, max_distance=400):
    """
    Converteert een afstand in cm naar een MIDI-waarde tussen 0 en 127.
    """
    if distance < min_distance or distance > max_distance:
        return None  # Buiten bereik
    # Normaliseer de afstand naar een waarde tussen 0 en 127
    normalized = (distance - min_distance) / (max_distance - min_distance)
    return int(normalized * 60 + 67)  # Schaal naar MIDI-waarde (60-127)

if __name__ == "__main__":

    TRIG_PIN = 23
    ECHO_PIN = 24

    sensor = None # Initialiseer sensor buiten try-blok voor cleanup

    try:
        midi_sender = midi.MidiSender(port_index=3)
        sensor = us.UltrasonicSensor(TRIG_PIN, ECHO_PIN, unit="cm")

        print("\nStart met meten. Druk Ctrl+C om te stoppen.")
        while True:
            distance = sensor.get_distance()
            if distance is not None:
                print(f"Afstand: {distance} {sensor.unit}")
                print(distance_to_midi_value(distance)) # Converteer afstand naar MIDI-waarde
                midi_value = distance_to_midi_value(distance)
                if midi_value is not None:
                    # Stuur een Control Change op kanaal 0 (MIDI-kanaal 1)
                    # midi_sender.send_control_change(0, 7, midi_value)
                    midi_sender.send_note_on(0, midi_value, 100)  # Speel een noot (C3) met de MIDI-waarde
            else:
                print("Meting mislukt of buiten bereik.")
            time.sleep(0.5) # Wacht 0.5 seconden tussen metingen

    except KeyboardInterrupt:
        print("\nProgramma gestopt door gebruiker.")
    finally:
        # Zorg ervoor dat GPIO wordt opgeruimd, zelfs bij een fout
        if sensor:
            del sensor # Dit roept __del__ aan
        else:
            # Als sensor niet is geïnitialiseerd (bijv. door fout in __init__),
            # dan moeten we GPIO toch opruimen als er iets is ingesteld.
            # Dit is een catch-all, maar idealiter vang je fouten in __init__ al op.
            GPIO.cleanup()

