import numpy as np
from instruments.keithley_7002 import KeithleyController
from instruments.m81_controller import M81Controller
import csv
from datetime import datetime
from pathlib import Path

print("--- Starting Normal Resistance (Rn) Measurements ---")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
data_dir = Path("data") / f"Rn_Sweep_{timestamp}"
data_dir.mkdir(parents=True, exist_ok=True)




sm = KeithleyController('GPIB0::7::INSTR')
smu = M81Controller()

sm.connect()
smu.connect()

i_max = 5e-6
step_size = 5e-7
nplc = 1

try:
    for i in range(22):
        num = 1+i
        sm.switch_to_device("Config_2W", f"Device_{num}")

        currents, voltages = smu.run_iv_sweep(i_max, step_size, nplc)
        resistances = voltages/currents
        slope = np.mean(resistances)
        csv_file_path = data_dir / f"Rn_results_Device_{num}.csv"
        print(f"Logging data to: {csv_file_path}")
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Current","Voltage","Resistance"])

            for j in range(len(currents)):
                resistance = voltages[i]/currents[i]
                writer.writerow([currents[j],voltages[j],resistance])
                csv_file.flush()



        #slope, intercept = np.polyfit(currents, voltages, 1)



        print(f"Device_{num} Rn: {slope:.2f} Ohms")

except Exception as e:

    print(f"\n[!] WARNING: Measurement failed or was interrupted!")
    print(f"Error Details: {e}")

finally:

    print("\n--- Safely shutting down instruments ---")

    try:
        sm.sm.write(':ROUT:OPEN ALL')
    except Exception:
        print("Could not communicate with Keithley to open relays.")

        # Safely release the ports
    #sm.disconnect()
    smu.disconnect()
    print("Ports released. Safe to exit.")
