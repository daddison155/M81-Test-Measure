from instruments.keithley_7002 import KeithleyController

sm = KeithleyController('GPIB0::7::INSTR')

if sm.connect():
    print('Ready to route signals.')
else:
    print('Check GPID cables or instrument power.')

sm.connection_test('Config_2W')


