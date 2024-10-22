import astropy.units as u
from yaml import load, dump
from ast import literal_eval

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

'''
Code in this file is taken straight from the chemcomp files. (https://github.com/AaronDavidSchneider/chemcomp)
File is originally located in /chemcomp/chemcomp/helpers/import_config.py
Full credit to Aaron David Schneider & Betram Bitsch.
'''


def import_config(config_file):
    """Wrapper that imports the config."""
    stream = open(config_file, "r")
    config = load(stream, Loader=Loader)

    scale_units(config)

    return config


def scale(dictionary, quantity, unit=1):
    """Helper function to scale dictionary without units.
    Original chemcomp code contains units but they have been removed for
    purposes of taking logs of values."""
    if dictionary is not None:
        if isinstance(dictionary, list):
            for item in dictionary:
                temp = item.get(quantity, None)
                if temp is not None:
                    item[quantity] = (float(temp) * unit).to_value()
        else:
            temp = dictionary.get(quantity, None)
            if temp is not None:
                dictionary[quantity] = (float(temp) * unit).to_value()


def scale_units(config):
    """Add a unit to all unit based quantities from the configuration file."""
    planets = config.get("config_planet", None)
    scale(planets, "M_c", u.earthMass)
    scale(planets, "M_a", u.earthMass)
    scale(planets, "a_p", u.au)
    scale(planets, "t_0", u.Myr)
    scale(planets, "r_p", u.jupiterRad)
    scale(planets, "rho_c", u.g / (u.cm**3))
    scale(planets, "rho_0", u.g / (u.cm**3))
    scale(planets, "dt", u.yr)
    scale(planets, "M_end", u.jupiterMass)
    scale(planets, "r_in", u.au)

    disk = config.get("config_disk", None)
    scale(disk, "M_STAR", u.M_sun)
    scale(disk, "M_DOT_0", u.M_sun / u.yr)
    scale(disk, "M0", u.M_sun)
    scale(disk, "R0", u.au)
    scale(disk, "time", u.Myr)
    scale(disk, "SIGMA_0", u.g / (u.cm**2))
    scale(disk, "a_0", u.cm)
    scale(disk, "FUV_MDOT", u.M_sun / u.yr)
    scale(disk, "tau_disk", u.yr)
    scale(disk, "begin_photoevap", u.Myr)
    scale(disk, "evap_width", u.au)

    pebble_accretion = config.get("config_pebble_accretion", None)
    scale(pebble_accretion, "M_DOT_P", u.earthMass / (u.Myr))
    scale(pebble_accretion, "R_peb", u.cm)
    scale(pebble_accretion, "rho_solid", u.g / (u.cm**3))
    scale(pebble_accretion, "u_frag", u.m / u.s)

    gas_accretion = config.get("config_gas_accretion", None)
    scale(gas_accretion, "kappa_env", u.cm**2 / u.g)

    defaults = config.get("defaults", None)
    scale(defaults, "DEF_R_IN", u.au)
    scale(defaults, "DEF_R_OUT", u.au)
    scale(defaults, "DEF_TIMESTEP", u.yr)
    scale(defaults, "DEF_T_END", u.Myr)

    output = config.get("output", None)
    scale(output, "save_interval", u.yr)


def eval_kwargs(inp):
    '''
    Code for this function is taken straight from the chemcomp files. (https://github.com/AaronDavidSchneider/chemcomp)
    File is originally located in /chemcomp/chemcomp/helpers/__init__.py
    Full credit to Aaron David Schneider & Betram Bitsch.
    '''
    try:
        if isinstance(inp, str):
            return literal_eval(inp)
        else:
            return inp
    except ValueError:
        return inp