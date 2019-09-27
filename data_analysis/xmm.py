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

        self.esas_caldb = os.path.abspath(os.path.join(Observation.sas_ccfpath, 'esas'))
        self.envvars['esas_caldb'] = self.esas_caldb


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
                            "regions": os.path.abspath(os.path.join(self.ODF_path, "../epic/regions")),
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
                'caldb={}'.format(self.envvars['esas_caldb']),
                'region={}/{}'.format("regions", region_file),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'ccd1={} ccd2={} ccd3={} ccd4={} ccd5={} ccd6={} ccd7={}'.format(*self.mos1_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mos_back',
                'prefix={}'.format(self.mos1_prefix),
                'caldb={}'.format(self.envvars['esas_caldb']),
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
                'caldb={}'.format(self.envvars['esas_caldb']),
                'region={}/{}'.format("regions", region_file),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'ccd1={} ccd2={} ccd3={} ccd4={} ccd5={} ccd6={} ccd7={}'.format(*self.mos2_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mos_back',
                'prefix={}'.format(self.mos2_prefix),
                'caldb={}'.format(self.envvars['esas_caldb']),
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
                'caldb={}'.format(self.envvars['esas_caldb']),
                'region={}/{}'.format("regions", region_file),
                'mask={}'.format(mask),
                'elow=400', 'ehigh=7200',
                'pattern=4',
                'quad1={} quad2={} quad3={} quad4={}'.format(*self.pn_ccds)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['pn_back',
                'prefix={}'.format(self.pn_prefix),
                'caldb={}'.format(self.envvars['esas_caldb']),
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

    def comb_image(self, mask=0, mos1=True, mos2=True, pn=True):
        prefixlist = ""
        if mos1:
            prefixlist = " ".join([prefixlist, self.mos1_prefix])
        if mos2:
            prefixlist.join(self.mos2_prefix)
        if pn:
            prefixlist.join(self.pn_prefix)
        prefixlist = prefixlist.strip()

        args = ['comb',
                'prefixlist="{}"'.format(prefixlist),
                'caldb={}'.format(self.envvars['esas_caldb']),
                'withpartcontrol=1',
                'withsoftcontrol=0',
                'withswcxcontrol=0',
                'mask={}'.format(mask),
                'elowlist=400', 'ehighlist=7200']
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['adapt',
                'smoothingcounts=50',
                'thresholdmasking=0.02',
                'detector=0',
                'binning=2',
                'withpartcontrol=1',
                'withsoftcontrol=0',
                'withswcxcontrol=0',
                'elow=400', 'ehigh=7200']
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        if mask:
            args = ['mv', 'adapt-400-7200.fits', 'adapt-400-7200-nps.fits']
        else:
            args = ['mv', 'adapt-400-7200.fits', 'adapt-400-7200-ps.fits']
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

    def set_detx_dety(self):
        self.mos1_detx = 134
        self.mos1_dety = -219

        self.mos2_detx = 6
        self.mos2_dety = -93

        self.pn_detx = 59
        self.pn_dety = -10

    def create_region_file(self, inner_radius, outer_radius):
        inner_radius_phy = float(inner_radius) * 20.0
        outer_radius_phy = float(outer_radius) * 20.0

        mos1_text = "&&((DETX,DETY) IN circle({0},{1},{2}))&&!((DETX,DETY) IN circle({0},{1},{3}))".format(self.mos1_detx,
                                                                                                           self.mos1_dety,
                                                                                                           outer_radius_phy,
                                                                                                           inner_radius_phy)
        mos1_file_name = "reg1-{}-{}.txt".format(int(inner_radius), int(outer_radius))

        with open(os.path.join(self.folder_list["regions"],mos1_file_name), "w") as f:
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

    def rename_spectra_output(self, inner_radius, outer_radius):
        name = "{}-{}".format(inner_radius, outer_radius)

        args = ['mv', 'mos{}-obj.pi'.format(self.mos1_prefix), 'mos{}-obj-{}.pi'.format(self.mos1_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}-back.pi'.format(self.mos1_prefix), 'mos{}-back-{}.pi'.format(self.mos1_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}.rmf'.format(self.mos1_prefix), 'mos{}-{}.rmf'.format(self.mos1_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}.arf'.format(self.mos1_prefix), 'mos{}-{}.arf'.format(self.mos1_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}-obj-im-sp-det.fits'.format(self.mos1_prefix),
                'mos{}-sp-{}.fits'.format(self.mos1_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()



        args = ['mv', 'mos{}-obj.pi'.format(self.mos2_prefix), 'mos{}-obj-{}.pi'.format(self.mos2_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}-back.pi'.format(self.mos2_prefix), 'mos{}-back-{}.pi'.format(self.mos2_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}.rmf'.format(self.mos2_prefix), 'mos{}-{}.rmf'.format(self.mos2_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}.arf'.format(self.mos2_prefix), 'mos{}-{}.arf'.format(self.mos2_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'mos{}-obj-im-sp-det.fits'.format(self.mos2_prefix),
                'mos{}-sp-{}.fits'.format(self.mos2_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()



        args = ['mv', 'pn{}-obj.pi'.format(self.pn_prefix), 'pn{}-obj-{}.pi'.format(self.pn_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'pn{}-back.pi'.format(self.pn_prefix), 'pn{}-back-{}.pi'.format(self.pn_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'pn{}.rmf'.format(self.pn_prefix), 'pn{}-{}.rmf'.format(self.pn_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'pn{}.arf'.format(self.pn_prefix), 'pn{}-{}.arf'.format(self.pn_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

        args = ['mv', 'pn{}-obj-im-sp-det.fits'.format(self.pn_prefix),
                'pn{}-sp-{}.fits'.format(self.pn_prefix, name)]
        proc = subprocess.Popen(args, cwd=self.folder_list["epic"], env=self.envvars).wait()

    def grppha_mos1(self, bin_value=20):
        pass

    def grppha_mos2(self, bin_value=20):
        pass

    def grppha_pn(self, bin_value=20):
        pass