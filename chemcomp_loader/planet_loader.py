import numpy as np
import tables
from tables.exceptions import NoSuchNodeError
import astropy.units as u
from .import_config import import_config, eval_kwargs
from .chemistry_properties import *


AU = (1*u.au).cgs.value  # define the astronomical unit conversion from cgs
Myr = (1*u.Myr).cgs.value  # define the Megayear unit conversion from cgs


class Planet_class:
    '''
    Class object that stores all the planet data.

    Parameters can be accessed via class attributes, e.g:
        Planet      = Planet_class('simulation.h5', 'config.yaml')
        core_mass   = Planet.M_c         # Retrieves core mass of the planet
        core_Fe     = Planet.core.Fe     # Retrieves Fe mass in the core
        atmo_H      = Planet.atmo.H      # Retrieves H mass in the atmosphere
    '''

    def __init__(self, file_path, config_file_path):
        self.load_planet(file_path)
        self.load_parameters_from_config(config_file_path)
        self.atmo = Planet_atmo(self)
        self.core = Planet_core(self)

    def load_planet(self, file_path):
        '''
        Function that loads the planet from the .h5 file produced by chemcomp simulations.
        Saves each planet parameter in a class attribute.

        NOTE:
            self.a_p is rescaled from cgs to AU.
            self.t is rescaled from cgs to Myr.

        Inputs:
            file_path : path to the .h5 file relative to the current folder. Includes the .h5 file
        '''

        with tables.open_file(file_path, mode='r') as f:
            self.disc_quantities = [q for q in dir(f.get_node('/planet')) if q[0]!='_']

            self.M                  = np.array(f.root.planet.M)
            self.M_a                = np.array(f.root.planet.M_a)
            self.M_c                = np.array(f.root.planet.M_c)
            self.M_z_gas            = np.array(f.root.planet.M_z_gas)
            self.M_z_peb            = np.array(f.root.planet.M_z_peb)
            self.T                  = np.array(f.root.planet.T)
            self.a_p                = np.array(f.root.planet.a_p) / AU
            self.comp_a             = np.array(f.root.planet.comp_a)
            self.comp_c             = np.array(f.root.planet.comp_c)
            self.fSigma             = np.array(f.root.planet.fSigma)
            self.gamma_norm         = np.array(f.root.planet.gamma_norm)
            self.gamma_tot          = np.array(f.root.planet.gamma_tot)
            self.m_dot_a_chem_gas   = np.array(f.root.planet.m_dot_a_chem_gas)
            self.m_dot_a_chem_peb   = np.array(f.root.planet.m_dot_a_chem_peb)
            self.m_dot_a_gas        = np.array(f.root.planet.m_dot_a_gas)
            self.m_dot_a_peb        = np.array(f.root.planet.m_dot_a_peb)
            self.m_dot_c_chem_gas   = np.array(f.root.planet.m_dot_c_chem_gas)
            self.m_dot_c_chem_peb   = np.array(f.root.planet.m_dot_c_chem_peb)
            self.m_dot_c_gas        = np.array(f.root.planet.m_dot_c_gas)
            self.m_dot_c_peb        = np.array(f.root.planet.m_dot_c_peb)
            self.m_dot_gas          = np.array(f.root.planet.m_dot_gas)
            self.m_dot_peb          = np.array(f.root.planet.m_dot_peb)
            self.peb_iso            = np.array(f.root.planet.peb_iso)
            self.pebble_flux        = np.array(f.root.planet.pebble_flux)
            self.regime_gas         = np.array(f.root.planet.regime_gas)
            self.regime_peb         = np.array(f.root.planet.regime_peb)
            self.sigma_g            = np.array(f.root.planet.sigma_g)
            self.sigma_peb          = np.array(f.root.planet.sigma_peb)
            self.t                  = np.array(f.root.planet.t) / Myr
            self.tau_m              = np.array(f.root.planet.tau_m)
            self.units              = np.array(f.root.planet.units)

    def load_parameters_from_config(self, config_file_path):
        '''
        Function that loads the planet parameters from the config file.
        '''

        config = import_config(config_file_path)
        config_disk = config.get("config_planet", {})
        config_planetesimal_accretion = config.get("config_planetesimal_accretion", {})

        self.matter_removal         = eval_kwargs(config_disk.get('matter_removal', None))
        self.use_heat_torque        = eval_kwargs(config_disk.get('use_heat_torque', None))
        self.use_dynamical_torque   = eval_kwargs(config_disk.get('use_dynamical_torque', None))
        self.migration              = eval_kwargs(config_disk.get('migration', None))
        self.M0_fact                = eval_kwargs(config_disk.get('M0_fact', None))
        self.a_p                    = eval_kwargs(config_disk.get('a_p', None))
        self.t_0                    = eval_kwargs(config_disk.get('t_0', None))
        self.rho_c                  = eval_kwargs(config_disk.get('rho_c', None))
        self.r_in                   = eval_kwargs(config_disk.get('r_in', None))
        self.keep_peb_iso           = eval_kwargs(config_disk.get('keep_peb_iso', None))
        self.use_pebiso_diffusion   = eval_kwargs(config_disk.get('use_pebiso_diffusion', None))
        self.R_pla                  = eval_kwargs(config_planetesimal_accretion.get('R_pla', None))
        self.rho_pla                = eval_kwargs(config_planetesimal_accretion.get('rho_pla', None))

    def print_attributes(self):
        '''
        Function that prints the attributes of the Planet class.
        '''

        [print(attribute) for attribute in dir(self) if attribute[0:2] != '__']


class Planet_atmo:
    def __init__(self, super):
        # Elements
        for element, atmo_component in zip(element_array,
                                          super.comp_a[:, 0].swapaxes(0, 1)):
            setattr(self, element, atmo_component)

        # Molecules
        for molecule, atmo_component in zip(molecule_array,
                                           super.comp_a[:, 1].swapaxes(0, 1)):
            setattr(self, molecule, atmo_component)


class Planet_core:
    def __init__(self, super):
        # Elements
        for element, core_component in zip(element_array,
                                          super.comp_c[:, 0].swapaxes(0, 1)):
            setattr(self, element, core_component)

        # Molecules
        for molecule, core_component in zip(molecule_array,
                                           super.comp_c[:, 1].swapaxes(0, 1)):
            setattr(self, molecule, core_component)
