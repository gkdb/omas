from __future__ import print_function, division, unicode_literals

from .omas_utils import *

__all__ = []

def add_to__ODS__(f):
    __all__.append(f.__name__)
    return f

# constants class that mimics scipy.constants
class constants(object):
    e = 1.6021766208e-19


@add_to__ODS__
def core_profiles_pressures(ods, update=True):
    '''
    calculates individual ions pressures
        `core_profiles.profiles_1d.:.ion.:.pressure_thermal` #Pressure (thermal) associated with random motion ~average((v-average(v))^2)
        `core_profiles.profiles_1d.:.ion.:.pressure`         #Pressure (thermal+non-thermal)

    as well as total pressures

        `core_profiles.profiles_1d.:.pressure_thermal`       #Thermal pressure (electrons+ions)
        `core_profiles.profiles_1d.:.pressure_ion_total`     #Total (sum over ion species) thermal ion pressure
        `core_profiles.profiles_1d.:.pressure_perpendicular` #Total perpendicular pressure (electrons+ions, thermal+non-thermal)
        `core_profiles.profiles_1d.:.pressure_parallel`      #Total parallel pressure (electrons+ions, thermal+non-thermal)

    NOTE: the fast particles ion pressures are read, not set by this function:
        `core_profiles.profiles_1d.:.ion.:.pressure_fast_parallel`      #Pressure (thermal) associated with random motion ~average((v-average(v))^2)
        `core_profiles.profiles_1d.:.ion.:.pressure_fast_perpendicular` #Pressure (thermal+non-thermal)

    :param ods: input ods

    :param update: operate in place

    :return: updated ods
    '''
    ods_p = ods
    if not update:
        from omas import ODS
        ods_p = ODS().copy_attrs_from(ods)

    for time_index in ods['core_profiles']['profiles_1d']:
        prof1d = ods['core_profiles']['profiles_1d'][time_index]
        prof1d_p = ods_p['core_profiles']['profiles_1d'][time_index]
        __p__ = prof1d['electrons']['density'] * prof1d['electrons']['temperature'] * constants.e
        prof1d_p['pressure_thermal'] = __p__
        prof1d_p['pressure_ion_total'] = __p__ * 0.0
        prof1d_p['pressure_perpendicular'] = __p__ / 3.
        prof1d_p['pressure_parallel'] = __p__ / 3.
        for k in range(len(prof1d['ion'])):
            prof1d_p['ion'][k]['pressure'] = __p__ * 0.0
            for therm_fast, density in [('therm', 'density'), ('fast', 'density_fast')]:
                if (len(prof1d['ion']) and density in prof1d['ion'][k] and numpy.sum(
                        numpy.abs(prof1d['ion'][k][density])) > 0):
                    if therm_fast == 'therm':
                        __p__ = prof1d['ion'][k]['density'] * prof1d['ion'][k]['temperature'] * constants.e
                        prof1d_p['ion'][k]['pressure_thermal'] = __p__
                        prof1d_p['pressure_ion_total'] += __p__
                        prof1d_p['pressure_thermal'] += __p__
                        prof1d_p['pressure_perpendicular'] += __p__ / 3.
                        prof1d_p['pressure_parallel'] += __p__ / 3.
                    else:
                        if not update:
                            prof1d_p['ion'][k]['pressure_fast_perpendicular'] = prof1d['ion'][k][
                                'pressure_fast_perpendicular']
                            prof1d_p['ion'][k]['pressure_fast_parallel'] = prof1d['ion'][k]['pressure_fast_parallel']
                        prof1d_p['pressure_perpendicular'] += prof1d['ion'][k]['pressure_fast_perpendicular']
                        prof1d_p['pressure_parallel'] += prof1d['ion'][k]['pressure_fast_parallel']
                        __p__ = prof1d_p['ion'][k]['pressure_fast_perpendicular'] * 2 + prof1d_p['ion'][k]['pressure_fast_parallel']
                    prof1d_p['ion'][k]['pressure'] += __p__

        #extra pressure information that is not within IMAS structure is set only if consistency_check is not True
        if ods_p.consistency_check is not True:
            prof1d_p['pressure'] = prof1d_p['pressure_perpendicular'] * 2 + prof1d_p['pressure_parallel']
            prof1d_p['pressure_electron_total'] = prof1d_p['pressure_thermal'] - prof1d_p['pressure_ion_total']
            prof1d_p['pressure_fast'] = prof1d_p['pressure'] - prof1d_p['pressure_thermal']

    return ods_p


