from data_analysis import xmm

# initial parameters
object_name = "A1589"
obs_id = "0149900301"
odf_path = "/Users/kym/PycharmProjects/astrostat/data/A1589/0149900301/ODF"

obs1 = xmm.Observation(object_name, obs_id, odf_path)
obs1.get_info()

def initialise_new_data():
    obs1.cifbuild()
    obs1.odfingest()
    obs1.chain()
    obs1.set_folders()
    obs1.copy_events()
    obs1.epic_filter()

    obs1.find_excluded_ccds()  # not automatic yet
    obs1.set_prefixes()  # not automatic yet
    obs1.cheese()
    obs1.set_detx_dety()

def initialise_existing_data():
    obs1.find_excluded_ccds()  # not automatic yet
    obs1.set_prefixes()
    obs1.set_detx_dety()

def radial_profile(radius_list, mos1=True, mos2=True, pn=True, mask=1, with_image=False):
    annulus_list = [(int(radius_list[i]), int(radius_list(i+1))) for i in range(len(radius_list)-1)]
    for annulus in annulus_list:
        inner_radius = annulus[0]
        outer_radius = annulus[1]
        obs1.create_region_file(inner_radius=inner_radius, outer_radius=outer_radius)
        name = "{}-{}".format(inner_radius, outer_radius)

        if mos1:
            mos1_region = "reg1-{}-{}.txt".format(inner_radius, outer_radius)
            obs1.mos1_spectra(region_file=mos1_region, mask=mask, with_image=with_image)
            obs1.rename_spectra_output(inner_radius=inner_radius, outer_radius=outer_radius, mos1=True, mos2=False, pn=False)
            obs1.grppha_mos1(name=name)

        if mos2:
            mos2_region = "reg2-{}-{}.txt".format(inner_radius, outer_radius)
            obs1.mos2_spectra(region_file=mos2_region, mask=1, with_image=False)
            obs1.rename_spectra_output(inner_radius=inner_radius, outer_radius=outer_radius, mos1=False, mos2=True, pn=False)
            obs1.grppha_mos2(name=name)

        if pn:
            pn_region = "reg3-{}-{}.txt".format(inner_radius, outer_radius)
            obs1.pn_spectra(region_file=pn_region, mask=1, with_image=False)
            obs1.rename_spectra_output(inner_radius=inner_radius, outer_radius=outer_radius, mos1=False, mos2=False, pn=True)
            obs1.grppha_pn(name=name)

        if with_image:
            obs1.comb_image(mask=mask, mos1=mos1, mos2=mos2, pn=pn)


obs1.cifbuild()
obs1.odfingest()
obs1.chain()
obs1.set_folders()
obs1.copy_events()
obs1.epic_filter()

obs1.find_excluded_ccds() # not automatic yet
obs1.set_prefixes() # not automatic yet
#obs1.cheese()
#obs1.mos1_spectra()
#obs1.mos2_spectra()
#obs1.pn_spectra()
#obs1.comb_image(mask=0, mos1=True, mos2=True, pn=True)

obs1.set_detx_dety() # not automatic yet

inner_radius=0
outer_radius=60
obs1.create_region_file(inner_radius=inner_radius, outer_radius=outer_radius)

mos1_region = "reg1-{}-{}.txt".format(inner_radius, outer_radius)
mos2_region = "reg2-{}-{}.txt".format(inner_radius, outer_radius)
pn_region = "reg3-{}-{}.txt".format(inner_radius, outer_radius)

#obs1.mos1_spectra(region_file=mos1_region, mask=1, with_image=False)
obs1.mos2_spectra(region_file=mos2_region, mask=1, with_image=False)
#obs1.pn_spectra(region_file=pn_region, mask=1, with_image=False)
#obs1.comb_image(mask=1)
obs1.rename_spectra_output(inner_radius=inner_radius, outer_radius=outer_radius, mos1=False, mos2=True, pn=False)

name="{}-{}".format(inner_radius, outer_radius)
#obs1.grppha_mos1(name=name)
obs1.grppha_mos2(name=name)
#obs1.grppha_pn(name=name)
