"""
This file contains codeflow suggestion for how the codeflow would work in
the project.
This is the newest version of the file. 
"""

import plant_modules # All functions that are being used
import CoT # Communication module with Circus of Things
import serial_messages # Function for Serial monitor / Console 
import json
from datetime import datetime
import time


# ----------------------------------------------------------------------------------------------------------------------

# First time python is run (If a reboot happens)
plant_dictionary = plant_modules.plant_setup()


while True:
    """
    Main loop of the system
    """
    # Checks the signals from Circus of Things, to see if user wants to save new configuration or update CoT with chosen plant configuration. 
    new_plant = CoT.new_plant_configuration_key2.get()['Value']
    save_configuration = CoT.save_configuration_key2.get()['Value']

    # Whenever user wants to update Circus of Things (IoT) with configuration value for a chosen plant
    # (or a new configuration will be created if the plant doesn't exist in json file)
    if (new_plant == 1):
        plant_dictionary = plant_modules.plant_setup()

    # Will be true if user wants to save new configuration for a chosen plant. 
    if (save_configuration == 1):
        plant_number = str(CoT.plant_number_key2.get()['Value'])
        plant_modules.plant_configuration(plant_number, plant_dictionary[plant_number])

    #### Sensor Values  ####-------------------------------------------------------------------------------------------------
    for plant_name in range(1, 9):

        if plant_dictionary[str(plant_name)]['active_status']: # Only run if plant is active

            #### Update sensor values ####------------------------------------------------------------------------------

            plant_dictionary = plant_modules.update_plant_sensor_values_v2(plant_dictionary, plant_name)
            plant_dictionary = plant_modules.update_plant_system_states(plant_dictionary, plant_name)

            #### Check sensors ####-------------------------------------------------------------------------------------

            plant_dictionary = plant_modules.soil_check(plant_dictionary, plant_name)
            plant_dictionary = plant_modules.lux_check(plant_dictionary, plant_name)
            plant_dictionary = plant_modules.checking_temperature(plant_dictionary, plant_name)
            plant_dictionary = plant_modules.checking_humidity(plant_dictionary, plant_name)
            plant_dictionary = plant_modules.checking_water_tank_volume(plant_dictionary, plant_name)

            #### Put updated states to CoT ####-------------------------------------------------------------------------

            plant_dictionary = plant_modules.put_system_states_to_CoT(plant_dictionary, plant_name)

        else:
            continue


    #### Serial monitor ####--------------------------------------------------------------------------------------------
    print('##########################################################')
    print('PLANT STATUSES:                           CLOCK:', datetime.fromtimestamp(int(time.time())).strftime('%H:%M:%S'))
    for plant_name in range(1, 9):
        if plant_dictionary[str(plant_name)]['active_status']:
            print('\n  Plant', str(plant_name) +':     ', serial_messages.plant_checktime_left(str(plant_name)))
            print('  Soil:', int(plant_dictionary[str(plant_name)]['soil_value']), '     Threshold:', int(plant_dictionary[str(plant_name)]['soil_requirement']))
            print('  Pump:', plant_dictionary[str(plant_name)]['pump_state'], '      Last given water:', datetime.fromtimestamp(plant_dictionary[str(plant_name)]['last_water']).strftime('%H:%M:%S %d/%m-%Y'))

            print('\n  Lux:', int(plant_dictionary[str(plant_name)]['lux_value']), '   Threshold:', int(plant_dictionary[str(plant_name)]['lux_requirement']))
            print('  Light:', plant_dictionary[str(plant_name)]['light_state'])

        else:
            continue

    print('##########################################################')

    # Store the dictionary with every plant configuration to the json file. 
    with open('plant_dictionaries_v2.json', 'w') as json_file:
        json.dump(plant_dictionary, json_file)

    #time.sleep(1) # To slow down communication with CoT
