from data_analysis import xmm
import os
object_name = "A1589"
obs_id = "0149900301"
odf_path = "/Users/kym/PycharmProjects/astrostat/data/A1589/0149900301/ODF"

obs1 = xmm.Observation(object_name, obs_id, odf_path)

obs1.get_info()
obs1.cifbuild()
obs1.odfingest()
obs1.chain()
obs1.set_folders()
obs1.copy_events()
obs1.epic_filter()
obs1.find_excluded_ccds()
obs1.set_prefixes()
#obs1.cheese()
#obs1.mos1_spectra()
#obs1.mos2_spectra()
#obs1.pn_spectra()
#obs1.comb_image(mask=0, mos1=True, mos2=True, pn=True)

obs1.set_detx_dety()
obs1.create_region_file(inner_radius=15, outer_radius=20)

mos1_region = "reg1-15-20.txt"
mos2_region = "reg2-15-20.txt"
pn_region = "reg3-15-20.txt"

obs1.mos1_spectra(region_file=mos1_region)
obs1.mos2_spectra(region_file=mos2_region)
obs1.pn_spectra(region_file=pn_region)
obs1.comb_image(mask=1)
obs1.rename_spectra_output()
