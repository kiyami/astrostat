from observation import Observation

A1589_info_dict = {
    "object_name": "A1589",
    "obs_id": "0149900301",
    "odf_path": "/Users/kym/PycharmProjects/astrostat/data/A1589/0149900301/ODF",
    "ccf_path": "/Users/kym/Desktop/software/ccf/",
    "mos1_prefix": "1S001",
    "mos2_prefix": "2S002",
    "pn_prefix": "S003",
    "mos1_ccds": (1, 1, 1, 0, 1, 1, 1),
    "mos2_ccds": (1, 1, 1, 1, 1, 1, 1),
    "pn_ccds": (1, 1, 1, 1),
    "ra": "190.32455",
    "dec": "18.5725719"
}

A1589 = Observation(A1589_info_dict)
A1589.set_folders()
A1589.info()
A1589.cifbuild()
A1589.odfingest()
A1589.chain()
#A1589.copy_events()
#A1589.epic_filter()
A1589.convert_coords()
#A1589.cheese()

A1589.create_region(mos1=True, mos2=True, pn=True, ra=None, dec=None, inner_radius=0, outer_radius=300)
A1589.list_regions()

mos1_spectrum_region = A1589.regions["mos1"][0]
mos2_spectrum_region = A1589.regions["mos2"][0]
pn_spectrum_region = A1589.regions["pn"][0]

A1589.mos1_spectrum(region_object=mos1_spectrum_region, mask=1)
A1589.mos2_spectrum(region_object=mos2_spectrum_region, mask=1)
A1589.pn_spectrum(region_object=pn_spectrum_region, mask=1)

A1589.rename_mos1_spectra_output(region_object=mos1_spectrum_region)
A1589.rename_mos2_spectra_output(region_object=mos2_spectrum_region)
A1589.rename_pn_spectra_output(region_object=pn_spectrum_region)

A1589.grppha_mos1(region_object=mos1_spectrum_region, bin_value=30)
A1589.grppha_mos2(region_object=mos2_spectrum_region, bin_value=30)
A1589.grppha_pn(region_object=pn_spectrum_region, bin_value=30)

A1589.proton_scale_mos1(region_object=mos1_spectrum_region)
A1589.proton_scale_mos2(region_object=mos2_spectrum_region)
A1589.proton_scale_pn(region_object=pn_spectrum_region)