# -*- coding: utf-8 -*-
"""
OMFIT gEQDSK and IMAS
=====================
This example loads a gEQDSK file using the OMFITgeqdsk class.
The gEQKDS file is then save to IMAS and loaded back.

This example only works with python 2.7 since OMFIT is only Python 2.7 compatible

.. figure:: ../images/eq_omas_omfit.png
  :align: center
  :width: 75%
  :alt: OMFIT+OMAS facilitate save/load gEQDSK to/from IMAS
  :target: /.._images/eq_omas_omfit.png

"""

from __future__ import print_function, division, unicode_literals

import os

os.environ['OMAS_DEBUG_TOPIC'] = 'imas'

from omfit.classes.omfit_eqdsk import OMFITgeqdsk, OMFITsrc
from omas import *

# omas_rcparams['allow_fake_imas_fallback']=True

# read gEQDSK file in OMFIT
eq = OMFITgeqdsk(OMFITsrc + '/../samples/g133221.01000')

# convert gEQDSK to OMAS data structure
ods = eq.to_omas()

# save OMAS data structure to IMAS
paths = save_omas_imas(ods, machine='DIII-D', shot=133221, new=True)

# load OMAS data structure from IMAS
ods1 = load_omas_imas(machine='DIII-D', shot=133221, paths=paths)

# generate gEQDSK file from OMAS data structure
eq1 = OMFITgeqdsk('g133221.02000').from_omas(ods1)

# save gEQDSK file
eq1.deploy('g133221.02000')