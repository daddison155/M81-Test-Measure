import time
import csv
from PyQt6.QtCore import QThread, pyqtSignal
from lakeshore import SSMSystem


class MeasurementWorker(QThread):
    # Signal to send data back to the GUI (Current, DC Voltage, AC Voltage)
    data_ready = pyqtSignal(float, float, float)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, filename, start_i, stop_i, steps):
        super().__init__()
        self.filename = filename
        self.start_i = start_i
        self.stop_i = stop_i
        self.steps = steps
        self.is_running = True

    def run(self):
        m81 = None
        try:
            # 1. Connect to the instrument
            m81 = SSMSystem()

            # (Configure your BCS-10 source and VM-10 measure modules here)

            # 2. Open CSV file in 'append' mode so we write live
            with open(self.filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["DC_Current_A", "DC_Voltage_V", "AC_Voltage_V"])

                # Generate your current sweep array
                current_points = [...]  # Your numpy array or list

                for current in current_points:
                    if not self.is_running:
                        break  # User pressed the Stop button on the GUI

                    # 3. Set the current
                    # m81.source_modules[1].set_dc_amplitude(current)

                    # 4. Wait for the instrument to settle
                    # time.sleep(0.1) 

                    # 5. Synchronous read prevents buffer overflow
                    # Read DC and Lock-in values simultaneously 
                    # v_dc = m81.measure_modules[1].get_dc_voltage()
                    # v_ac = m81.measure_modules[1].get_lock_in_voltage()

                    # Placeholder values for demonstration
                    v_dc, v_ac = 0.0, 0.0

                    # 6. Save to CSV immediately
                    writer.writerow([current, v_dc, v_ac])

                    # 7. Send to GUI for plotting
                    self.data_ready.emit(current, v_dc, v_ac)

        except Exception as e:
            # Catch hardware timeouts, cable disconnects, etc.
            self.error_occurred.emit(f"Measurement Error: {str(e)}")

        finally:
            # 8. THE FAILSAFE: This block ALWAYS runs, even if the code crashes
            if m81 is not None:
                try:
                    print("Safely shutting down hardware...")
                    # ALWAYS turn off the current output to protect the JJ
                    # m81.source_modules[1].disable_output()

                    # Safely close the port/connection
                    m81.disconnect()
                except Exception as disconnect_error:
                    print(f"Failed to cleanly disconnect: {disconnect_error}")

            self.finished.emit()

    def stop(self):
        # Called when the user clicks 'Stop' in the GUI
        self.is_running = False