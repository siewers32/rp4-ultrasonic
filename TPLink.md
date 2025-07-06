Om je Raspberry Pi met BlueZ en de TP-Link UB500 via BLE MIDI (Bluetooth Low Energy MIDI) te adverteren, zodat deze zichtbaar wordt in MIDI Studio op je Mac, moet je de Raspberry Pi configureren als een BLE MIDI-peripheral. Dit omvat het correct instellen van BlueZ en het gebruik van een BLE MIDI-advertentieservice.

Hier zijn de stappen en configuratieaanpassingen:

**Voorbereiding (Eerste keer of als je problemen hebt):**

1.  **Zorg voor de juiste BlueZ-versie:**
      * BlueZ 5.43 of nieuwer is vereist voor de meeste BLE MIDI-functionaliteit.
      * Zoals eerder vermeld, **moet BlueZ gecompileerd zijn met de `--enable-midi` optie.** Als je Raspberry Pi OS (voorheen Raspbian) gebruikt, is dit vaak al het geval, maar het is cruciaal om dit te controleren. Als je BlueZ handmatig hebt geïnstalleerd, zorg dan dat deze optie is aangevinkt. Zie mijn vorige antwoord voor instructies over het compileren van BlueZ.
2.  **TP-Link UB500 firmware en driver:**
      * Controleer of de UB500 correct wordt herkend. Gebruik `lsusb` om te zien of de adapter wordt gedetecteerd.
      * De Realtek RTL8761BU chipset (gebruikt in de UB500) heeft firmware nodig. Zorg dat de firmwarebestanden (`rtl8761bu_fw.bin` en `rtl8761bu_config.bin`) aanwezig zijn in `/lib/firmware/rtl_bt/`. Zo niet, installeer dan het `linux-firmware` pakket of haal ze handmatig op.
3.  **BlueZ service status:**
      * Zorg ervoor dat de Bluetooth-service actief is: `sudo systemctl status bluetooth`. Zo niet, start en enable deze dan: `sudo systemctl start bluetooth` en `sudo systemctl enable bluetooth`.
4.  **Verwijder eventuele interne Bluetooth-adapters:**
      * Als je Raspberry Pi een ingebouwde Bluetooth-adapter heeft (zoals de Pi 3B+, Pi 4), is het raadzaam deze uit te schakelen om conflicten te voorkomen. Dit kan via `sudo btmgmt --index 0 power off` (vervang 0 door de index van de interne adapter, te vinden met `sudo btmgmt info`) of door het uitschakelen in `config.txt` (voor Pi 3B/3B+ en 4):
          * Open `sudo nano /boot/config.txt`
          * Voeg toe of uncomment: `dtoverlay=disable-bt`
          * Reboot de Pi.

**Stappen om de Raspberry Pi te adverteren als BLE MIDI-apparaat:**

Het belangrijkste onderdeel hiervoor is het gebruik van `btmidi-server` of een vergelijkbare tool die BLE MIDI-advertenties kan afhandelen. BlueZ zelf regelt de laag-niveau communicatie, maar een applicatie is nodig om de MIDI-dienst te adverteren.

**Methode 1: Met `btmidi-server` (aanbevolen en meest directe)**

Als BlueZ is gecompileerd met `--enable-midi`, dan is `btmidi-server` de tool die je nodig hebt.

1.  **Start `btmidi-server`:**
    Open een terminal op je Raspberry Pi en voer het volgende commando uit:

    ```bash
    sudo btmidi-server -v -n "RaspberryPi MIDI"
    ```

      * `-v`: Verbose output, handig voor debugging.
      * `-n "RaspberryPi MIDI"`: Dit stelt de naam in waaronder je Raspberry Pi zal adverteren. Deze naam zal verschijnen in MIDI Studio op je Mac. Kies een duidelijke en herkenbare naam.

    Wanneer `btmidi-server` start, zal het het volgende doen:

      * Het probeert de TP-Link UB500 (of de standaard Bluetooth-adapter) te gebruiken.
      * Het registreert de BLE MIDI-service (UUID `03B80E5A-EDE8-4B33-A751-6CE34EC4C700`) bij BlueZ.
      * Het begint met adverteren.

2.  **Controleer op je Mac (MIDI Studio):**

      * Ga op je Mac naar `Programma's` -\> `Hulpprogramma's` -\> `Audio/MIDI-configuratie`.
      * Klik in de menubalk op `Venster` -\> `Toon MIDI Studio`.
      * Dubbelklik op het `Bluetooth`-pictogram.
      * Als alles goed is, zou je "RaspberryPi MIDI" (of de naam die je hebt ingesteld) moeten zien verschijnen in de lijst met detecteerbare apparaten.
      * Klik op de knop "Verbind" naast de naam van je Raspberry Pi.

