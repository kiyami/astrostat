from data_analysis.xmm2 import Threads

A1835_info = {
    "object_name": "A1835",
    "obs_id": "0551830101",
    "odf_path": "/Users/kym/PycharmProjects/astrostat/data/A1835/0551830101/ODF",
    "ccf_path": "/Users/kym/Desktop/software/ccf/",
    "mos1_prefix": "1S001",
    "mos2_prefix": "2S002",
    "pn_prefix": "S003",
    "mos1_ccds": (1, 1, 1, 0, 1, 0, 1),
    "mos2_ccds": (1, 1, 1, 1, 0, 1, 1),
    "pn_ccds": (1, 1, 1, 1),
    "mos1_detx": 160.36793,
    "mos1_dety": -217.38445,
    "mos2_detx": 39.185507,
    "mos2_dety": -81.309178,
    "pn_detx": 141.5,
    "pn_dety": -94.417516
}

A1589_info = {
    "object_name": "A1589",
    "obs_id": "0149900301",
    "odf_path": "/Users/kym/PycharmProjects/astrostat/data/A1589/0149900301/ODF",
    "ccf_path": "/Users/kym/Desktop/software/ccf/",
    "mos1_prefix": "1S001",
    "mos2_prefix": "2S002",
    "pn_prefix": "S003",
    "mos1_ccds": (1, 1, 1, 1, 1, 1, 1),
    "mos2_ccds": (1, 1, 1, 1, 1, 1, 1),
    "pn_ccds": (1, 1, 1, 1),
    "mos1_detx": 206.5,
    "mos1_dety": -79.4,
    "mos2_detx": 95.3,
    "mos2_dety": -126.0,
    "pn_detx": 228.6,
    "pn_dety": -40.6
}

# create observation object
info = A1589_info
obs = Threads.initialize_obs(info)

# initial definitions for new data
#Threads.initialise_new_data(obs)

# initial definitions for existing data
Threads.initialise_existing_data(obs)

# prefix and ccd definitions
Threads.set_prefixes_and_ccds(obs, info)

# point source detection
Threads.cheese(obs, scale=0.5, rate=1.0, dist=40, clobber=False)

# set detector coordinates
Threads.set_detx_dety(obs, info)

# create region file
inner_radius, outer_radius = 0, 60
mos1_region, mos2_region, pn_region = Threads.create_region_file(obs, inner_radius, outer_radius)
print(mos1_region, mos2_region, pn_region)

# mos1 spectrum
Threads.mos1_spectra(obs, region_file=mos1_region.name, mask=1)
Threads.mos2_spectra(obs, region_file=mos2_region.name, mask=1)
Threads.pn_spectra(obs, region_file=pn_region.name, mask=1)

# rename spectrum
Threads.rename_mos1_spectra_output(obs, inner_radius, outer_radius)
Threads.rename_mos2_spectra_output(obs, inner_radius, outer_radius)
Threads.rename_pn_spectra_output(obs, inner_radius, outer_radius)

# group spectrum
bin_value = 30
Threads.grppha_mos1(obs, inner_radius, outer_radius, bin_value=bin_value)
Threads.grppha_mos2(obs, inner_radius, outer_radius, bin_value=bin_value)
Threads.grppha_pn(obs, inner_radius, outer_radius, bin_value=bin_value)

# proton scale
mos1_area = Threads.proton_scale_mos1(obs, inner_radius, outer_radius)
mos2_area = Threads.proton_scale_mos2(obs, inner_radius, outer_radius)
pn_area = Threads.proton_scale_pn(obs, inner_radius, outer_radius)