def define_cocos(cocos_ind):
    """
    Returns dictionary with COCOS coefficients given a COCOS index

    https://docs.google.com/document/d/1-efimTbI55SjxL_yE_GKSmV4GEvdzai7mAj5UYLLUXw/edit

    :param cocos_ind: COCOS index

    :return: dictionary with COCOS coefficients
    """

    cocos=dict.fromkeys(['sigma_Bp', 'sigma_RpZ', 'sigma_rhotp', 'sign_q_pos', 'sign_pprime_pos', 'exp_Bp'])

    # all multipliers shouldn't change input values if cocos_ind is None
    if cocos_ind is None:
        cocos['exp_Bp']          = 0
        cocos['sigma_Bp']        = +1
        cocos['sigma_RpZ']       = +1
        cocos['sigma_rhotp']     = +1
        cocos['sign_q_pos']      = 0
        cocos['sign_pprime_pos'] = 0
        return cocos

    # if COCOS>=10, this should be 1
    cocos['exp_Bp'] = 0
    if cocos_ind>=10:
        cocos['exp_Bp'] = +1

    if cocos_ind in [1,11]:
        # These cocos are for
        # (1)  psitbx(various options), Toray-GA
        # (11) ITER, Boozer
        cocos['sigma_Bp']        = +1
        cocos['sigma_RpZ']       = +1
        cocos['sigma_rhotp']     = +1
        cocos['sign_q_pos']      = +1
        cocos['sign_pprime_pos'] = -1

    elif cocos_ind in [2,12,-12]:
        # These cocos are for
        # (2)  CHEASE, ONETWO, HintonHazeltine, LION, XTOR, MEUDAS, MARS, MARS-F
        # (12) GENE
        # (-12) ASTRA
        cocos['sigma_Bp']        = +1
        cocos['sigma_RpZ']       = -1
        cocos['sigma_rhotp']     = +1
        cocos['sign_q_pos']      = +1
        cocos['sign_pprime_pos'] = -1

    elif cocos_ind in [3,13]:
        # These cocos are for
        # (3) Freidberg*, CAXE and KINX*, GRAY, CQL3D^, CarMa, EFIT* with : ORB5, GBSwith : GT5D
        # (13) 	CLISTE, EQUAL, GEC, HELENA, EU ITM-TF up to end of 2011
        cocos['sigma_Bp']        = -1
        cocos['sigma_RpZ']       = +1
        cocos['sigma_rhotp']     = -1
        cocos['sign_q_pos']      = -1
        cocos['sign_pprime_pos'] = +1

    elif cocos_ind in [4,14]:
        #These cocos are for
        cocos['sigma_Bp']        = -1
        cocos['sigma_RpZ']       = -1
        cocos['sigma_rhotp']     = -1
        cocos['sign_q_pos']      = -1
        cocos['sign_pprime_pos'] = +1

    elif cocos_ind in [5,15]:
        # These cocos are for
        # (5) TORBEAM, GENRAY^
        cocos['sigma_Bp']        = +1
        cocos['sigma_RpZ']       = +1
        cocos['sigma_rhotp']     = -1
        cocos['sign_q_pos']      = -1
        cocos['sign_pprime_pos'] = -1

    elif cocos_ind in [6,16]:
        #These cocos are for
        cocos['sigma_Bp']        = +1
        cocos['sigma_RpZ']       = -1
        cocos['sigma_rhotp']     = -1
        cocos['sign_q_pos']      = -1
        cocos['sign_pprime_pos'] = -1

    elif cocos_ind in [7,17]:
        #These cocos are for
        # (17) LIUQE*, psitbx(TCV standard output)
        cocos['sigma_Bp']        = -1
        cocos['sigma_RpZ']       = +1
        cocos['sigma_rhotp']     = +1
        cocos['sign_q_pos']      = +1
        cocos['sign_pprime_pos'] = +1

    elif cocos_ind in [8,18]:
        #These cocos are for
        cocos['sigma_Bp']        = -1
        cocos['sigma_RpZ']       = -1
        cocos['sigma_rhotp']     = +1
        cocos['sign_q_pos']      = +1
        cocos['sign_pprime_pos'] = +1

    return cocos


