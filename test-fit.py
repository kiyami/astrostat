from data_analysis import fitting

kwargs = {"spectrum_files": {"mos1": "mos1S001-obj-0-60-grp.pi",
                             "mos2": "mos2S002-obj-0-60-grp.pi",
                             "pn": "pnS003-obj-0-60-grp.pi",
                             "rass": "rass-grp.pi"},
          "path": "/Users/kym/PycharmProjects/astrostat/data/A2667/0148990101/epic",
          "nh": "0.02",
          "redshift": "0.0871",
          "statistic": "chi",
          "abs_model": "phabs",
          "src_model": "apec"}

def fit_spectrum(kwargs):
    spec = fitting.Spectrum(**kwargs)
    print(spec)
    spec.check_diag_files()

    spec.deneme()

    #spec.set_fit_parameters()
    #spec.fit()

fit_spectrum(kwargs)

