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

    def create_image(self, camera='mos1', evt_file='mos1.fits', out_file='', emin=300, emax=10000):
        if (camera == 'mos1') or (camera == 'mos2'):
            expression = "#XMMEA_EM&&(PI in [{}:{}])&&(PATTERN in [0:12])&&(FLAG==0)".format(emin, emax)
        else:
            expression = "#XMMEA_EP&&(PI in [{}:{}])&&(PATTERN==0)".format(emin, emax)

        if not out_file:
            out_file = "{}_image_{}_{}.fits".format(camera, emin, emax)

        path = self.folder_list[camera]

        args = ["evselect",
                "table={}".format(evt_file),
                "imagebinning=binSize",
                "withimageset=yes",
                "imageset={}".format(out_file),
                "xcolumn=X",
                "ycolumn=Y",
                "ximagebinsize=40",
                "yimagebinsize=40",
                "expression={}".format(expression)]
        proc = subprocess.Popen(args, cwd=path, env=self.envvars).wait()

    def espfilt(self, camera='mos1', evt_file='mos1.fits'):
        path = self.folder_list[camera]

        objevlifilt = glob.glob(os.path.join(path, "*objevlifilt.FIT"))
        filt_evt = glob.glob(os.path.join(path, "*filt.fits"))

        if len(filt_evt) == 0:
            if len(objevlifilt) == 0:
                args = ["espfilt",
                        "eventset={}".format(evt_file)]
                proc = subprocess.Popen(args, cwd=path, env=self.envvars).wait()
                objevlifilt = glob.glob(os.path.join(path, "*objevlifilt.FIT"))

            args = ["mv",
                    "{}".format(objevlifilt[0]),
                    "{}_filt.fits".format(camera)]
            proc = subprocess.Popen(args, cwd=path, env=self.envvars).wait()
        else:
            print("Light curve filtered event file already exist..")
            print("filt_evt: {}".format(os.path.basename(filt_evt[0])))

    def edetectchain(self, camera='mos1', evt_file='mos1_filt.fits'):
        path = self.folder_list[camera]

        atthk = glob.glob(os.path.join(path, "*atthk*"))
        emllist = glob.glob(os.path.join(path, "*emllist*"))
        srclist = glob.glob(os.path.join(path, "*srclist*"))

        if len(atthk) == 0:
            atthk = glob.glob(os.path.join(self.folder_list["epic"], "*atthk*"))
            copy(atthk[0], path)
            print("{} file copied to the working directory..".format(os.path.basename(atthk[0])))
        else:
            print("{} file exist..".format(os.path.basename(atthk[0])))

        if len(emllist) == 0:
            pimin_list = [200, 500, 1000, 2000, 4500]
            pimax_list = [500, 1000, 2000, 4500, 12000]
            band_names = ['b1', 'b2', 'b3', 'b4', 'b5']
            image_names = []

            for i in range(len(pimin_list)):
                out_file = '{}_image_{}.fits'.format(camera, band_names[i])
                if len(glob.glob(os.path.join(path, out_file))) == 0:
                    self.create_image(camera=camera, evt_file=evt_file, out_file=out_file, emin=pimin_list[i], emax=pimax_list[i])
                else:
                    print("{} already exist..".format(out_file))
                image_names.append(out_file)

            imagesets = '"{}" "{}" "{}" "{}" "{}"'.format(*image_names)

            pimin = "{} {} {} {} {}".format(*pimin_list)
            pimax = "{} {} {} {} {}".format(*pimax_list)

            print(pimin, pimax)


            args = ["edetect_chain",
                    "imagesets={}".format(imagesets),
                    "eventsets={}".format(evt_file),
                    "attitudeset={}".format(atthk[0]),
                    "pimin={} {} {} {} {}".format(*pimin_list),
                    "pimax={} {} {} {} {}".format(*pimax_list),
                    "ecf=1.734 1.746 2.041 0.737 0.145",
                    "eboxl_list={}_eboxlist_l.fits".format(camera),
                    "eboxm_list={}_eboxlist_m.fits".format(camera),
                    "esp_nsplinenodes=16",
                    "eml_list={}_emllist.fits".format(camera),
                    "esen_mlmin=15"]
            proc = subprocess.Popen(args, cwd=path, env=self.envvars).wait()
        else:
            print("{} already exist..".format(os.path.basename(emllist[0])))

        if len(srclist) == 0:
            args = ["srcmatch",
                    "inputlistsets={}".format('{}_emllist.fits'.format(camera)),
                    "outputlistset={}".format('{}_srclist.fits'.format(camera)),
                    "htmloutput={}".format('{}_srclist.html'.format(camera))]
            proc = subprocess.Popen(args, cwd=path, env=self.envvars).wait()
        else:
            print("{} already exist..".format(os.path.basename(srclist[0])))

    def filter_point_sources(self):
        pass

    def extract_spectrum(self):
        pass
