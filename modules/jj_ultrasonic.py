import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    """
    Klasse voor het uitlezen van een HC-SR04 ultrasone afstandssensor op een Raspberry Pi.

    De HC-SR04 heeft 4 pinnen: VCC, GND, Trig, Echo.
    Vergeet niet een spanningsdeler (voltage divider) te gebruiken op de Echo pin
    als je de sensor met een 5V voeding gebruikt en de Raspberry Pi met 3.3V GPIO's werkt!
    """

    # Snelheid van geluid in lucht (meter per seconde) bij ca. 20°C
    # Pas dit aan voor nauwkeurigere metingen bij afwijkende temperaturen
    # De snelheid van geluid varieert met temperatuur: ~331.3 + (0.606 * temperatuur_celsius) m/s
    SPEED_OF_SOUND_CM_PER_S = 34320  # cm/s (ongeveer 343.2 m/s)

    def __init__(self, trig_pin, echo_pin, unit="cm", timeout_s=1.0):
        """
        Initialiseert de ultrasone sensor.

        Args:
            trig_pin (int): Het GPIO BCM-nummer van de TRIG-pin van de sensor.
            echo_pin (int): Het GPIO BCM-nummer van de ECHO-pin van de sensor.
            unit (str, optional): De gewenste eenheid voor de afstand ('cm' of 'm'). Standaard is 'cm'.
            timeout_s (float, optional): De maximale tijd (in seconden) om te wachten op een echo.
                                         Voorkomt dat de code blijft hangen bij geen object. Standaard is 1.0s.
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.unit = unit.lower()
        self.timeout_s = timeout_s

        # Controleer of de eenheid geldig is
        if self.unit not in ["cm", "m"]:
            raise ValueError("Ongeldige eenheid. Kies 'cm' of 'm'.")

        # GPIO initialisatie
        GPIO.setmode(GPIO.BCM)  # Gebruik BCM-nummering voor GPIO-pinnen
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

        # Zorg ervoor dat de TRIG-pin laag is bij de start
        GPIO.output(self.trig_pin, GPIO.LOW)
        time.sleep(0.5)  # Geef de sensor even de tijd om te stabiliseren

        print(f"Ultrasonic Sensor initialized: Trig={self.trig_pin}, Echo={self.echo_pin}")

    def _get_raw_pulse_duration(self):
        """
        Interne methode om de duur van de echo-puls te meten.
        Deze methode is 'private' (door de underscore) omdat deze intern door de klasse wordt gebruikt.
        """
        # Stuur een korte puls op de TRIG-pin
        GPIO.output(self.trig_pin, GPIO.HIGH)
        time.sleep(0.00001)  # 10 microseconden puls
        GPIO.output(self.trig_pin, GPIO.LOW)

        pulse_start_time = time.time()
        pulse_end_time = time.time()

        # Wacht tot de ECHO-pin HOOG wordt (start van de puls)
        timeout_start = time.time()
        while GPIO.input(self.echo_pin) == GPIO.LOW:
            pulse_start_time = time.time()
            if time.time() - timeout_start > self.timeout_s:
                raise RuntimeError("Echo timeout: Geen echo ontvangen (sensor te ver of geen object).")

        # Wacht tot de ECHO-pin LAAG wordt (einde van de puls)
        timeout_start = time.time()
        while GPIO.input(self.echo_pin) == GPIO.HIGH:
            pulse_end_time = time.time()
            if time.time() - timeout_start > self.timeout_s:
                raise RuntimeError("Echo timeout: Echo bleef te lang hoog.")

        pulse_duration = pulse_end_time - pulse_start_time
        return pulse_duration

    def get_distance(self):
        """
        Meet de afstand tot een object met behulp van de ultrasone sensor.

        Returns:
            float: De gemeten afstand in de opgegeven eenheid (cm of m).
            Geeft None terug bij een fout (bijv. timeout) of als de meting buiten bereik is.
        """
        try:
            pulse_duration = self._get_raw_pulse_duration()

            # Afstand = (duur van de puls * snelheid van geluid) / 2
            # Deel door 2 omdat het geluid heen en weer reist
            distance_cm = (pulse_duration * self.SPEED_OF_SOUND_CM_PER_S) / 2

            if self.unit == "m":
                return distance_cm / 100.0  # Converteer naar meters
            else:
                return round(distance_cm, 2) # Rond af op 2 decimalen voor cm

        except RuntimeError as e:
            # Vang specifieke fouten van _get_raw_pulse_duration op
            print(f"Sensor Error: {e}")
            return None
        except Exception as e:
            # Vang andere onverwachte fouten op
            print(f"An unexpected error occurred: {e}")
            return None

    def __del__(self):
        """
        Opruim-methode die wordt aangeroepen wanneer het object wordt vernietigd.
        Zorgt ervoor dat de GPIO-pinnen correct worden vrijgegeven.
        """
        print(f"Cleaning up GPIO for sensor on Trig={self.trig_pin}, Echo={self.echo_pin}")
        GPIO.cleanup() # Dit zal alle GPIO-pinnen opruimen die zijn ingesteld.
                       # Overweeg GPIO.cleanup(self.trig_pin) en GPIO.cleanup(self.echo_pin)
                       # als je meerdere sensoren hebt die doorgaan.

