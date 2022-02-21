import random

from rcplant import *  # using the pip package


def is_PVC(spectrum):  # PVC method is correct
    decision = False
    if 1250 < spectrum.idxmax() < 1275:
        decision = True
    return decision


def is_PS(spectrum):  # PS method is correct
    decision = False
    if 1400 < spectrum.idxmax() < 1500:
        decision = True
    return decision


def is_PP_HPDE_LDPE(spectrum):
    decision = False
    if 2850 < spectrum.idxmax() < 2950:
        decision = True
    return decision


def is_PC_PU_PET_Polyester(spectrum):  # one PC max occurs at 1250, others are around 1700 - 1800
    decision = False
    if 1700 < spectrum.idxmax() < 1800 or spectrum.idxmax() == 1250:
        decision = True
    return decision


def is_PU(spectrum): # PU method succeed
    decision = False
    spectrum_zoomin = spectrum.loc[1575:1500]
    spectrum_zoomin_1 = spectrum.loc[3500:3050]
    if 3300 < spectrum_zoomin_1.idxmax() < 3400:
        if 1500 < spectrum_zoomin.idxmax() < 1575:  # wavenumber of second max transmittance
            if spectrum_zoomin.max() > 0.010:
                decision = True
    return decision

def is_PC(spectrum): # PC_method scuueed but still need to improve
    decision = False
    spectrum_zoomin_2 = spectrum.loc[1550:1450]
    spectrum_zoomin_3 = spectrum.loc[1275:1250]
    if spectrum_zoomin_2.idxmax() < 1550:
        if spectrum_zoomin_2.max() > 0.09:
            if 0.08 < spectrum_zoomin_3.max() < 0.3: # based on maximum number condition
                decision = True
    return decision

def is_Polyester(spectrum):
    decision = False

    spectrum_zoomin = spectrum.loc[3000:2750]
    spectrum_zoomin_2 = spectrum.loc[2500:1750]
    spectrum_zoomin_3 = spectrum.loc[3000:2500]
    spectrum_zoomin_4 = spectrum.loc[2000:1500]
    if spectrum_zoomin.idxmax() > 2850:  # wavenumber of second max transmittance
        if spectrum_zoomin.max() > 0.025:
            if spectrum_zoomin_2.idxmax() < 2000:
                if spectrum_zoomin_3.idxmax() > 2750:
                    if 0.02 < spectrum_zoomin_4.max() >0.06:
                        decision = True
    return decision



def is_Pet(spectrum):
    decision = False
    spectrum_zoomin = spectrum.loc[1700:1250]
    if spectrum_zoomin.idxmax() < 1300:  # wavenumber of second max transmittance
        if spectrum_zoomin.max() > 0.08:
            decision = True
    return decision



def user_sorting_function(sensors_output):
    # This sorting function provides a simple example to help you understand how to use
    # the variable sensors_output. You need to figure out more advanced function to achieve
    # a higher sorting accuracy in both 'training' and 'testing' mode

    sensor_id = 1
    spectrum = sensors_output[sensor_id]['spectrum']

    decision = {sensor_id: random.choice(list(Plastic)[0:-1])}
    if spectrum.iloc[0] == 0:  # For FTIR, if the first transmittance is 0, it is blank spectra
        decision = {sensor_id: Plastic.Blank}
    else:
        if is_PVC(spectrum):
            decision = {sensor_id: Plastic.PVC}
        elif is_PS(spectrum):
            decision = {sensor_id: Plastic.PS}
        elif is_PP_HPDE_LDPE(spectrum):
            spectrum_zoomin = spectrum.loc[1550:1250]  # zoom in to check the second max
            if 1350 < spectrum_zoomin.idxmax() < 1450:  # Difference occurs at the second max transmittance
                decision = {sensor_id: Plastic.PP}
            else:
                decision = {sensor_id: random.choice([Plastic.HDPE, Plastic.LDPE])}  # A random guess
        elif is_PC_PU_PET_Polyester(spectrum):  # This part need to be updated
            if is_PU(spectrum):
                decision = {sensor_id: Plastic.PU}
            elif is_PC(spectrum):
                decision = {sensor_id: Plastic.PC}
            elif is_Polyester(spectrum):
                decision = {sensor_id: Plastic.Polyester}
            else:
                is_Pet(spectrum)
                decision = {sensor_id: Plastic.PET}

    return decision


def main():
    # simulation parameters
    conveyor_length = 1000  # cm
    conveyor_width = 100  # cm
    conveyor_speed = 10  # cm per second
    num_containers = 2000
    sensing_zone_location_1 = 500  # cm
    sensors_sampling_frequency = 10  # Hz
    simulation_mode = 'training'

    # Add two lists
    identification_lst = []
    actual_lst = []

    sensors = [
        Sensor.create(SpectrumType.FTIR, sensing_zone_location_1),
    ]

    conveyor = Conveyor.create(conveyor_speed, conveyor_length, conveyor_width)

    simulator = RPSimulation(
        sorting_function=user_sorting_function,
        num_containers=num_containers,
        sensors=sensors,
        sampling_frequency=sensors_sampling_frequency,
        conveyor=conveyor,
        mode=simulation_mode
    )

    elapsed_time = simulator.run()  # added last two arguments
    for item_id, result in simulator.identification_result.items():
        if result['actual_type'] != result['identified_type']:
            print(f"incorrectly identified : {result}")

    print(f'\nResults for running the simulation in "{simulation_mode}" mode:')
    print(f'Total missed containers = {simulator.total_missed}')
    print(f'Total sorted containers = {simulator.total_classified}')
    print(f'Total mistyped containers = {simulator.total_mistyped}')

    print(f'\n{num_containers} containers are processed in {elapsed_time:.2f} seconds')


if __name__ == '__main__':
    main()