def cocos_transform(cocosin_index, cocosout_index):
    """
    Returns a dictionary with coefficients for how various quantities should get multiplied in order to go from cocosin_index to cocosout_index

    https://docs.google.com/document/d/1-efimTbI55SjxL_yE_GKSmV4GEvdzai7mAj5UYLLUXw/edit

    :param cocosin_index: COCOS index in

    :param cocosout_index: COCOS index out

    :return: dictionary with transformation multipliers
    """

    # Don't transform if either cocos is undefined
    if (cocosin_index is None) or (cocosout_index is None):
        printd("No COCOS tranformation for "+str(cocosin_index)+" to "+str(cocosout_index),topic='cocos')
        sigma_Ip_eff    = 1
        sigma_B0_eff    = 1
        sigma_Bp_eff    = 1
        exp_Bp_eff      = 0
        sigma_rhotp_eff = 1
    else:
        printd("COCOS tranformation from "+str(cocosin_index)+" to "+str(cocosout_index),topic='cocos')
        cocosin = define_cocos(cocosin_index)
        cocosout = define_cocos(cocosout_index)

        sigma_Ip_eff    = cocosin['sigma_RpZ'] * cocosout['sigma_RpZ']
        sigma_B0_eff    = cocosin['sigma_RpZ'] * cocosout['sigma_RpZ']
        sigma_Bp_eff    = cocosin['sigma_Bp'] * cocosout['sigma_Bp']
        exp_Bp_eff      = cocosout['exp_Bp'] - cocosin['exp_Bp']
        sigma_rhotp_eff = cocosin['sigma_rhotp'] * cocosout['sigma_rhotp']

    # Transform
    transforms = {}
    transforms['1/PSI'] = sigma_Ip_eff * sigma_Bp_eff / (2 * numpy.pi) ** exp_Bp_eff
    transforms['invPSI'] = transforms['1/PSI']
    transforms['dPSI'] = transforms['1/PSI']
    transforms['F_FPRIME'] = transforms['dPSI']
    transforms['PPRIME'] = transforms['dPSI']
    transforms['PSI'] = sigma_Ip_eff * sigma_Bp_eff * (2 * numpy.pi) ** exp_Bp_eff
    transforms['Q'] = sigma_Ip_eff * sigma_B0_eff * sigma_rhotp_eff
    transforms['TOR'] = sigma_B0_eff
    transforms['BT'] = transforms['TOR']
    transforms['IP'] = transforms['TOR']
    transforms['F'] = transforms['TOR']
    transforms['POL'] = sigma_B0_eff * sigma_rhotp_eff
    transforms['BP'] = transforms['POL']

    printd(transforms,topic='cocos')

    return transforms


@contextmanager
def cocos_environment(ods, cocosin=None, cocosout=None):
    '''
    Provides OMAS environment within wich a certain COCOS convention is defined

    :param ods: ODS on which to operate

    :param cocosin: input COCOS convention

    :param cocosout: output COCOS convention

    :return: ODS with COCOS convention set
    '''
    old_cocosin = ods.cocosin
    old_cocosout = ods.cocosout
    if cocosin is not None:
        ods.cocosin = cocosin
    if cocosout is not None:
        ods.cocosout = cocosout
    try:
        yield ods
    finally:
        ods.cocosin = old_cocosin
        ods.cocosout = old_cocosout



