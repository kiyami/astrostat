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
obs1.cheese()
