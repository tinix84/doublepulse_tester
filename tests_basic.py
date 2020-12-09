import helpers_plot
from helpers_plot import DoublePulseViewerPlotly, plot_switching_energy_map, plot_single_switching_energy_map

import ltspice_dpt
from ltspice_dpt import calc_sw_losses_ltspice, import_ltspice_log

from PyLTSpice.LTSpice_RawRead import LTSpiceRawRead

import pandas as pd



def test_extract_switching_losses_from_wfm(filename_sim, ton=30e-6, toff=40e-6):

    # viewer = DoublePulseViewerBokeh()
    viewer = DoublePulseViewerPlotly()

    LTR = LTSpiceRawRead(filename_sim)
    # print(LTR.get_trace_names())
    # print(LTR.get_raw_property())
    steps = LTR.get_steps()

    time = LTR.get_trace("time")  # Zero is always the X axis
    v_QLS = LTR.get_trace("V(d_ls)")
    i_QLS = LTR.get_trace("Ix(u4:DRAININ)")

    switching_energy_lut = pd.DataFrame(columns=['step', 'current', 'voltage', 'eon', 'eoff'])
    for step in range(len(steps)):

        Eon, Eoff = calc_sw_losses_ltspice(time=time.get_wave(step), vds=v_QLS.get_wave(step), id=i_QLS.get_wave(step), ton=ton, toff=toff)
        
        step_label = ''.join(['{0}={1} '.format(k, v) for k, v in LTR.steps[step].items()])
        print(f"Step {step_label} Eon={Eon}, Eoff={Eoff}")

        switching_energy_lut = switching_energy_lut.append({'step': step,
                                                            'current': LTR.steps[step].get('idc'), 'voltage': LTR.steps[step].get('vdc'),
                                                            'eon': Eon, 'eoff': Eoff},
                                                            ignore_index=True)

        viewer.add_time_wfm(time=time.get_wave(step), vds=v_QLS.get_wave(step), id=i_QLS.get_wave(step), label=step_label)

    switching_energy_lut.to_csv("./Eloss_DoublePulseTester_EPC8009_sync.csv")

    plot_single_switching_energy_map(switching_energy_lut)


def test_extract_switching_losses_from_log_file(filename_sim):
    swithing_energy_LUT = import_ltspice_log(filename_sim)
    plot_single_switching_energy_map(swithing_energy_LUT)


if __name__ == "__main__":
    import os

    abs_dirname = os.path.dirname(os.path.abspath(__file__))
    # test_extract_switching_losses_from_log_file(abs_dirname+ "/LTSpice/DoublePulseTester_EPC8009_sync.log")
    test_extract_switching_losses_from_wfm(abs_dirname+ "/LTSpice/DoublePulseTester_EPC8009_sync.raw")
