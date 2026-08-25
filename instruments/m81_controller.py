import numpy as np
import time
from lakeshore import SSMSystem
class M81Controller:

    def __init__(self):
        self.my_ssm = None

    def connect(self):
        try:
            self.my_ssm = SSMSystem()
            self.s1_bcs = self.my_ssm.get_source_module(1)
            self.s1_vm = self.my_ssm.get_measure_module(1)
            self.s1_bcs.disable()
        finally :
            print("M81 SSM and Modules Connected.")

    def disconnect(self):

        if hasattr(self,'my_ssm') and self.my_ssm is not None:
            self.my_ssm.disconnect_usb()
            print("Successfully disconnected from the M81-SSM.")
    def run_iv_sweep(self, i_max, step_size, nplc):

        self.s1_bcs.set_readback_nplcycles(nplc)

        current_array = np.arange(-i_max,i_max + step_size, step_size)
        total_points = len(current_array)

        print(f"Starting sweep: {total_points} points at {nplc} NPLC. Imax: {i_max} A")

        #self.my_ssm._usb_command('SOUR1:SWE:CENT 0')
        #self.my_ssm._usb_command(f'SOUR1:SWE:SPAN {2 * i_max}')
        #self.my_ssm._usb_command(f'SOUR1:SWE:POIN {total_points}')
        #self.my_ssm._usb_command('SOUR:SWE:MODE LIN')

        #self.my_ssm._usb_command('SOUR1:SWE:STAT ON')
        #self.my_ssm._usb_command('INIT:SWE')
        sweep_config = SSMSystem.SourceSweepSettings(
            sweep_type= self.my_ssm.SourceSweepType.CURRENT_AMPLITUDE,start=-i_max,stop=i_max,points=total_points,
            dwell=0.01, direction=self.my_ssm.SourceSweepSettings.Direction.UP, round_trip=True)
        self.s1_bcs.set_sweep_configuration(sweep_config)
        self.s1_bcs.enable()
        stream_data = self.my_ssm.get_data(total_points, total_points,[self.my_ssm.DataSourceMnemonic.SOURCE_AMPLITUDE, 1],
                                           [self.my_ssm.DataSourceMnemonic.MEASURE_DC, 1])


        print("Sweep running...")



        raw_currents, raw_voltages = zip(*stream_data)
        currents = np.array(raw_currents)
        voltages = np.array(raw_voltages)

        return currents, voltages


