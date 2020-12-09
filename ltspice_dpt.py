# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility
# plotly basics


import numpy as np
import pandas as pd
import re
import scipy.interpolate as interpolate

regex_step = r"^\.step (idc=(.*) vdc=(.*))"
regex_Eoff = r"Measurement: eoff([\s\S]*?)^\n"
regex_Eon = r"Measurement: eon([\s\S]*?)^\n"
regex_energy_loss = r"^\s+(\d+)\s(\S*)\s(\S*)\s(\S*)\s"


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]


def calc_sw_losses_ltspice(time, vds, id, ton=30e-6, toff=40e-6):
    ton_interval = ton*np.array([0.95, +1.05])
    toff_interval = toff*np.array([0.95, +1.05])
    tcond = (ton+toff)/2  # mid of condution interval

    sc_losses = vds*id
    time_cond_idx = find_nearest(time, tcond)[0]
    rdson = sc_losses[time_cond_idx] / id**2

    cond_losses = rdson * id**2
    sw_losses = sc_losses-cond_losses
    sw_losses = sw_losses.clip(min=0)  # remove negative swlosses negative

    time_eon_idx = tuple([(time >= np.min(ton_interval))
                          & (time <= np.max(ton_interval))])
    time_eoff_idx = tuple(
        [(time >= np.min(toff_interval)) & (time <= np.max(toff_interval))])

    Eon = np.trapz(sw_losses[time_eon_idx], x=time[time_eon_idx])
    Eoff = np.trapz(sw_losses[time_eoff_idx], x=time[time_eoff_idx])

    # plt.plot(time, cond_losses, label="cond")
    # plt.plot(time, sw_losses, label="sw")
    # plt.legend() # order a legend.
    # plt.show()

    return Eon, Eoff


def import_ltspice_log(ltspice_filename: str):
    switching_energy = pd.DataFrame(
        columns=['step', 'current', 'voltage', 'eon', 'eoff'])

    fp_sim = open(str(ltspice_filename), "r")
    content = fp_sim.read()

    # matches_step = re.finditer(regex_step, test_str, re.MULTILINE)
    # matches_Eon = re.finditer(regex_Eon, test_str, re.MULTILINE)
    # matches_Eoff = re.finditer(regex_Eoff, test_str, re.MULTILINE)

    steps_list = re.findall(regex_step, content, re.MULTILINE)

    eon_str_block = re.findall(regex_Eon, content, re.MULTILINE)[0]
    eon_list = re.findall(regex_energy_loss, eon_str_block, re.MULTILINE)

    eoff_str_block = re.findall(regex_Eoff, content, re.MULTILINE)[0]
    eoff_list = re.findall(regex_energy_loss, eoff_str_block, re.MULTILINE)

    for step, eon, eoff in zip(steps_list, eon_list, eoff_list):
        switching_energy = switching_energy.append({'step': int(eon[0]), 'current': float(
            step[1]), 'voltage': float(step[2]), 'eon': float(eon[1]), 'eoff': float(eoff[1])}, ignore_index=True)

    return switching_energy








