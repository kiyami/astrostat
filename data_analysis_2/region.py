import sys
import os

class Region:
    def __init__(self, camera="mos1", ra=None, dec=None, detx=None, dety=None, inner_radius=0, outer_radius=120, name="", text=""):
        self.camera = camera
        self.ra = ra
        self.dec = dec
        self.detx = detx
        self.dety = dety
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.name = name
        self.text = text

        self.area= None

        self.set_physical_radius()
        self.set_name()
        self.set_text()

    def set_physical_radius(self):
        self.inner_radius_phy = self.inner_radius * 20.0
        self.outer_radius_phy = self.outer_radius * 20.0

    def set_name(self):
        if self.camera == "mos1":
            _root = "reg1"
        elif self.camera == "mos2":
            _root = "reg2"
        elif self.camera == "pn":
            _root = "reg3"
        else:
            sys.exit("Invalid camera name!")

        if self.name == "":
            _name = "{}-{}-{}.txt".format(_root, self.inner_radius, self.outer_radius)
            self.name = _name

    def set_text(self):
        _text = "&&((DETX,DETY) IN circle({0},{1},{2}))&&!((DETX,DETY) IN circle({0},{1},{3}))".format(self.detx,
                                                                                                       self.dety,
                                                                                                       self.outer_radius_phy,
                                                                                                       self.inner_radius_phy)
        self.text = _text

    def save_region(self, path):
        with open(os.path.join(path, self.name), "w") as f:
            f.write(self.text)
