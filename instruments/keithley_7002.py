import json
import pyvisa

class KeithleyController:

    def __init__(self,resource_address):

        self.address = resource_address
        self.rm = pyvisa.ResourceManager()
        self.sm = None

    def connect(self):
        """Attempts to connect to instrument"""
        try:
            self.sm = self.rm.open_resource(self.address)
            self.sm.write('*RST')
            return True
        except pyvisa.VisaIOError as e:
            print(f"Connection failed: {e}")
            return False

    def switch_to_device(self, config_name, device_name,map_path = 'C:/Users/Bluefors/Documents/M81_SSM_rev1/config/wiring_map.json'):

            with open(map_path,'r') as file:
                wiring = json.load(file)
            self.sm.write(':ROUT:OPEN All')

            dev_hi = wiring[config_name][device_name]["Hi"]
            dev_lo = wiring[config_name][device_name]["Lo"]

            self.sm.write(f':CLOS (@ {dev_hi})')
            self.sm.write(f':CLOS (@ {dev_lo})')

            print(f"Connected {device_name} using {config_name}")

            pass

    def connection_test(self, config_name,map_path = 'C:/Users/Bluefors/Documents/M81_SSM_rev1/config/wiring_map.json'):
        """Steps through each device in a configuration for manual pinout verification."""
        with open(map_path, 'r') as file:
            wiring = json.load(file)

        if config_name not in wiring:
            print(f"Error: {config_name} not found in wiring map.")
            return

        print(f"\n--- Starting Pinout Verification for {config_name} ---")

        # Loop through each device in the chosen configuration
        for device_name, channels in wiring[config_name].items():
            # Open all relays first for safety
            self.sm.write(':ROUT:OPEN ALL')

            # Extract relays (handles both lists and single strings)
            hi_relays = channels["Hi"]
            lo_relays = channels["Lo"]

            if isinstance(hi_relays, list):
                hi_relays = ",".join(hi_relays)
            if isinstance(lo_relays, list):
                lo_relays = ",".join(lo_relays)

            # Close the specific relays
            self.sm.write(f':CLOS (@ {hi_relays})')
            self.sm.write(f':CLOS (@ {lo_relays})')

            print(f"\nActive: {device_name}")
            print(f"Closed Hi: {hi_relays} | Closed Lo: {lo_relays}")

            # Pause the script until the user presses Enter
            input("Press Enter to step to the next device (or Ctrl+C to abort)...")

        # Clean up at the end of the test
        self.sm.write(':ROUT:OPEN ALL')
        print("\n--- Connection test complete. All relays opened. ---")