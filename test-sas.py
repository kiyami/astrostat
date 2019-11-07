from data_analysis import xmm_sas

# A2667
# initial parameters
object_name = "A2667"
obs_id = "0148990101"
odf_path = "/Users/kym/PycharmProjects/astrostat/data/A2667/0148990101/ODF"

obs1 = xmm_sas.Observation(object_name, obs_id, odf_path)
obs1.get_info()

def initialise_new_data(obs):
    obs.cifbuild()
    obs.odfingest()
    obs.chain()
    obs.set_folders()
    obs.copy_events()

def initialise_existing_data(obs):
    obs.cifbuild()
    obs.odfingest()
    obs.set_folders()

def create_image(obs, camera='mos1', evt_file='mos1.fits', out_file='m1_image_all.fits', emin=300, emax=10000):
    obs.create_image(camera=camera, evt_file=evt_file, out_file=out_file, emin=emin, emax=emax)

def ltc_filt(obs, camera='mos1', evt_file='mos1.fits'):
    obs.espfilt(camera=camera, evt_file=evt_file)

def source_detection(obs, camera='mos1', evt_file='mos1_filt.fits'):
    obs.edetectchain(camera=camera, evt_file=evt_file)

initialise_existing_data(obs=obs1)

#create_image(obs1, camera='mos1', evt_file='mos1.fits', out_file='', emin=300, emax=10000)
#create_image(obs1, camera='mos2', evt_file='mos2.fits', out_file='', emin=300, emax=10000)
#create_image(obs1, camera='pn', evt_file='pn.fits', out_file='', emin=300, emax=10000)

ltc_filt(obs1, camera='mos1', evt_file='mos1.fits')
ltc_filt(obs1, camera='mos2', evt_file='mos2.fits')
ltc_filt(obs1, camera='pn', evt_file='pn.fits')

source_detection(obs1, camera='mos1', evt_file='mos1_filt.fits')
source_detection(obs1, camera='mos2', evt_file='mos2_filt.fits')
source_detection(obs1, camera='pn', evt_file='pn_filt.fits')
