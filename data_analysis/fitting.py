import xspec
import os
import sys


class Gaussian:
    def __init__(self, component_number, LineE):
        self.component_number = component_number
        self.LineE = [LineE, -0.05, 0, 0, 1e+06, 1e+06]
        self.Sigma = [0.0, -0.05, 0, 0, 10, 20]
        self.norm = [1e-5, -0.01, 0, 0, 1e+24, 1e+24]

    def get_params(self):
        return self.LineE, self.Sigma, self.norm


class Spectrum:

    diag_files = ["mos1-diag.rsp.gz", "mos2-diag.rsp.gz", "pn-diag.rsp.gz"]
    esas_model = "gaussian + gaussian + gaussian + gaussian + gaussian + gaussian + gaussian + constant*constant(gaussian + gaussian + apec + (apec + powerlaw)phabs + apec*phabs)"
    energy_range = {"mos1": "0.0-0.3,11.0-**",
                    "mos2": "0.0-0.3,11.0-**",
                    "pn": "0.0-0.4,11.0-**"}

    def __init__(self, spectrum_files, path, nh="0.0154", redshift="0.233", statistic="chi", abs_model="phabs", src_model="apec"):
        self.spectrum_files = spectrum_files
        self.path = path
        self.nh = nh
        self.redshift = redshift
        self.statistic = statistic
        self.abs_model = abs_model
        self.src_model = src_model

    def __str__(self):
        string = "{}\n" \
                 "{}\n" \
                 "{}\n" \
                 "{}\n" \
                 "{}\n" \
                 "{}\n" \
                 "{}\n".format(self.spectrum_files, self.path, self.nh, self.redshift, self.statistic, self.abs_model, self.src_model)

        return string

    def check_diag_files(self):
        for diag_file in Spectrum.diag_files:
            diag_path = os.path.join(self.path, diag_file)
            if os.path.exists(diag_path):
                print("{} file exist.".format(diag_file))
            else:
                print("{} file doesn't exist.".format(diag_file))
                sys.exit()

    def deneme(self):
        xspec.AllData.clear()
        xspec.Fit.statMethod = str(self.statistic)
        xspec.Fit.query = "yes"

        os.chdir(self.path)

        xspec.AllData("1:1 {} 2:2 {}".format(self.spectrum_files["mos1"], self.spectrum_files["mos2"]))

        self.spec_mos1 = xspec.AllData(1)
        self.spec_mos1.ignore(self.energy_range["mos1"])

        self.spec_mos2 = xspec.AllData(2)
        self.spec_mos2.ignore(self.energy_range["mos2"])

        xspec.AllModels += "apec+pow"

        self.m1 = xspec.AllModels(1)
        self.m2 = xspec.AllModels(2)

        xspec.AllModels.show()
        #xspec.AllData.nSpectra
        #xspec.Fit.perform()

    def set_fit_parameters(self):
        xspec.AllData.clear()
        xspec.Fit.statMethod = str(self.statistic)
        xspec.Fit.query = "yes"

        os.chdir(self.path)

        self.spec_mos1 = xspec.Spectrum(self.spectrum_files["mos1"])
        self.spec_mos1.ignore(self.energy_range["mos1"])

        self.spec_mos2 = xspec.Spectrum(self.spectrum_files["mos2"])
        self.spec_mos2.ignore(self.energy_range["mos2"])

        self.spec_pn = xspec.Spectrum(self.spectrum_files["pn"])
        self.spec_pn.ignore(self.energy_range["pn"])

        self.spec_rass = xspec.Spectrum(self.spectrum_files["rass"])

        print(self.spec_mos1, self.spec_mos2, self.spec_pn, self.spec_rass)

        #self.m1 = xspec.Model("{}+{}*{}".format(Spectrum.esas_bkg_model, self.abs_model, self.src_model))
        self.m1 = xspec.Model(Spectrum.esas_model)

        gau1 = Gaussian(component_number=1, LineE=1.48516)
        self.m1.gaussian.LineE.values, self.m1.gaussian.Sigma.values, self.m1.gaussian.norm.values = gau1.get_params()

        gau2 = Gaussian(component_number=2, LineE=1.74000)
        self.m1.gaussian_2.LineE.values, self.m1.gaussian_2.Sigma.values, self.m1.gaussian_2.norm.values = gau2.get_params()

        gau3 = Gaussian(component_number=3, LineE=7.11)
        self.m1.gaussian_3.LineE.values, self.m1.gaussian_3.Sigma.values, self.m1.gaussian_3.norm.values = gau3.get_params()

        gau4 = Gaussian(component_number=4, LineE=7.49)
        self.m1.gaussian_4.LineE.values, self.m1.gaussian_4.Sigma.values, self.m1.gaussian_4.norm.values = gau4.get_params()

        gau5 = Gaussian(component_number=5, LineE=8.05)
        self.m1.gaussian_5.LineE.values, self.m1.gaussian_5.Sigma.values, self.m1.gaussian_5.norm.values = gau5.get_params()

        gau6 = Gaussian(component_number=6, LineE=8.62)
        self.m1.gaussian_6.LineE.values, self.m1.gaussian_6.Sigma.values, self.m1.gaussian_6.norm.values = gau6.get_params()

        gau7 = Gaussian(component_number=7, LineE=8.90)
        self.m1.gaussian_7.LineE.values, self.m1.gaussian_7.Sigma.values, self.m1.gaussian_7.norm.values = gau7.get_params()

        print(dir(self.m1))
        print(self.m1.show())
        print(self.m1.componentNames)
        print(self.m1.setPars())

        #self.m1.phabs.nH = str(self.nh)
        #self.m1.phabs.nH.frozen = True
        #self.m1.snapec.redshift = str(self.redshift)

    def fit(self):
        xspec.Fit.perform()

        xspec.Fit.error("1.0 41")
        statistic = xspec.Fit.statistic
        dof = xspec.Fit.dof
        chi = statistic / dof

        print(chi)
