import time
from modules import jj_midi as midi

if __name__ == "__main__":
    # Opties voor het initialiseren van de MidiSender:
    # 1. Handmatig een index opgeven (handig als je de index weet)
    #    midi_sender = MidiSender(port_index=0)
    # 2. Handmatig een deel van de naam opgeven (handig als de index kan variëren)
    #    midi_sender = MidiSender(port_name="Midi Gadget") # Voor Raspberry Pi Zero gadget
    #    midi_sender = MidiSender(port_name="IAC Driver Bus 1") # Voor macOS
    #    midi_sender = MidiSender(port_name="loopMIDI Port 1") # Voor Windows
    # 3. Laat de gebruiker een keuze maken uit de beschikbare poorten (standaard)
    midi_sender = midi.MidiSender(port_index=3)

    if midi_sender._is_ready(): # Controleer of de poort succesvol is geopend
        try:
            print("\nStart MIDI-sequenties. Druk Ctrl+C om te stoppen.")

            # Speel een eenvoudige C-majeur arpeggio op kanaal 0 (MIDI-kanaal 1)
            print("\nSpeel C-majeur arpeggio (C3, E3, G3, C4)...")
            notes = [60, 64, 67, 72] # C3, E3, G3, C4
            for note in notes:
                midi_sender.send_note_on(0, note, 100)
                time.sleep(0.3)
                midi_sender.send_note_off(0, note)
                time.sleep(0.1)

            time.sleep(1) # Korte pauze

            # Verander instrument (Program Change) op kanaal 0
            print("\nVerander instrument naar 'Acoustic Guitar (steel)' (Program Change 25)...")
            midi_sender.send_program_change(0, 25)
            time.sleep(0.5)

            # Speel opnieuw de arpeggio met het nieuwe instrument
            print("Speel opnieuw C-majeur arpeggio met nieuw instrument...")
            for note in notes:
                midi_sender.send_note_on(0, note, 90)
                time.sleep(0.3)
                midi_sender.send_note_off(0, note)
                time.sleep(0.1)

            time.sleep(1)

            # Stuur een Control Change (Modulation Wheel, CC#1)
            print("\nStuur Modulation Wheel (CC#1) van 0 naar 127 en terug...")
            for value in range(0, 128, 10):
                midi_sender.send_control_change(0, 1, value)
                time.sleep(0.1)
            for value in range(127, -1, -10):
                midi_sender.send_control_change(0, 1, value)
                time.sleep(0.1)

            time.sleep(1)

            # Stuur een Pitch Bend
            print("\nStuur Pitch Bend van -8192 naar 8191 en terug (over noot D4)...")
            midi_sender.send_note_on(0, 62, 100) # Speel D4
            time.sleep(0.5)
            for bend in range(-8192, 8192, 500):
                midi_sender.send_pitch_bend(0, bend)
                time.sleep(0.05)
            for bend in range(8191, -8193, -500):
                midi_sender.send_pitch_bend(0, bend)
                time.sleep(0.05)
            midi_sender.send_pitch_bend(0, 0) # Zet Pitch Bend terug naar midden
            midi_sender.send_note_off(0, 62) # Noot uit

        except KeyboardInterrupt:
            print("\nProgramma gestopt door gebruiker.")
        except Exception as e:
            print(f"Een onverwachte fout is opgetreden: {e}")
        finally:
            # De __del__ methode wordt automatisch aangeroepen wanneer het script eindigt
            # of wanneer het object buiten scope valt/wordt verwijderd.
            print("Klaar met MIDI-verzending.")
    else:
        print("Kan geen MIDI-sender initialiseren, programma beëindigd.")