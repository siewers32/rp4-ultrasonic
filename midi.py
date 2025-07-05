import time
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
midiin = rtmidi.MidiIn()


def send_control_change(port_index, channel, controller_number, value):
    """
    Sends a Control Change message.

    Args:
        port_index (int): The index of the MIDI output port.
        channel (int): MIDI channel (0-15).
        controller_number (int): MIDI controller number (0-127).
        value (int): Controller value (0-127).
    """
    if not (0 <= channel <= 15 and 0 <= controller_number <= 127 and 0 <= value <= 127):
        print("Invalid MIDI parameters. Channel (0-15), Controller (0-127), Value (0-127).")
        return

    cc_status = 0xB0 | channel # 0xB0 is Control Change
    cc_message = [cc_status, controller_number, value]

    print(f"\nSending Control Change: Channel {channel}, Controller {controller_number}, Value {value}")
    send_midi_message(port_index, cc_message)


def send_midi_message(port_index, message):
    """
    Sends a MIDI message to the specified output port.

    Args:
        port_index (int): The index of the MIDI output port to use.
        message (list): A list of integers representing the MIDI message bytes.
    """
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if not available_ports:
        print("No MIDI output ports found. Please ensure your device is connected and recognized.")
        return

    if port_index >= len(available_ports) or port_index < 0:
        print(f"Invalid port index {port_index}. Available ports:")
        for i, port_name in enumerate(available_ports):
            print(f"  [{i}]: {port_name}")
        return

    try:
        midiout.open_port(port_index)
        port_name = available_ports[port_index]
        print(f"Sending to port: {port_name}")

        print(f"  Sending message: {message} (hex: {[hex(b) for b in message]})")
        midiout.send_message(message)
        time.sleep(0.1) # Give a small delay to ensure message is sent
    except rtmidi.SystemError as e:
        print(f"Error opening or sending MIDI message: {e}")
    finally:
        del midiout # Close the MIDI output when done


print("Available MIDI input ports:")
ports = range(midiin.get_port_count())
if ports:
    for i in ports:
        print(midiin.get_port_name(i))

    
print ("Available MIDI ports:")
for i, port in enumerate(available_ports):
    print(f"{i}: {port}")

send_control_change(3, 0, 90, 127)