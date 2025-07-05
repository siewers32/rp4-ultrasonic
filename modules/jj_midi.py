import rtmidi
import time

class MidiSender:
    """
    Klasse voor het verzenden van MIDI-berichten via python-rtmidi.
    Bundelt functionaliteit voor het openen/sluiten van poorten en het verzenden van diverse MIDI-berichten.
    """

    def __init__(self, port_name=None, port_index=None):
        """
        Initialiseert de MidiSender. Probeer een MIDI-outputpoort te openen.

        Args:
            port_name (str, optional): De volledige of gedeeltelijke naam van de MIDI-poort om te openen.
                                       Bijv. "UM-ONE", "IAC Driver Bus 1", "Midi Gadget".
            port_index (int, optional): De numerieke index van de MIDI-poort om te openen.
                                        Heeft voorrang als zowel port_name als port_index zijn opgegeven.
        """
        self.midiout = rtmidi.MidiOut()
        self.port_name = None # Bewaart de naam van de daadwerkelijk geopende poort
        self.port_index = -1  # Bewaart de index van de daadwerkelijk geopende poort

        available_ports = self.midiout.get_ports()

        if not available_ports:
            print("Geen MIDI outputpoorten gevonden. Zorg ervoor dat je MIDI-apparaat is aangesloten en herkend.")
            self.midiout = None # Markeer als niet-geïnitialiseerd
            return

        if port_index is not None:
            if 0 <= port_index < len(available_ports):
                self.port_index = port_index
                self.port_name = available_ports[port_index]
            else:
                print(f"Waarschuwing: Ongeldige poortindex {port_index}. Beschikbare poorten:")
                for i, name in enumerate(available_ports):
                    print(f"  [{i}]: {name}")
                self.midiout = None
                return
        elif port_name is not None:
            found_index = -1
            for i, name in enumerate(available_ports):
                if port_name.lower() in name.lower():
                    found_index = i
                    break
            if found_index != -1:
                self.port_index = found_index
                self.port_name = available_ports[found_index]
            else:
                print(f"Waarschuwing: Geen MIDI-poort gevonden met naam die '{port_name}' bevat. Beschikbare poorten:")
                for i, name in enumerate(available_ports):
                    print(f"  [{i}]: {name}")
                self.midiout = None
                return
        else:
            # Als niets is opgegeven, toon beschikbare poorten en vraag de gebruiker
            print("Geen MIDI-poort gespecificeerd. Beschikbare poorten:")
            for i, name in enumerate(available_ports):
                print(f"  [{i}]: {name}")
            try:
                chosen_index = int(input("Voer de index in van de MIDI outputpoort die je wilt gebruiken: "))
                if 0 <= chosen_index < len(available_ports):
                    self.port_index = chosen_index
                    self.port_name = available_ports[chosen_index]
                else:
                    print("Ongeldige index ingevoerd.")
                    self.midiout = None
                    return
            except ValueError:
                print("Ongeldige invoer. Voer een nummer in.")
                self.midiout = None
                return

        try:
            self.midiout.open_port(self.port_index)
            print(f"MIDI Sender geïnitialiseerd. Verbonden met poort: {self.port_name} (Index: {self.port_index})")
        except rtmidi.SystemError as e:
            print(f"Fout bij het openen van MIDI-poort {self.port_name}: {e}")
            self.midiout = None # Markeer als niet-geïnitialiseerd


    def _is_ready(self):
        """Controleert of de MIDI outputpoort succesvol is geopend."""
        return self.midiout is not None and self.midiout.is_port_open()

    def send_raw_message(self, message):
        """
        Verzendt een rauw MIDI-bericht (lijst van bytes/integers).

        Args:
            message (list): Een lijst van integers die het MIDI-bericht voorstellen (0-255).
        Returns:
            bool: True als het bericht succesvol is verzonden, anders False.
        """
        if not self._is_ready():
            print("Fout: MIDI-poort is niet geopend.")
            return False
        
        # Basisvalidatie: Zorg ervoor dat alle bytes in het bereik 0-255 liggen
        if not all(0 <= b <= 255 for b in message):
            print(f"Fout: Ongeldige byte(s) in MIDI-bericht: {message}. Alle bytes moeten tussen 0 en 255 liggen.")
            return False

        try:
            self.midiout.send_message(message)
            # print(f"Verzonden: {message} (hex: {[hex(b) for b in message]})") # Optioneel voor debugging
            return True
        except rtmidi.SystemError as e:
            print(f"Fout bij het verzenden van MIDI-bericht: {e}")
            return False

    def send_note_on(self, channel, note_number, velocity):
        """
        Verzendt een MIDI Note On-bericht.

        Args:
            channel (int): MIDI-kanaal (0-15).
            note_number (int): MIDI-nootnummer (0-127).
            velocity (int): Velocity (aanslaggevoeligheid) van de noot (0-127).
        Returns:
            bool: True als het bericht succesvol is verzonden, anders False.
        """
        if not (0 <= channel <= 15 and 0 <= note_number <= 127 and 0 <= velocity <= 127):
            print("Fout: Ongeldige parameters voor Note On. Kanaal (0-15), Noot (0-127), Velocity (0-127).")
            return False
        status_byte = 0x90 | channel
        message = [status_byte, note_number, velocity]
        return self.send_raw_message(message)

    def send_note_off(self, channel, note_number, velocity=0):
        """
        Verzendt een MIDI Note Off-bericht.

        Args:
            channel (int): MIDI-kanaal (0-15).
            note_number (int): MIDI-nootnummer (0-127).
            velocity (int, optional): Velocity van de noot-uit (0-127). Standaard is 0.
                                      (Een Note On met velocity 0 is ook een geldige Note Off).
        Returns:
            bool: True als het bericht succesvol is verzonden, anders False.
        """
        if not (0 <= channel <= 15 and 0 <= note_number <= 127 and 0 <= velocity <= 127):
            print("Fout: Ongeldige parameters voor Note Off. Kanaal (0-15), Noot (0-127), Velocity (0-127).")
            return False
        status_byte = 0x80 | channel
        message = [status_byte, note_number, velocity]
        return self.send_raw_message(message)

    def send_control_change(self, channel, controller_number, value):
        """
        Verzendt een MIDI Control Change (CC) bericht.

        Args:
            channel (int): MIDI-kanaal (0-15).
            controller_number (int): Controller-nummer (0-127).
            value (int): Waarde van de controller (0-127).
        Returns:
            bool: True als het bericht succesvol is verzonden, anders False.
        """
        if not (0 <= channel <= 15 and 0 <= controller_number <= 127 and 0 <= value <= 127):
            print("Fout: Ongeldige parameters voor Control Change. Kanaal (0-15), Controller (0-127), Waarde (0-127).")
            return False
        status_byte = 0xB0 | channel
        message = [status_byte, controller_number, value]
        return self.send_raw_message(message)

    def send_program_change(self, channel, program_number):
        """
        Verzendt een MIDI Program Change (PC) bericht.

        Args:
            channel (int): MIDI-kanaal (0-15).
            program_number (int): Programmanummer (0-127).
        Returns:
            bool: True als het bericht succesvol is verzonden, anders False.
        """
        if not (0 <= channel <= 15 and 0 <= program_number <= 127):
            print("Fout: Ongeldige parameters voor Program Change. Kanaal (0-15), Programma (0-127).")
            return False
        status_byte = 0xC0 | channel
        message = [status_byte, program_number]
        return self.send_raw_message(message)

    def send_pitch_bend(self, channel, bend_value):
        """
        Verzendt een MIDI Pitch Bend-bericht.

        Args:
            channel (int): MIDI-kanaal (0-15).
            bend_value (int): 14-bit pitch bend waarde (-8192 tot 8191, of 0 tot 16383).
                              0 is in het midden (geen bend).
        Returns:
            bool: True als het bericht succesvol is verzonden, anders False.
        """
        if not (0 <= channel <= 15 and -8192 <= bend_value <= 8191):
            print("Fout: Ongeldige parameters voor Pitch Bend. Kanaal (0-15), Waarde (-8192 tot 8191).")
            return False

        # Converteer 14-bit waarde naar twee 7-bit bytes
        # Offset bend_value zodat 0 het laagste is (0 tot 16383)
        converted_value = bend_value + 8192
        lsb = converted_value & 0x7F
        msb = (converted_value >> 7) & 0x7F

        status_byte = 0xE0 | channel
        message = [status_byte, lsb, msb]
        return self.send_raw_message(message)

    def __del__(self):
        """
        Sluit de MIDI-poort wanneer het object wordt vernietigd.
        """
        if self.midiout and self.midiout.is_port_open():
            self.midiout.close_port()
            print(f"MIDI-poort {self.port_name} gesloten.")
        del self.midiout