3.  **Connectie en ALSA MIDI:**

      * Zodra de verbinding tot stand is gebracht, zal `btmidi-server` een ALSA MIDI-poort aanmaken op je Raspberry Pi. Je kunt dit controleren met:
        ```bash
        aconnect -l
        ```
        Je zult een client en poort zien die overeenkomt met de verbinding (bijvoorbeeld "RaspberryPi MIDI" als client).
      * Vanaf dat moment kun je MIDI-gegevens heen en weer sturen tussen je Mac en de ALSA MIDI-poort op de Raspberry Pi.

**Methode 2: Handmatig adverteren met `bluetoothctl` en `gatttool` (complexer, voor debugging/specifieke gevallen)**

Deze methode is geavanceerder en minder gebruiksvriendelijk dan `btmidi-server`, maar kan nuttig zijn om te begrijpen wat er achter de schermen gebeurt of voor specifieke debugging. **Gebruik deze alleen als `btmidi-server` niet werkt.**

1.  **Zorg dat BlueZ draait en de adapter actief is:**

    ```bash
    sudo systemctl start bluetooth
    sudo btmgmt --index 0 power on # Controleer de index van je UB500 met btmgmt info
    ```

2.  **Registreer de BLE MIDI-service UUID en karakteristiek:**
    Dit is waar het ingewikkeld wordt. Je moet de MIDI-service (UUID `03B80E5A-EDE8-4B33-A751-6CE34EC4C700`) en de MIDI-data karakteristiek registreren bij BlueZ. Dit vereist vaak een applicatie die de GATT-server functionaliteit van BlueZ gebruikt. `btmidi-server` doet dit automatisch.

3.  **Start BLE-advertenties:**
    Je kunt met `bluetoothctl` de advertenties starten, maar de *inhoud* van de advertentie moet de MIDI-service UUID bevatten.

    ```bash
    bluetoothctl
    # power on
    # advertise on
    # register-service 03B80E5A-EDE8-4B33-A751-6CE34EC4C700
    # Dit is NIET voldoende voor een complete BLE MIDI advertentie.
    ```

    Dit laat zien waarom `btmidi-server` zo handig is: het implementeert de volledige BLE MIDI-specificatie (inclusief de juiste service en karakteristieken) die nodig is om zichtbaar te zijn in MIDI Studio.

**Belangrijke overwegingen en troubleshooting:**

  * **Firewall:** Zorg ervoor dat je firewall (bijv. `ufw`) geen Bluetooth-verbindingen blokkeert. Standaard zou dit geen probleem moeten zijn voor lokale verbindingen, maar controleer het.
  * **Andere Bluetooth-verbindingen:** Zorg ervoor dat er geen andere apparaten zijn die al verbinding proberen te maken met de Raspberry Pi via Bluetooth, of dat de Pi niet al verbonden is met iets anders dat de BLE MIDI-functionaliteit blokkeert.
  * **"Powered Off" in MIDI Studio:** Als je de Raspberry Pi ziet, maar deze als "Powered Off" wordt weergegeven, controleer dan nogmaals of `btmidi-server` draait en of de Bluetooth-adapter van de Pi actief is.
  * **Kernel modules:** Zorg ervoor dat de benodigde kernelmodules zijn geladen: `lsmod | grep bluetooth`, `lsmod | grep hci_uart`.
  * **Debuggen `btmidi-server`:** Als `btmidi-server` problemen geeft, start het dan met `sudo btmidi-server -d -v`. Dit geeft nog meer debugging-informatie.
  * **MAC-adres:** Soms helpt het om de Bluetooth-cache op de Mac te resetten of om de Raspberry Pi een vast Bluetooth MAC-adres te geven, hoewel dit zelden nodig is voor advertenties.
  * **Afstand:** Houd de Raspberry Pi en de Mac binnen een redelijke afstand voor een stabiele Bluetooth-verbinding.
  * **Herstarten:** Na elke belangrijke wijziging (vooral aan BlueZ-configuratie, kernel modules of firmware) is een herstart van de Raspberry Pi vaak de beste eerste stap.

Door de `btmidi-server` te gebruiken met een duidelijke naam, wordt de Raspberry Pi effectief een advertentie van een BLE MIDI-apparaat, waardoor je Mac deze kan detecteren en verbinding kan maken via MIDI Studio.