def generate_cocos_signals(structures, threshold=0):
    '''
    This is a utility function for printing the cocos_signals entries as the ones defined in omas/omas_physics.py
    The printed text must be copied to omas/omas_physics.py and the COCOS transformations assigned by hand.
    '''
    # units of entries currently in cocos_singals
    cocos_units = []
    for item in cocos_signals:
        units = omas_info_node(item)['units']
        if units not in cocos_units:
            cocos_units.append(units)

    if isinstance(structures, basestring):
        structures = [structures]
    structures += cocos_structures
    structures = numpy.unique(structures)

    from .omas_utils import _structures
    from .omas_utils import i2o
    from .omas_core import ODS
    ods = ODS()
    out = {}
    text=['cocos_signals = {}']
    for structure in structures:
        text.extend(['','# '+structure.upper()])
        out[structure] = {}
        ods[structure]
        d = dict_structures(imas_version=default_imas_version)
        m = 0
        for item in sorted(list(list(_structures[d[structure]].keys()))):
            item=i2o(item)
            m=max(m,len(item))
            score = 0
            rationale = []
            if item.startswith(structure) and '_error_' not in item:
                entry = "cocos_signals['%s']=" % i2o(item)
                info = omas_info_node(item)
                units = info.get('units', None)
                data_type = info.get('data_type', None)
                if data_type in ['structure','STR_0D','struct_array']:
                    continue
                elif units in [None,'s']:
                    out[structure].setdefault(-1, []).append((item,'[%s]'%units))
                    continue
                elif any([item.endswith(k) for k in ['chi_squared','standard_deviation','weight','coefficients','.r','.z']]):
                    out[structure].setdefault(-1, []).append((item,p2l(item)[-1]))
                    continue
                n=item.count(separator)
                for pnt,key in enumerate(p2l(item)):
                    pnt=float(pnt)/n
                    for k in ['q','ip','b0','phi','psi','f_df']:
                        if key==k:
                            rationale += [k]
                            score += pnt
                            break
                    for k in ['q','j','phi','psi','ip','b','f','v','f_df']:
                        if key.startswith('%s_'%k):
                            rationale += [k]
                            score += pnt
                            break
                    for k in ['velocity','current','b_field','e_field','torque','momentum']:
                        if k in key and key not in ['heating_current_drive']:
                            rationale += [k]
                            score += pnt
                            break
                    for k in ['_dpsi']:
                        if k in key and k+'_norm' not in key:
                            rationale += [k]
                            score += pnt
                            break
                    for k in ['poloidal','toroidal','parallel','_tor','_pol','_par','tor_','pol_','par_']:
                        if key.endswith(k) or key.startswith(k) and key not in ['beta_pol','beta_pol']:
                            rationale += [k]
                            score += pnt
                            break
                if units in cocos_units:
                    if len(rationale):
                        rationale += ['[%s]'%units]
                        score += 1
                out[structure].setdefault(score, []).append((item,'  '.join(rationale)))
        for score in reversed(sorted(out[structure])):
            if score>threshold or item in cocos_signals:
                for item,rationale in out[structure][score]:
                    attention='# <--> '
                    if item in cocos_signals:
                        attention='       '
                    text.append(("cocos_signals['%s']='%s'" %(item,cocos_signals.get(item,'?'))).ljust(m+20)+attention+'# %3.3f # %s'%(score,rationale))

        print('\n'.join(text))
    return out

# cocos_signals contains the IMAS locations and the corresponding `cocos_transform` function
from .omas_cocos import cocos_signals

# cocos_structures contains the list of all the IDSs that have been checked for COCOS convention transformations
cocos_structures = ['summary','wall', 'info']
for item in cocos_signals:
    structure_name = item.split(separator)[0]
    if structure_name not in cocos_structures:
        cocos_structures.append(structure_name)