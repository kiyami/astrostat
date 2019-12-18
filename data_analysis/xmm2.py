import os
import glob
import subprocess
from shutil import copyfile, copy

class Observation:

    def __init__(self, info_dict):
        self.object_name = info_dict["object_name"]
        self.obs_id = info_dict["obs_id"]
        self.ODF_path = info_dict["odf_path"]
        self.ccf_path = info_dict["ccf_path"]

        self.environ = dict(os.environ)

        self.environ['SAS_ODF'] = self.ODF_path
        self.environ['SAS_CCFPATH'] = self.ccf_path

        self.esas_caldb = os.path.abspath(os.path.join(self.ccf_path, 'esas'))
        self.environ['esas_caldb'] = self.esas_caldb

        self.set_folders()

    def get_info(self):
        print("Object: {}".format(self.object_name),
              "Obs_Id: {}".format(self.obs_id),
              "ODF_path: {}".format(self.ODF_path),
              "CCF_path: {}".format(self.ccf_path), sep="\n")

    def set_folders(self):
        self.folder_list = {"evt_copy": os.path.abspath(os.path.join(self.ODF_path, "../evt_copy")),
                            "epic": os.path.abspath(os.path.join(self.ODF_path, "../epic")),
                            "regions": os.path.abspath(os.path.join(self.ODF_path, "../epic/regions")),
                            "mos1": os.path.abspath(os.path.join(self.ODF_path, "../mos1")),
                            "mos2": os.path.abspath(os.path.join(self.ODF_path, "../mos2")),
                            "pn": os.path.abspath(os.path.join(self.ODF_path, "../pn"))}

        for folder_name, folder in self.folder_list.items():
            if not os.path.exists(folder):
                os.mkdir(folder)

    @staticmethod
    def file_check(path, file):
        my_file = glob.glob(os.path.join(path, file))

        if len(my_file) == 0:
            return ""
        else:
            return os.path.abspath(my_file[0])

    def abstract_proccess(self, path, file, args, cwd, env, set_new_env=False, new_env_name="", log=False, log_file="", clobber=False):
        my_file = Observation.file_check(path=path, file=file)

        if my_file and not clobber:
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
            my_file = Observation.file_check(path=path, file=file)
            self.environ[new_env_name] = my_file

    def cifbuild(self):
        args = ['cifbuild',
                'fullpath=yes']

        self.abstract_proccess(path=self.ODF_path,
                               file='ccf.cif',
                               args=args,
                               cwd=self.ODF_path,
                               env=self.environ,
                               set_new_env=True,
                               new_env_name='SAS_CCF')

    def odfingest(self):
        args = ['odfingest',
                'odfdir={}'.format(self.ODF_path),
                'outdir={}'.format(self.ODF_path)]

        self.abstract_proccess(path=self.ODF_path,
                               file='*SUM.SAS*',
                               args=args,
                               cwd=self.ODF_path,
                               env=self.environ,
                               set_new_env=True,
                               new_env_name="SAS_ODF")

    def chain(self):
        file_list = ['*M*EVLI*',
                     '*PN*PI*EVLI*',
                     '*PN*OO*EVLI*']

        args_list = [['emchain'],
                     ['epchain'],
                     ['epchain', 'withoutoftime=true']]

        for file, args in zip(file_list, args_list):
            self.abstract_proccess(path=self.ODF_path,
                                   file=file,
                                   args=args,
                                   cwd=self.ODF_path,
                                   env=self.environ)


    def copy_events(self):
        mos1_evt_file = Observation.file_check(path=self.ODF_path, file="*M1*EVLI*")
        mos2_evt_file = Observation.file_check(path=self.ODF_path, file="*M2*EVLI*")
        pn_evt_file = Observation.file_check(path=self.ODF_path, file="*PN*PI*EVLI*")
        pn_oot_evt_file = Observation.file_check(path=self.ODF_path, file="*PN*OO*EVLI*")

        copyfile(mos1_evt_file, os.path.join(self.ODF_path, "{}/{}".format(self.folder_list["mos1"], "mos1.fits")))
        copyfile(mos2_evt_file, os.path.join(self.ODF_path, "{}/{}".format(self.folder_list["mos2"], "mos2.fits")))
        copyfile(pn_evt_file, os.path.join(self.ODF_path, "{}/{}".format(self.folder_list["pn"], "pn.fits")))

        copy(mos1_evt_file, self.folder_list["epic"])
        copy(mos2_evt_file, self.folder_list["epic"])
        copy(pn_evt_file, self.folder_list["epic"])
        copy(pn_oot_evt_file, self.folder_list["epic"])

        copy(mos1_evt_file, self.folder_list["evt_copy"])
        copy(mos2_evt_file, self.folder_list["evt_copy"])
        copy(pn_evt_file, self.folder_list["evt_copy"])
        copy(pn_oot_evt_file, self.folder_list["evt_copy"])

    def epic_filter(self):
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
                                   log=True,
                                   log_file=log_file)

    def set_prefixes_and_ccds(self, info_dict):
        self.mos1_prefix = info_dict["mos1_prefix"]
        self.mos2_prefix = info_dict["mos2_prefix"]
        self.pn_prefix = info_dict["pn_prefix"]

        self.mos1_ccds = info_dict["mos1_ccds"]
        self.mos2_ccds = info_dict["mos2_ccds"]
        self.pn_ccds = info_dict["pn_ccds"]

    def cheese(self, scale=0.5, rate=1.0, dist=40, clobber=True):
        args = ['cheese',
                'prefixm=\'{} {}\''.format(self.mos1_prefix, self.mos2_prefix),
                'prefixp={}'.format(self.pn_prefix),
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

    def set_detx_dety(self, info_dict):
        self.mos1_detx = info_dict["mos1_detx"]
        self.mos1_dety = info_dict["mos1_dety"]

        self.mos2_detx = info_dict["mos2_detx"]
        self.mos2_dety = info_dict["mos2_dety"]

        self.pn_detx = info_dict["pn_detx"]
        self.pn_dety = info_dict["pn_dety"]

    def create_region_file(self, inner_radius, outer_radius):
        inner_radius_phy = float(inner_radius) * 20.0
        outer_radius_phy = float(outer_radius) * 20.0

        mos1_text = "&&((DETX,DETY) IN circle({0},{1},{2}))&&!((DETX,DETY) IN circle({0},{1},{3}))".format(self.mos1_detx,
                                                                                                           self.mos1_dety,
                                                                                                           outer_radius_phy,
                                                                                                           inner_radius_phy)
        mos1_file_name = "reg1-{}-{}.txt".format(int(inner_radius), int(outer_radius))

        with open(os.path.join(self.folder_list["regions"], mos1_file_name), "w") as f:
            f.write(mos1_text)

        mos2_text = "&&((DETX,DETY) IN circle({0},{1},{2}))&&!((DETX,DETY) IN circle({0},{1},{3}))".format(self.mos2_detx,
                                                                                                           self.mos2_dety,
                                                                                                           outer_radius_phy,
                                                                                                           inner_radius_phy)
        mos2_file_name = "reg2-{}-{}.txt".format(int(inner_radius), int(outer_radius))

        with open(os.path.join(self.folder_list["regions"], mos2_file_name), "w") as f:
            f.write(mos2_text)

        pn_text = "&&((DETX,DETY) IN circle({0},{1},{2}))&&!((DETX,DETY) IN circle({0},{1},{3}))".format(self.pn_detx,
                                                                                                         self.pn_dety,
                                                                                                         outer_radius_phy,
                                                                                                         inner_radius_phy)
        pn_file_name = "reg3-{}-{}.txt".format(int(inner_radius), int(outer_radius))

        with open(os.path.join(self.folder_list["regions"], pn_file_name), "w") as f:
            f.write(pn_text)

    def mos1_spectra(self, region_file='reg.txt', mask=0, with_image=False, elow=400, ehigh=7200):

        if not with_image:
            elow = 0
            ehigh = 0

        args = ['mos-spectra',
                'prefix={}'.format(self.mos1_prefix),
                'caldb={}'.format(self.environ['esas_caldb']),
                'region={}/{}'.format("regions", region_file),
                'mask={}'.format(mask),
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'ccd1={}'.format(self.mos1_ccds[0]),
                'ccd2={}'.format(self.mos1_ccds[1]),
                'ccd3={}'.format(self.mos1_ccds[2]),
                'ccd4={}'.format(self.mos1_ccds[3]),
                'ccd5={}'.format(self.mos1_ccds[4]),
                'ccd6={}'.format(self.mos1_ccds[5]),
                'ccd7={}'.format(self.mos1_ccds[6])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file='',
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=True)

        args = ['mos_back',
                'prefix={}'.format(self.mos1_prefix),
                'caldb={}'.format(self.environ['esas_caldb']),
                'diag=0',
                'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                'ccd1={}'.format(self.mos1_ccds[0]),
                'ccd2={}'.format(self.mos1_ccds[1]),
                'ccd3={}'.format(self.mos1_ccds[2]),
                'ccd4={}'.format(self.mos1_ccds[3]),
                'ccd5={}'.format(self.mos1_ccds[4]),
                'ccd6={}'.format(self.mos1_ccds[5]),
                'ccd7={}'.format(self.mos1_ccds[6])]

        self.abstract_proccess(path=self.folder_list["epic"],
                               file='',
                               args=args,
                               cwd=self.folder_list["epic"],
                               env=self.environ,
                               clobber=True)

        if with_image:
            args = ['rot-im-det-sky',
                    'prefix={}'.format(self.mos1_prefix),
                    'mask={}'.format(mask),
                    'elow={}'.format(elow), 'ehigh={}'.format(ehigh),
                    'mode=1']

            self.abstract_proccess(path=self.folder_list["epic"],
                                   file='',
                                   args=args,
                                   cwd=self.folder_list["epic"],
                                   env=self.environ,
                                   clobber=True)


class Threads:
    @staticmethod
    def initialize_obs(info_dict):
        obs = Observation(info_dict)
        return obs

    @staticmethod
    def initialise_new_data(obs):
        obs.cifbuild()
        obs.odfingest()
        obs.chain()
        obs.copy_events()
        obs.epic_filter()

    @staticmethod
    def initialise_existing_data(obs):
        obs.cifbuild()
        obs.odfingest()

    @staticmethod
    def set_prefixes_and_ccds(obs, info_dict):
        obs.set_prefixes_and_ccds(info_dict)

    @staticmethod
    def cheese(obs, scale=0.5, rate=1.0, dist=40, clobber=False):
        obs.cheese(scale, rate, dist, clobber)

    @staticmethod
    def set_detx_dety(obs, info_dict):
        obs.set_detx_dety(info_dict)

    @staticmethod
    def create_region_file(obs, inner_radius, outer_radius):
        obs.create_region_file(inner_radius, outer_radius)

    @staticmethod
    def mos1_spectra(obs, region_file='reg.txt', mask=0, with_image=False, elow=400, ehigh=7200):
        obs.mos1_spectra(region_file, mask, with_image, elow, ehigh)
