import os
import sys
import glob
import subprocess
from shutil import copyfile, copy

class Observation:
    sas_ccfpath = "/Users/kym/Desktop/software/ccf/"

    def __init__(self, object_name, obs_id, ODF_path):
        self.object_name = object_name
        self.obs_id = obs_id
        self.ODF_path = ODF_path

        self.envvars = dict(os.environ)
        self.envvars['SAS_ODF'] = self.ODF_path

    def get_info(self):
        print("Object: {}".format(self.object_name),
              "Obs_Id: {}".format(self.obs_id), sep="\n")

    def set_environ(self):
        self.envvars['SAS_CCFPATH'] = os.path.abspath(Observation.sas_ccfpath)

        if glob.glob(os.path.join(self.ODF_path, '*SUM.SAS')):
            self.envvars['SAS_ODF'] = os.path.abspath(glob.glob(os.path.join(self.ODF_path, '*SUM.SAS'))[0])
        else:
            sys.exit("*SUM.SAS file can not be found!")

        if glob.glob(os.path.join(self.ODF_path, 'ccf.cif')):
            self.envvars['SAS_CCF'] = os.path.abspath(glob.glob(os.path.join(self.ODF_path, 'ccf.cif'))[0])
        else:
            sys.exit("ccf.cif file can not be found!")

        self.esas_caldb = os.path.abspath(os.path.join(Observation.sas_ccfpath, 'esas'))
        self.envvars['esas_caldb'] = self.esas_caldb

    def cifbuild(self):
        if len(glob.glob(os.path.join(self.ODF_path, 'ccf.cif'))) == 0:
            args = ['cifbuild',
                    'fullpath=yes']

            proc = subprocess.Popen(args, cwd=self.ODF_path, env=self.envvars).wait()
        else:
            print("ccf.cif already exist!")

        self.envvars["SAS_CCF"] = os.path.abspath(glob.glob(os.path.join(self.ODF_path, 'ccf.cif'))[0])

    def odfingest(self):
        if len(glob.glob(os.path.join(self.ODF_path, '*SUM.SAS'))) == 0:
            args = ['odfingest',
                    'odfdir={}'.format(self.ODF_path),
                    'outdir={}'.format(self.ODF_path)]

            proc = subprocess.Popen(args, cwd=self.ODF_path, env=self.envvars).wait()
        else:
            print("*SUM.SAS already exist!")

        self.envvars["SAS_ODF"] = os.path.abspath(glob.glob(os.path.join(self.ODF_path, '*SUM.SAS'))[0])

    def chain(self):
        if len(glob.glob(os.path.join(self.ODF_path, '*M*EVLI*'))) == 0:
            args = ['emchain']
            proc = subprocess.Popen(args, cwd=self.ODF_path, env=self.envvars).wait()
        else:
            print("*M*EVLI* files already exist!")

        if len(glob.glob(os.path.join(self.ODF_path, '*PN*PI*EVLI*'))) == 0:
            args = ['epchain']
            proc = subprocess.Popen(args, cwd=self.ODF_path, env=self.envvars).wait()
        else:
            print("**PN*PI*EVLI* files already exist!")

        if len(glob.glob(os.path.join(self.ODF_path, '*PN*OO*EVLI*'))) == 0:
            args = ['epchain', 'withoutoftime=true']
            proc = subprocess.Popen(args, cwd=self.ODF_path, env=self.envvars).wait()
        else:
            print("*PN*OO*EVLI* files already exist!")

    def set_folders(self):
        self.folder_list = {"evt_copy": os.path.abspath(os.path.join(self.ODF_path, "../evt_copy")),
                            "epic": os.path.abspath(os.path.join(self.ODF_path, "../epic")),
                            "mos1": os.path.abspath(os.path.join(self.ODF_path, "../mos1")),
                            "mos2": os.path.abspath(os.path.join(self.ODF_path, "../mos2")),
                            "pn": os.path.abspath(os.path.join(self.ODF_path, "../pn"))}

        for folder_name, folder in self.folder_list.items():
            if not os.path.exists(folder):
                os.mkdir(folder)

    def copy_events(self):
        mos1_evt_file = os.path.join(self.ODF_path, glob.glob(os.path.join(self.ODF_path, "*M1*EVLI*"))[0])
        mos2_evt_file = os.path.join(self.ODF_path, glob.glob(os.path.join(self.ODF_path, "*M2*EVLI*"))[0])
        pn_evt_file = os.path.join(self.ODF_path, glob.glob(os.path.join(self.ODF_path, "*PN*PI*EVLI*"))[0])
        pn_oot_evt_file = os.path.join(self.ODF_path, glob.glob(os.path.join(self.ODF_path, "*PN*OO*EVLI*"))[0])

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
        if len(glob.glob(os.path.join(self.folder_list["epic"], 'pn*clean*'))) == 0:
            args = ['pn-filter']
            proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars, stdout=subprocess.PIPE)
            pn_out, pn_err = proc.communicate()

            out_file = os.path.join(self.folder_list["epic"], "pn_out.txt")
            with open(out_file, "w") as f:
                f.write(pn_out.decode("utf-8"))
        else:
            print("pn*clean* files already exist!")

        if len(glob.glob(os.path.join(self.folder_list["epic"], 'mos*clean*'))) == 0:
            args = ['mos-filter']
            proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars, stdout=subprocess.PIPE)
            mos_out, mos_err = proc.communicate()

            out_file = os.path.join(self.folder_list["epic"], "mos_out.txt")
            with open(out_file, "w") as f:
                f.write(mos_out.decode("utf-8"))
        else:
            print("mos*clean* files already exist!")

    def find_excluded_ccds(self):
        """
        with open(os.path.join(self.folder_list["epic"], "mos_out.txt"), "r") as f:
            lines = f.readlines()
        """

        # command.csh dosyasına bak
        self.mos1_ccds = (1, 1, 1, 0, 1, 1, 1)
        self.mos2_ccds = (1, 1, 1, 1, 1, 1, 1)
        self.pn_ccds = (1, 1, 1, 1)

    def set_prefixes(self):
        self.mos1_prefix = "1S001"
        self.mos2_prefix = "2S002"
        self.pn_prefix = "S003"

    def cheese(self):
        if len(glob.glob(os.path.join(self.folder_list["epic"], '*cheese*'))) < 3:
            args = ['cheese',
                    'prefixm=\'{} {}\''.format(self.mos1_prefix, self.mos2_prefix),
                    'prefixp={}'.format(self.pn_prefix),
                    'scale=0.5', 'rate=1.0', 'dist=40', 'clobber=0',
                    'elow=400', 'ehigh=7200']
            proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        else:
            print("*cheese* files already exist!")

    def mos1_spectra(self, region_file='reg.txt', mask=0):
        args = ['mos-spectra',
                'prefix={}'.format(self.mos1_prefix),
                'caldb={}'.format(os.environ['esas_caldb']),
                'region={}'.format(region_file),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'ccd1={} ccd2={} ccd3={} ccd4={} ccd5={} ccd6={} ccd7={}'.format(*self.mos1_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mos-back',
                'prefix={}'.format(self.mos1_prefix),
                'caldb={}'.format(os.environ['esas_caldb']),
                'diag=0',
                'elow=400', 'ehigh=7200',
                'ccd1={} ccd2={} ccd3={} ccd4={} ccd5={} ccd6={} ccd7={}'.format(*self.mos1_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['rot-im-det-sky',
                'prefix={}'.format(self.mos1_prefix),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'mode=1']
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

    def mos2_spectra(self, region_file='reg.txt', mask=0):
        args = ['mos-spectra',
                'prefix={}'.format(self.mos2_prefix),
                'caldb={}'.format(os.environ['esas_caldb']),
                'region={}'.format(region_file),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'ccd1={} ccd2={} ccd3={} ccd4={} ccd5={} ccd6={} ccd7={}'.format(*self.mos2_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mos-back',
                'prefix={}'.format(self.mos2_prefix),
                'caldb={}'.format(os.environ['esas_caldb']),
                'diag=0',
                'elow=400', 'ehigh=7200',
                'ccd1={} ccd2={} ccd3={} ccd4={} ccd5={} ccd6={} ccd7={}'.format(*self.mos2_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['rot-im-det-sky',
                'prefix={}'.format(self.mos2_prefix),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'mode=1']
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

    def pn_spectra(self, region_file='pn-reg.txt', mask=0):
        args = ['pn-spectra',
                'prefix={}'.format(self.pn_prefix),
                'caldb={}'.format(os.environ['esas_caldb']),
                'region={}'.format(region_file),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'pattern=4',
                'quad1={} quad2={} quad3={} quad4={}'.format(*self.pn_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['pn-back',
                'prefix={}'.format(self.pn_prefix),
                'caldb={}'.format(os.environ['esas_caldb']),
                'diag=0',
                'elow=400', 'ehigh=7200',
                'quad1={} quad2={} quad3={} quad4={}'.format(*self.pn_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['rot-im-det-sky',
                'prefix={}'.format(self.pn_prefix),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'mode=1']
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

