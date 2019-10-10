from data_analysis import xmm

# A1589
# initial parameters
#object_name = "A1589"
#obs_id = "0149900301"
#odf_path = "/Users/kym/PycharmProjects/astrostat/data/A1589/0149900301/ODF"

# A2667
# initial parameters
object_name = "A2667"
obs_id = "0148990101"
odf_path = "/Users/kym/PycharmProjects/astrostat/data/A2667/0148990101/ODF"

obs1 = xmm.Observation(object_name, obs_id, odf_path)
obs1.get_info()

def initialise_new_data(obs):
    obs.cifbuild()
    obs.odfingest()
    obs.chain()
    obs.set_folders()
    obs.copy_events()
    obs.epic_filter()

    obs.find_excluded_ccds()  # not automatic yet
    obs.set_prefixes()  # not automatic yet
    obs.cheese()
    obs.set_detx_dety()

def initialise_existing_data(obs):
    obs.cifbuild()
    obs.odfingest()
    obs.set_folders()
    obs.find_excluded_ccds()  # not automatic yet
    obs.set_prefixes()
    obs.set_detx_dety()

def radial_profile(obs, radius_list, mos1=True, mos2=True, pn=True, mask=1, bin_value=20, with_image=False):
    annulus_list = [(int(radius_list[i]), int(radius_list[i+1])) for i in range(len(radius_list)-1)]
    for annulus in annulus_list:
        inner_radius = annulus[0]
        outer_radius = annulus[1]
        obs.create_region_file(inner_radius=inner_radius, outer_radius=outer_radius)
        name = "{}-{}".format(inner_radius, outer_radius)

        if mos1:
            mos1_region = "reg1-{}-{}.txt".format(inner_radius, outer_radius)
            obs.mos1_spectra(region_file=mos1_region, mask=mask, with_image=with_image)
            obs.rename_spectra_output(inner_radius=inner_radius, outer_radius=outer_radius, mos1=True, mos2=False, pn=False)
            obs.grppha_mos1(name=name, bin_value=bin_value)

        if mos2:
            mos2_region = "reg2-{}-{}.txt".format(inner_radius, outer_radius)
            obs.mos2_spectra(region_file=mos2_region, mask=mask, with_image=with_image)
            obs.rename_spectra_output(inner_radius=inner_radius, outer_radius=outer_radius, mos1=False, mos2=True, pn=False)
            obs.grppha_mos2(name=name, bin_value=bin_value)

        if pn:
            pn_region = "reg3-{}-{}.txt".format(inner_radius, outer_radius)
            obs.pn_spectra(region_file=pn_region, mask=mask, with_image=with_image)
            obs.rename_spectra_output(inner_radius=inner_radius, outer_radius=outer_radius, mos1=False, mos2=False, pn=True)
            obs.grppha_pn(name=name, bin_value=bin_value)

        if with_image:
            obs.comb_image(mask=mask, mos1=mos1, mos2=mos2, pn=pn)

def rebin_spectra(obs, radius_list, mos1=True, mos2=True, pn=True, bin_value=20):
    annulus_list = [(int(radius_list[i]), int(radius_list[i + 1])) for i in range(len(radius_list) - 1)]
    for annulus in annulus_list:
        inner_radius = annulus[0]
        outer_radius = annulus[1]
        name = "{}-{}".format(inner_radius, outer_radius)

        if mos1:
            obs.grppha_mos1(name=name, bin_value=bin_value)

        if mos2:
             obs.grppha_mos2(name=name, bin_value=bin_value)

        if pn:
             obs.grppha_pn(name=name, bin_value=bin_value)


initialise_existing_data(obs=obs1)

#radius_list = [0, 60, 120, 240, 360, 600]
radius_list = [300, 600]

#bin_value = 50
#radial_profile(obs=obs1, radius_list=radius_list, mos1=True, mos2=True, pn=True, mask=1, bin_value=bin_value, with_image=False)

rebin_radius_list = [300, 600]
rebin_value = 20
rebin_spectra(obs=obs1, radius_list=rebin_radius_list, mos1=True, mos2=True, pn=True, bin_value=rebin_value)
