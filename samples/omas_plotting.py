from __future__ import print_function, division, unicode_literals

from matplotlib.pyplot import show

import os

os.environ['OMAS_DEBUG_TOPIC'] = 'imas'

from omas import *

# ods = load_omas_s3('STEP_sample', user='omas_shared')
ods = load_omas_s3('OMFITprofiles_sample', user='omas_shared')

ods.consistency_check = False
ods.physics_core_profiles_pressures()
ods.plot_core_profiles_pressures()
show()

ods.plot_core_profiles_summary()
show()

omas_plot.equilibrium_summary(ods, linewidth=1, label='my label')
show()
