from omfit.classes.omfit_eqdsk import OMFITeqdsk
from omas import *
import os

#set OMAS debugging topic
os.environ['OMAS_DEBUG_TOPIC']='imas'

#read gEQDSK file in OMFIT
eq=OMFITgeqdsk('133221.01000')

#convert gEQDSK to OMAS data structure
ods=eq.to_omas()

# save OMAS data structure to IMAS
user = os.environ['USER']
tokamak = 'ITER'
imas_version = os.environ.get('IMAS_VERSION','3.10.1')
shot = 1
run = 0
new = True
paths = save_omas_imas(ods, user, tokamak, imas_version,
                       shot, run, new)

# load IMAS to OMAS data structure
ods1 = load_omas_imas(user, tokamak, imas_version, shot,
                      run, paths)

#read from OMAS data structure
eq1=OMFITgeqdsk('133221.02000').from_omas(ods1)

#save gEQDSK file
eq1.deploy()
