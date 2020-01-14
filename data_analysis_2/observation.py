import os
import sys
import glob
import subprocess
from shutil import copyfile, copy
from region import Region

class Observation:
    def __init__(self, info_dict):
        self.info_dict = info_dict

        self.regions = {"mos1": [],
                        "mos2": [],
                        "pn": []}

        self.set_environ()

    def info(self):
        print(self.info_dict)

    def set_environ(self):
        self.environ = dict(os.environ)

        self.environ['SAS_ODF'] = self.info_dict["odf_path"]
        self.environ['SAS_CCFPATH'] = self.info_dict["ccf_path"]

        self.esas_caldb = os.path.abspath(os.path.join(self.info_dict["ccf_path"], 'esas'))
        self.environ['esas_caldb'] = self.esas_caldb

    def set_folders(self):
        self.folder_list = {"evt_copy": os.path.abspath(os.path.join(self.info_dict["odf_path"], "../evt_copy")),
                            "epic": os.path.abspath(os.path.join(self.info_dict["odf_path"], "../epic")),
                            "regions": os.path.abspath(os.path.join(self.info_dict["odf_path"], "../epic/regions")),
                            "mos1": os.path.abspath(os.path.join(self.info_dict["odf_path"], "../mos1")),
                            "mos2": os.path.abspath(os.path.join(self.info_dict["odf_path"], "../mos2")),
                            "pn": os.path.abspath(os.path.join(self.info_dict["odf_path"], "../pn"))}

        for folder_name, folder in self.folder_list.items():
            if not os.path.exists(folder):
                os.mkdir(folder)

    @staticmethod
    def file_check(path, file):
        _file_list = glob.glob(os.path.join(path, file))

        if len(_file_list) == 0:
            return ""
        else:
            abs_path_list = [os.path.abspath(_file) for _file in _file_list]
            return abs_path_list

    def abstract_proccess(self, path, file, args, cwd, env, set_new_env=False, new_env_name="", log=False, log_file="", clobber=False):
        if file==None or file=="":
            _file_list = []
        else:
            _file_list = Observation.file_check(path=path, file=file)
        len_file_list = len(_file_list)

        if len_file_list>0 and not clobber:
            print("{} file(s) already exist!".format(file))
        else:
            if log:
                proc = subprocess.Popen(args, cwd=cwd, env=env, stdout=subprocess.PIPE)
                proc_out, proc_err = proc.communicate()

                out_file = os.path.join(cwd, log_file)
                with open(out_file, "w") as f:
                    f.write(proc_out.decode("utf-8"))
            else:
                proc = subprocess.Popen(args, cwd=cwd, env=env).wait()

        if set_new_env:
            _file_list = Observation.file_check(path=path, file=file)
            self.environ[new_env_name] = _file_list[0]

    def cifbuild(self, clobber=False):
        args = ['cifbuild',
                'fullpath=yes']

        self.abstract_proccess(path=self.info_dict["odf_path"],
                               file='ccf.cif',
                               args=args,
                               cwd=self.info_dict["odf_path"],
                               env=self.environ,
                               clobber=clobber,
                               set_new_env=True,
                               new_env_name='SAS_CCF')

    def odfingest(self, clobber=False):
        args = ['odfingest',
                'odfdir={}'.format(self.info_dict["odf_path"]),
                'outdir={}'.format(self.info_dict["odf_path"])]

        self.abstract_proccess(path=self.info_dict["odf_path"],
                               file='*SUM.SAS*',
                               args=args,
                               cwd=self.info_dict["odf_path"],
                               env=self.environ,
                               clobber=clobber,
                               set_new_env=True,
                               new_env_name="SAS_ODF")

    def chain(self, clobber=False):
        file_list = ['*M*EVLI*',
                     '*PN*PI*EVLI*',
                     '*PN*OO*EVLI*']

        args_list = [['emchain'],
                     ['epchain'],
                     ['epchain', 'withoutoftime=true']]

        for file, args in zip(file_list, args_list):
            self.abstract_proccess(path=self.info_dict["odf_path"],
                                   file=file,
                                   args=args,
                                   cwd=self.info_dict["odf_path"],
                                   env=self.environ,
                                   clobber=clobber)

    def copy_events(self):
        mos1_evt_file = Observation.file_check(path=self.info_dict["odf_path"], file="*M1*EVLI*")[0]
        mos2_evt_file = Observation.file_check(path=self.info_dict["odf_path"], file="*M2*EVLI*")[0]
        pn_evt_file = Observation.file_check(path=self.info_dict["odf_path"], file="*PN*PI*EVLI*")[0]
        pn_oot_evt_file = Observation.file_check(path=self.info_dict["odf_path"], file="*PN*OO*EVLI*")[0]

        _temp_file_path = os.path.join(self.info_dict["odf_path"], "{}/{}".format(self.folder_list["mos1"], "mos1.fits"))
        if Observation.file_check(_temp_file_path) == "":
            copyfile(mos1_evt_file, _temp_file_path)

        _temp_file_path = os.path.join(self.info_dict["odf_path"], "{}/{}".format(self.folder_list["mos2"], "mos2.fits"))
        if Observation.file_check(_temp_file_path) == "":
            copyfile(mos2_evt_file, _temp_file_path)

        _temp_file_path = os.path.join(self.info_dict["odf_path"], "{}/{}".format(self.folder_list["pn"], "pn.fits"))
        if Observation.file_check(_temp_file_path) == "":
            copyfile(pn_evt_file, _temp_file_path)

        copy(mos1_evt_file, self.folder_list["epic"])
        copy(mos2_evt_file, self.folder_list["epic"])
        copy(pn_evt_file, self.folder_list["epic"])
        copy(pn_oot_evt_file, self.folder_list["epic"])

        copy(mos1_evt_file, self.folder_list["evt_copy"])
        copy(mos2_evt_file, self.folder_list["evt_copy"])
        copy(pn_evt_file, self.folder_list["evt_copy"])
        copy(pn_oot_evt_file, self.folder_list["evt_copy"])

    def epic_filter(self, clobber=False):
        file_list = ['pn*clean*',
                     'mos*clean*']

        args_list = [['pn-filter'],
                     ['mos-filter']]

        for file, args in zip(file_list, args_list):
            if 'mos' in file:
                log_file = "mos-filter-log.txt"
            elif 'pn' in file:
                log_file = "pn-filter-log.txt"
            else:
                log_file = "no-name-log.txt"

            self.abstract_proccess(path=self.folder_list["epic"],
                                   file=file,
                                   args=args,
                                   cwd=self.folder_list["epic"],
                                   env=self.environ,
                                   clobber=clobber,
                                   log=True,
                                   log_file=log_file)

    def convert_coords(self, mos1=True, mos2=True, pn=True, clobber=False):
        _camera_list = [mos1, mos2, pn]

        _image_list = ["mos{}-obj-im.fits".format(self.info_dict["mos1_prefix"]),
                       "mos{}-obj-im.fits".format(self.info_dict["mos2_prefix"]),
                       "pn{}-obj-im.fits".format(self.info_dict["pn_prefix"])]

        _root_list = ["mos1", "mos2", "pn"]

        _log_file_list = ["{}_coords_log.txt".format(_root) for _root in _root_list]

        for _camera, _image, _root, _log_file in zip(_camera_list, _image_list, _root_list, _log_file_list):
            if _camera:
                args = ['ecoordconv',
                        'imageset={}'.format(_image),
                        'x={}'.format(self.info_dict["ra"]),
                        'y={}'.format(self.info_dict["dec"]),
                        'coordtype=eqpos']

                self.abstract_proccess(path=self.folder_list["epic"],
                                       file=_log_file,
                                       args=args,
                                       cwd=self.folder_list["epic"],
                                       env=self.environ,
                                       clobber=clobber,
                                       log=True,
                                       log_file=_log_file)

                _log_full_path = os.path.join(self.folder_list["epic"], _log_file)
                with open(_log_full_path, "r", encoding="utf-8") as f:
                    _log_text = f.readlines()

                _temp_text = ""
                for line in _log_text:
                    if "DETX: DETY:" in line:
                        _temp_text = line.strip().split()[-2:]

                self.info_dict["{}_detx".format(_root)], self.info_dict["{}_dety".format(_root)] = _temp_text

    def cheese(self, scale=0.5, rate=1.0, dist=40, clobber=False):
        args = ['cheese',
                'prefixm=\'{} {}\''.format(self.info_dict["mos1_prefix"], self.info_dict["mos2_prefix"]),
                'prefixp={}'.format(self.info_dict["pn_prefix"]),
                'scale={}'.format(scale),
                'rate={}'.format(rate),
                'dist={}'.format(dist),
                'clobber={}'.format(clobber),
                'elow=400', 'ehigh=7200']

        self.abstract_proccess(path=self.folder_list["epic"],
                               file='*cheese*',
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

    def create_region(self, mos1=True, mos2=True, pn=True, ra=None, dec=None, inner_radius=0, outer_radius=120, name=""):
        if (ra==None) or (dec==None):
            ra = self.info_dict["ra"]
            dec = self.info_dict["dec"]
            print("RA and Dec of this region will be set as cluster center..")

        if mos1:
            _region = Region(camera="mos1",
                             ra=ra, dec=dec,
                             detx=self.info_dict["mos1_detx"],
                             dety=self.info_dict["mos1_dety"],
                             inner_radius=inner_radius,
                             outer_radius=outer_radius,
                             name=name, text="")
            _region.save_region(path=self.folder_list["regions"])
            self.regions["mos1"].append(_region)

        if mos2:
            _region = Region(camera="mos2",
                             ra=ra, dec=dec,
                             detx=self.info_dict["mos2_detx"],
                             dety=self.info_dict["mos2_dety"],
                             inner_radius=inner_radius,
                             outer_radius=outer_radius,
                             name=name, text="")
            _region.save_region(path=self.folder_list["regions"])
            self.regions["mos2"].append(_region)

        if pn:
            _region = Region(camera="pn",
                             ra=ra, dec=dec,
                             detx=self.info_dict["pn_detx"],
                             dety=self.info_dict["pn_dety"],
                             inner_radius=inner_radius,
                             outer_radius=outer_radius,
                             name=name, text="")
            _region.save_region(path=self.folder_list["regions"])
            self.regions["pn"].append(_region)

    def list_regions(self):
        for camera, regions in self.regions.items():
            print("Camera: {}".format(camera))
            for num, region in enumerate(regions):
                print("{}{}) {}".format(" "*2, num+1, region.name))

    def mos1_spectrum(self, region_object=None, region_file="", mask=0, with_image=False, elow=0, ehigh=0, fov=False, clobber=True):
        if region_file != "":
            temp_region_file = Observation.file_check(path=self.folder_list["regions"], file=region_file)
            if (temp_region_file == '') and (fov == False):
                print("{} region file can not be found!".format(region_file))
                sys.exit()
            my_region = region_file

        if region_object != None:
            my_region = region_object.name

        if with_image:
            elow = 400
            ehigh = 7200

        args = ['mos-spectra',
                'prefix={}'.format(self.info_dict["mos1_prefix"]),
                'caldb={}'.format(self.environ['esas_caldb']),
                'region={}/{}'.format("regions", my_region),
                'mask={}'.format(mask),
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'ccd1={}'.format(self.info_dict["mos1_ccds"][0]),
                'ccd2={}'.format(self.info_dict["mos1_ccds"][1]),
                'ccd3={}'.format(self.info_dict["mos1_ccds"][2]),
                'ccd4={}'.format(self.info_dict["mos1_ccds"][3]),
                'ccd5={}'.format(self.info_dict["mos1_ccds"][4]),
                'ccd6={}'.format(self.info_dict["mos1_ccds"][5]),
                'ccd7={}'.format(self.info_dict["mos1_ccds"][6])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

        args = ['mos_back',
                'prefix={}'.format(self.info_dict["mos1_prefix"]),
                'caldb={}'.format(self.environ['esas_caldb']),
                'diag=0',
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'ccd1={}'.format(self.info_dict["mos1_ccds"][0]),
                'ccd2={}'.format(self.info_dict["mos1_ccds"][1]),
                'ccd3={}'.format(self.info_dict["mos1_ccds"][2]),
                'ccd4={}'.format(self.info_dict["mos1_ccds"][3]),
                'ccd5={}'.format(self.info_dict["mos1_ccds"][4]),
                'ccd6={}'.format(self.info_dict["mos1_ccds"][5]),
                'ccd7={}'.format(self.info_dict["mos1_ccds"][6])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

        if with_image:
            args = ['rot-im-det-sky',
                    'prefix={}'.format(self.info_dict["mos1_prefix"]),
                    'mask={}'.format(mask),
                    'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                    'mode=1']

            self.abstract_proccess(path=self.folder_list["epic"],
                                   file=None,
                                   args=args,
                                   cwd=self.folder_list["epic"],
                                   env=self.environ,
                                   clobber=clobber)

    def mos2_spectrum(self, region_object=None, region_file="", mask=0, with_image=False, elow=0, ehigh=0, fov=False, clobber=True):
        if region_file != "":
            temp_region_file = Observation.file_check(path=self.folder_list["regions"], file=region_file)
            if (temp_region_file == '') and (fov == False):
                print("{} region file can not be found!".format(region_file))
                sys.exit()
            my_region = region_file

        if region_object != None:
            my_region = region_object.name

        if with_image:
            elow = 400
            ehigh = 7200

        args = ['mos-spectra',
                'prefix={}'.format(self.info_dict["mos2_prefix"]),
                'caldb={}'.format(self.environ['esas_caldb']),
                'region={}/{}'.format("regions", my_region),
                'mask={}'.format(mask),
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'ccd1={}'.format(self.info_dict["mos2_ccds"][0]),
                'ccd2={}'.format(self.info_dict["mos2_ccds"][1]),
                'ccd3={}'.format(self.info_dict["mos2_ccds"][2]),
                'ccd4={}'.format(self.info_dict["mos2_ccds"][3]),
                'ccd5={}'.format(self.info_dict["mos2_ccds"][4]),
                'ccd6={}'.format(self.info_dict["mos2_ccds"][5]),
                'ccd7={}'.format(self.info_dict["mos2_ccds"][6])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

        args = ['mos_back',
                'prefix={}'.format(self.info_dict["mos2_prefix"]),
                'caldb={}'.format(self.environ['esas_caldb']),
                'diag=0',
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'ccd1={}'.format(self.info_dict["mos2_ccds"][0]),
                'ccd2={}'.format(self.info_dict["mos2_ccds"][1]),
                'ccd3={}'.format(self.info_dict["mos2_ccds"][2]),
                'ccd4={}'.format(self.info_dict["mos2_ccds"][3]),
                'ccd5={}'.format(self.info_dict["mos2_ccds"][4]),
                'ccd6={}'.format(self.info_dict["mos2_ccds"][5]),
                'ccd7={}'.format(self.info_dict["mos2_ccds"][6])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

        if with_image:
            args = ['rot-im-det-sky',
                    'prefix={}'.format(self.info_dict["mos2_prefix"]),
                    'mask={}'.format(mask),
                    'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                    'mode=1']

            self.abstract_proccess(path=self.folder_list["epic"],
                                   file=None,
                                   args=args,
                                   cwd=self.folder_list["epic"],
                                   env=self.environ,
                                   clobber=clobber)

    def pn_spectrum(self, region_object=None, region_file="", mask=0, with_image=False, elow=0, ehigh=0, fov=False, clobber=True):
        if region_file != "":
            temp_region_file = Observation.file_check(path=self.folder_list["regions"], file=region_file)
            if (temp_region_file == '') and (fov == False):
                print("{} region file can not be found!".format(region_file))
                sys.exit()
            my_region = region_file

        if region_object != None:
            my_region = region_object.name

        if with_image:
            elow = 400
            ehigh = 7200

        args = ['pn-spectra',
                'prefix={}'.format(self.info_dict["pn_prefix"]),
                'caldb={}'.format(self.environ['esas_caldb']),
                'region={}/{}'.format("regions", my_region),
                'mask={}'.format(mask),
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'quad1={}'.format(self.info_dict["pn_ccds"][0]),
                'quad2={}'.format(self.info_dict["pn_ccds"][1]),
                'quad3={}'.format(self.info_dict["pn_ccds"][2]),
                'quad4={}'.format(self.info_dict["pn_ccds"][3])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

        args = ['pn_back',
                'prefix={}'.format(self.info_dict["pn_prefix"]),
                'caldb={}'.format(self.environ['esas_caldb']),
                'diag=0',
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'quad1={}'.format(self.info_dict["pn_ccds"][0]),
                'quad2={}'.format(self.info_dict["pn_ccds"][1]),
                'quad3={}'.format(self.info_dict["pn_ccds"][2]),
                'quad4={}'.format(self.info_dict["pn_ccds"][3])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

        if with_image:
            args = ['rot-im-det-sky',
                    'prefix={}'.format(self.info_dict["pn_prefix"]),
                    'mask={}'.format(mask),
                    'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                    'mode=1']

            self.abstract_proccess(path=self.folder_list["epic"],
                                   file=None,
                                   args=args,
                                   cwd=self.folder_list["epic"],
                                   env=self.environ,
                                   clobber=clobber)

    def rename_mos1_spectra_output(self, region_object, clobber=True):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        file_names_dict = {'mos{}-obj.pi': 'mos{}-obj-{}.pi',
                           'mos{}-back.pi': 'mos{}-back-{}.pi',
                           'mos{}.rmf': 'mos{}-{}.rmf',
                           'mos{}.arf': 'mos{}-{}.arf',
                           'mos{}-obj-im-sp-det.fits': 'mos{}-sp-{}.fits'}

        args_list = [['mv', key.format(self.info_dict["mos1_prefix"]), value.format(self.info_dict["mos1_prefix"], name)] for key, value in file_names_dict.items()]

        for args in args_list:
            if self.file_check(self.folder_list["epic"], args[1]) == '':
                print("{} file doesn't exist to rename!".format(args[1]))
            else:
                self.abstract_proccess(path=self.folder_list["epic"],
                                       file=None,
                                       args=args,
                                       cwd=self.folder_list["epic"],
                                       env=self.environ,
                                       clobber=clobber)

    def rename_mos2_spectra_output(self, region_object, clobber=True):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        file_names_dict = {'mos{}-obj.pi': 'mos{}-obj-{}.pi',
                           'mos{}-back.pi': 'mos{}-back-{}.pi',
                           'mos{}.rmf': 'mos{}-{}.rmf',
                           'mos{}.arf': 'mos{}-{}.arf',
                           'mos{}-obj-im-sp-det.fits': 'mos{}-sp-{}.fits'}

        args_list = [['mv', key.format(self.info_dict["mos2_prefix"]), value.format(self.info_dict["mos2_prefix"], name)] for key, value in file_names_dict.items()]

        for args in args_list:
            if self.file_check(self.folder_list["epic"], args[1]) == '':
                print("{} file doesn't exist to rename!".format(args[1]))
            else:
                self.abstract_proccess(path=self.folder_list["epic"],
                                       file=None,
                                       args=args,
                                       cwd=self.folder_list["epic"],
                                       env=self.environ,
                                       clobber=clobber)

    def rename_pn_spectra_output(self, region_object, clobber=True):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        file_names_dict = {'pn{}-obj.pi': 'pn{}-obj-{}.pi',
                           'pn{}-back.pi': 'pn{}-back-{}.pi',
                           'pn{}.rmf': 'pn{}-{}.rmf',
                           'pn{}.arf': 'pn{}-{}.arf',
                           'pn{}-obj-im-sp-det.fits': 'pn{}-sp-{}.fits'}

        args_list = [['mv', key.format(self.info_dict["pn_prefix"]), value.format(self.info_dict["pn_prefix"], name)] for key, value in file_names_dict.items()]

        for args in args_list:
            if self.file_check(self.folder_list["epic"], args[1]) == '':
                print("{} file doesn't exist to rename!".format(args[1]))
            else:
                self.abstract_proccess(path=self.folder_list["epic"],
                                       file=None,
                                       args=args,
                                       cwd=self.folder_list["epic"],
                                       env=self.environ,
                                       clobber=clobber)

    def grppha_mos1(self, region_object, bin_value=20, clobber=True):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        if os.path.isfile(os.path.join(self.folder_list["epic"], 'mos{}-obj-{}-grp.pi'.format(self.info_dict["mos1_prefix"], name))):
            os.remove(os.path.join(self.folder_list["epic"], 'mos{}-obj-{}-grp.pi'.format(self.info_dict["mos1_prefix"], name)))

        args = ['grppha',
                'mos{}-obj-{}.pi'.format(self.info_dict["mos1_prefix"], name),
                'mos{}-obj-{}-grp.pi'.format(self.info_dict["mos1_prefix"], name),
                'chkey BACKFILE mos{0}-back-{1}.pi & chkey RESPFILE mos{0}-{1}.rmf & \
                 chkey ANCRFILE mos{0}-{1}.arf & group min {2} & exit'.format(self.info_dict["mos1_prefix"], name, bin_value)]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

    def grppha_mos2(self, region_object, bin_value=20, clobber=True):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        if os.path.isfile(os.path.join(self.folder_list["epic"], 'mos{}-obj-{}-grp.pi'.format(self.info_dict["mos2_prefix"], name))):
            os.remove(os.path.join(self.folder_list["epic"], 'mos{}-obj-{}-grp.pi'.format(self.info_dict["mos2_prefix"], name)))

        args = ['grppha',
                'mos{}-obj-{}.pi'.format(self.info_dict["mos2_prefix"], name),
                'mos{}-obj-{}-grp.pi'.format(self.info_dict["mos2_prefix"], name),
                'chkey BACKFILE mos{0}-back-{1}.pi & chkey RESPFILE mos{0}-{1}.rmf & \
                 chkey ANCRFILE mos{0}-{1}.arf & group min {2} & exit'.format(self.info_dict["mos2_prefix"], name, bin_value)]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

    def grppha_pn(self, region_object, bin_value=20, clobber=True):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        if os.path.isfile(os.path.join(self.folder_list["epic"], 'pn{}-obj-{}-grp.pi'.format(self.info_dict["pn_prefix"], name))):
            os.remove(os.path.join(self.folder_list["epic"], 'pn{}-obj-{}-grp.pi'.format(self.info_dict["pn_prefix"], name)))

        args = ['grppha',
                'pn{}-obj-{}.pi'.format(self.info_dict["pn_prefix"], name),
                'pn{}-obj-{}-grp.pi'.format(self.info_dict["pn_prefix"], name),
                'chkey BACKFILE pn{0}-back-{1}.pi & chkey RESPFILE pn{0}-{1}.rmf & \
                 chkey ANCRFILE pn{0}-{1}.arf & group min {2} & exit'.format(self.info_dict["pn_prefix"], name, bin_value)]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file=None,
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=clobber)

    def proton_scale_mos1(self, region_object):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        args = ['proton_scale',
                'caldb={}'.format(self.environ['esas_caldb']),
                'mode=1',
                'detector=1',
                'maskfile=mos{}-sp-{}.fits'.format(self.info_dict["mos1_prefix"], name),
                'specfile=mos{}-obj-{}.pi'.format(self.info_dict["mos1_prefix"], name)]

        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.environ, stdout=subprocess.PIPE)
        out = proc.communicate()[0].decode("utf-8").splitlines()
        region_object.area = [out[i] for i in range(len(out)) if "Area" in out[i]][0].split()[1]

        output = "Region Name: {} \nArea: {}".format(region_object.name, region_object.area)
        print(output)
        return region_object.area

    def proton_scale_mos2(self, region_object):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        args = ['proton_scale',
                'caldb={}'.format(self.environ['esas_caldb']),
                'mode=1',
                'detector=2',
                'maskfile=mos{}-sp-{}.fits'.format(self.info_dict["mos2_prefix"], name),
                'specfile=mos{}-obj-{}.pi'.format(self.info_dict["mos2_prefix"], name)]

        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.environ, stdout=subprocess.PIPE)
        out = proc.communicate()[0].decode("utf-8").splitlines()
        region_object.area = [out[i] for i in range(len(out)) if "Area" in out[i]][0].split()[1]

        output = "Region Name: {} \nArea: {}".format(region_object.name, region_object.area)
        print(output)
        return region_object.area

    def proton_scale_pn(self, region_object):
        name = "{}-{}".format(region_object.inner_radius, region_object.outer_radius)

        args = ['proton_scale',
                'caldb={}'.format(self.environ['esas_caldb']),
                'mode=1',
                'detector=3',
                'maskfile=pn{}-sp-{}.fits'.format(self.info_dict["pn_prefix"], name),
                'specfile=pn{}-obj-{}.pi'.format(self.info_dict["pn_prefix"], name)]

        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.environ, stdout=subprocess.PIPE)
        out = proc.communicate()[0].decode("utf-8").splitlines()
        region_object.area = [out[i] for i in range(len(out)) if "Area" in out[i]][0].split()[1]

        output = "Region Name: {} \nArea: {}".format(region_object.name, region_object.area)
        print(output)
        return region_object.area