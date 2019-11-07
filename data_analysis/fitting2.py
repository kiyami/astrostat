import xspec
import os
import sys

class Gaussian:
    pass

class Apec:
    pass

class MyModel:
    camera = {"mos1": None,
             "mos2": None,
             "pn": None,
             "rass": None}

    @classmethod
    def set_model(cls, model, mos1=True, mos2=True, pn=True, rass=True):
        _model_counter = 1

        if mos1:
            cls.camera["mos1"] = model(_model_counter)
            _model_counter += 1

        if mos2:
            cls.camera["mos2"] = model(_model_counter)
            _model_counter += 1

        if pn:
            cls.camera["pn"] = model(_model_counter)
            _model_counter += 1

        if rass:
            cls.camera["rass"] = model(_model_counter)
            _model_counter += 1

    def __init__(self):
        self.components = []

    def add_comp(self, comp):
        self.components.append(comp)

class Epic:
    camera_dict = {"mos1": None,
                   "mos2": None,
                   "pn": None,
                   "rass": None}

    def __init__(self, camera):
        self.camera = camera
        self.model = None
        Epic.camera_dict[camera] = self

    @classmethod
    def set_model(cls, model):
        for camera in cls.camera_dict:
            if camera and isinstance(camera, Epic):
                camera.model = model

class Spectrum:

    diag_files = ["mos1-diag.rsp.gz", "mos2-diag.rsp.gz", "pn-diag.rsp.gz"]
    esas_model = "gaussian + gaussian + gaussian + gaussian + gaussian + gaussian + gaussian + constant*constant(gaussian + gaussian + apec + (apec + powerlaw)phabs + apec*phabs)"
    energy_range = {"mos1": "0.0-0.3,11.0-**",
                    "mos2": "0.0-0.3,11.0-**",
                    "pn": "0.0-0.4,11.0-**"}

    def __init__(self, spectrum_files, path, nh="0.0154", redshift="0.233", statistic="chi", model=None):
        self.spectrum_files = spectrum_files
        self.path = path
        self.nh = nh
        self.redshift = redshift
        self.statistic = statistic
        if not model:
            self.model = Spectrum.esas_model
        else:
            self.model = model

    def deneme(self):
        xspec.AllData.clear()
        xspec.Fit.statMethod = str(self.statistic)
        xspec.Fit.query = "yes"

        os.chdir(self.path)

        xspec.AllData("1:1 {} 2:2 {} 3:3 {} 4:4 {}".format(self.spectrum_files["mos1"],
                                                           self.spectrum_files["mos2"],
                                                           self.spectrum_files["pn"],
                                                           self.spectrum_files["rass"]))

        self.spec_mos1 = xspec.AllData(1)
        self.spec_mos1.ignore(self.energy_range["mos1"])

        self.spec_mos2 = xspec.AllData(2)
        self.spec_mos2.ignore(self.energy_range["mos2"])

        xspec.AllModels += "apec+gau+gau"

        MyModel.set_model(xspec.AllModels)
        MyModel.camera["mos1"].show()
        print(MyModel.camera["mos2"].componentNames)
        print(dir(MyModel.camera["mos2"].apec))

        mos1 = Epic("mos1")

        #self.my_model = {"gau1": Gaussian(),
        #                 "gau2": Gaussian(),
        #                 "apec1": Apec()}

