
import numpy as np
import tables
from tables.exceptions import NoSuchNodeError
import astropy.units as u
from .import_config import import_config, eval_kwargs
from .chemistry_properties import *

AU = (1*u.au).cgs.value  # define the astronomical unit conversion from cgs
Myr = (1*u.Myr).cgs.value # define the Megayear unit conversion from cgs


def instructions():
    '''
    Function you can call to learn what to do with this module.
    '''
    print("\n\
    Create a Python file in the same folder as your simulation .h5 file and config file.\n\
    Then in the Python file, import the Disc_class module and instantiate the class as:\n\
    \n\
        from disc_loader import Disc_class\n\
        Disc = Disc_class('simulation.h5', 'config.yaml')\n\
    \n\
    Parameters can be accessed via class attributes, e.g:\n\
        sigma_gas   = Disc.sigma_g          # Retrieves gas surface density\n\
        CO_gas      = Disc.gas.CO           # Retrieves CO vapour surface density\n\
        Water_ice   = Disc.dust.H2O         # Retrieves water icte surface density\n\
        ")

class Disc_class:
    '''
    Class object that stores all the disc data and some methods to perform
    certain actions with the data (e.g. calculating C/O ratios).

    Parameters can be accessed via class attributes, e.g:
        Disc        = Disc_class('simulation.h5', 'config.yaml')
        sigma_gas   = Disc.sigma_g          # Retrieves gas surface density
        CO_gas      = Disc.gas.CO           # Retrieves CO vapour surface density
        Water_ice   = Disc.dust.H2O         # Retrieves water ice surface density
    '''
    def __init__(self, file_path, config_file_path):
        self.load_disc(file_path)
        self.load_parameters_from_config(config_file_path)
        self.gas      = Disc_gas(self)
        self.dust     = Disc_dust(self)
        self.icelines = Disc_icelines(self)
    

    def load_disc(self, file_path):
        '''
        Function that loads the disc from the .h5 file produced by chemcomp simulations.
        Saves each disc parameter in a class attribute.

        NOTE:
            self.r is rescaled from cgs to AU.
            self.t is rescaled from cgs to Myr.

        Inputs:
            file_path : path to the .h5 file relative to the current folder. Includes the .h5 file
        '''

        # Load quantities
        with tables.open_file(file_path, mode='r') as f:
            self.disc_quantities = [q for q in dir(f.get_node('/disk')) if q[0]!='_']

            self.T                       = np.array(f.root.disk.T)                       # Disc temperature
            self.T_irr                   = np.array(f.root.disk.T_irr)                   # Disc temperature due to stellar radiation
            self.T_visc                  = np.array(f.root.disk.T_visc)                  # Disc temperature due to viscous heating
            self.a_1                     = np.array(f.root.disk.a_1)                     # 
            self.cum_pebble_flux         = np.array(f.root.disk.cum_pebble_flux)         # Cumulative pebble flux
            self.f_m                     = np.array(f.root.disk.f_m)                     # 
            self.m_dot                   = np.array(f.root.disk.m_dot)                   # Gas accretion rate
            self.m_dot_components        = np.array(f.root.disk.m_dot_components)        # Gass accretion rate for each species
            self.mu                      = np.array(f.root.disk.mu)                      # Mean molecular weight
            self.peb_iso                 = np.array(f.root.disk.peb_iso)                 # Pebble isolation mass at disc positions
            self.pebble_flux             = np.array(f.root.disk.pebble_flux)             # Pebble flux due to all pebbles
            self.r                       = np.array(f.root.disk.r) / AU                  # Radial grid
            self.r_i                     = np.array(f.root.disk.r_i)                     #
            self.sigma_dust              = np.array(f.root.disk.sigma_dust)              # Dust & ice surface density
            self.sigma_dust_components   = np.array(f.root.disk.sigma_dust_components)   # Dust & ice surface density for each species/element
            self.sigma_g                 = np.array(f.root.disk.sigma_g)                 # Gas surface density
            self.sigma_g_components      = np.array(f.root.disk.sigma_g_components)      # Gas surface density for each species/element
            self.stokes_number_df        = np.array(f.root.disk.stokes_number_df)        # Stokes number in drift-induced fragmentation limit
            self.stokes_number_drift     = np.array(f.root.disk.stokes_number_drift)     # Stokes number in drift-limit
            self.stokes_number_frag      = np.array(f.root.disk.stokes_number_frag)      # Stokes number in fragmentation limit
            self.stokes_number_pebbles   = np.array(f.root.disk.stokes_number_pebbles)   # Stokes number of large dust population
            self.stokes_number_small     = np.array(f.root.disk.stokes_number_small)     # Stokes number of small dust population
            self.t                       = np.array(f.root.disk.t)  / Myr                 # Time grid
            self.vr_dust                 = np.array(f.root.disk.vr_dust)                 # Radial velocity of dust
            self.vr_gas                  = np.array(f.root.disk.vr_gas)                  # Radial velocity of gas
            try:
                self.lstar               = np.array(f.root.disk.lstar)
            except NoSuchNodeError:
                pass
            try:
                self.rho_solid           = np.array(f.root.disk.rho_solid)
            except NoSuchNodeError:
                pass
    

    def load_parameters_from_config(self, config_file_path):
        '''
        Function that loads the disc parameters from the config file.
        
        Some code for this function taken straight from the chemcomp files. (https://github.com/AaronDavidSchneider/chemcomp)
        Code taken straight from `/chemcomp/chemcomp/helpers/main_helpers.py
        Full credit to Aaron David Schneider & Betram Bitsch.
        '''
        config                  = import_config(config_file_path)
        config_disk             = config.get("config_disk", {})
        config_pebble_accretion = config.get("config_pebble_accretion", {})
        chemistry_conf          = config.get("chemistry", {})

        # Evaluating chemical partitioning model initial conditions
        self.chemistry = Disc_chemistry(chemistry_conf)

        # Evaluating disc and pebble parameters
        self.M_star             = eval_kwargs(config_disk.get('M_STAR', None))
        self.alpha              = eval_kwargs(config_disk.get('ALPHA', None))
        self.alpha_height       = eval_kwargs(config_disk.get('ALPHAHEIGHT', None))
        self.Mdisk              = eval_kwargs(config_disk.get('M0', None))
        self.Rdisk              = eval_kwargs(config_disk.get('R0', None))
        self.DTG                = eval_kwargs(config_disk.get('DTG_total', None))
        self.static             = eval_kwargs(config_disk.get('static', None)) # gas/dust evolution boolean
        self.evaporation        = eval_kwargs(config_disk.get('evaporation', None))
        self.static_stokes      = eval_kwargs(config_disk.get('static_stokes', None))
        self.tau_disk           = eval_kwargs(config_disk.get('tau disk', None))
        self.begin_photevap     = eval_kwargs(config_disk.get('begin_photevap', None))
        self.temp_evol          = eval_kwargs(config_disk.get('temp_evol', None))
        self.evap_width         = eval_kwargs(config_disk.get('evap_width', None))
        self.vfrag              = eval_kwargs(config_pebble_accretion.get('u_frag', '1m/s for dry, 10m/s for icy pebbles'))
        
        if not hasattr(self, 'rho_solid'): # Only if rho_solid has been set in config file
            self.rho_solid          = eval_kwargs(config_pebble_accretion.get('rho_solid'))
            if self.rho_solid is None:
                print('No \'rho_solid\' parameter found in config or output. Assuming rho=1.67 g/cm^3 for grain size calculations.')
                self.rho_solid = 1.67
    

    def calculate_C_to_O(self, t=None):
        '''
        Function to calculate the C-to-O ratio in the disc for the solid and gas
        phases. These can be accessed as e.g.:

            Disc = Disc_class('simulation.h5', 'config.yaml')
            Disc.calculate_C_to_O()
            C_to_O_gas = Disc.gas.C_to_O
            C_to_O_solid = Disc.dust.C_to_o
        '''
        # return
        if t == None:
            print('No time specified to C/O ratio. Assuming t = 1 Myr.')
            t = 1
        self.it = self.t.searchsorted(t)
        self.dust.C_to_O    = self.dust.C_elem[self.it] / self.dust.O[self.it]
        self.gas.C_to_O     = self.gas.C_elem[self.it] / self.gas.O[self.it]
    
    def calculate_O_to_H(self, t=None):
        if t == None:
            print('No time specified to C/O ratio. Assuming t = 1 Myr.')
            t = 1
        self.it = self.t.searchsorted(t)
        self.dust.O_to_H    = self.dust.O / self.dust.H
        self.gas.O_to_H     = self.gas.O / self.gas.H

    def print_attributes(self):
        '''
        Function that prints the attributes of the Disc class.
        '''
        [print(attribute) for attribute in dir(self) if attribute[0:2] != '__']


class Disc_gas:
    '''
    Class that contains the gas surface densities of the disc.
    Attributes can be accessed via e.g. self.gas.CO inside Disc_class.
    '''
    def __init__(self, super):
        # Disc_gas does not need to inherit any components of super.
        # Elemental distributions
        for element, gas_component in zip(element_array,
                                          super.sigma_g_components[:,:,0,:].swapaxes(0,2).swapaxes(1,2)):
            setattr(self, element, gas_component)        

        # Molecules
        for molecule, gas_component in zip(molecule_array,
                                           super.sigma_g_components[:,:,1].swapaxes(0,2).swapaxes(1,2)):
            setattr(self, molecule, gas_component)


class Disc_dust:
    '''
    Class that contains the dust and ice surface densities of the disc.
    Attributes can be accessed via e.g. self.dust.CO inside Disc_class.
    '''
    def __init__(self, super):
        # Elemental distributions
        for element, gas_component in zip(element_array,
                                          super.sigma_dust_components[:,:,0].swapaxes(0,2).swapaxes(1,2)):
            setattr(self, element, gas_component)        

        # Molecules
        for molecule, gas_component in zip(molecule_array,
                                           super.sigma_dust_components[:,:,1].swapaxes(0,2).swapaxes(1,2)):
            setattr(self, molecule, gas_component)


class Disc_icelines:
    '''
    Class that contains indexes of ice-lines of chemical species in the disc.
    Attributes can be accessed via e.g. self.icelines.CO inside Disc_class.
    '''
    def __init__(self, super):
        positions = np.array([self.get_position_of_ice(super.T[i,:]) for i in range(len(super.T))]).swapaxes(0, 1)
        for molecule, idx in zip(iceline_names, positions):
            setattr(self, molecule, idx)

    def get_position_of_ice(self, T: np.array) -> np.array:
        """
        Function taken straight from the chemcomp files. (https://github.com/AaronDavidSchneider/chemcomp)
        Code taken straight from `/chemcomp/chemcomp/disks/_chemistry.py
        Full credit to Aaron David Schneider & Betram Bitsch.

        function that can be used to determine the indicees of the icelines
        This index is the index of the first cell in r/T that has no gas in sigma

        gas | gas | gas | solid | solid | solid
                           idx

        Parameters
        ----------
        T: temperature N-dimensional array in cgs

        Returns
        -------
        idx: position of icelines

        """
        # exclude phantom iceline of rest_mol
        idx = np.squeeze(np.searchsorted(-T, -np.array(iceline_temperatures), side="right"))
        # np.squeeze uses 1e-6 s. Total: 5.3e-6 s
        idx = np.minimum(idx, T.size - 2)

        return idx


class Disc_chemistry:
    '''
    Class that contains the elemental abundances and Carbon species fractions used in the simulations.
    Note that this assumes use_FeH = False.

    Some code for this function taken straight from the chemcomp files. (https://github.com/AaronDavidSchneider/chemcomp)
    Code taken straight from `/chemcomp/chemcomp/disks/_chemistry.py
    Credit to Aaron David Schneider & Betram Bitsch.
    '''
    def __init__(self, chemistry_conf):
        self.OH         = OH_init_abu   * 10 ** (eval_kwargs(chemistry_conf.get('OH',   0.0 )))
        self.CH         = CH_init_abu   * 10 ** (eval_kwargs(chemistry_conf.get('CH',   0.0 )))
        self.SiH        = SiH_init_abu  * 10 ** (eval_kwargs(chemistry_conf.get('SiH',  0.0 )))
        self.SH         = SH_init_abu   * 10 ** (eval_kwargs(chemistry_conf.get('SH',   0.0 )))
        self.MgH        = MgH_init_abu  * 10 ** (eval_kwargs(chemistry_conf.get('MgH',  0.0 )))
        self.FeH        = FeH_init_abu  * 10 ** (eval_kwargs(chemistry_conf.get('FeH',  0.0 )))
        self.NH         = NH_init_abu   * 10 ** (eval_kwargs(chemistry_conf.get('NH',   0.0 )))
        self.AlH        = AlH_init_abu  * 10 ** (eval_kwargs(chemistry_conf.get('AlH',  0.0 )))
        self.TiH        = TiH_init_abu  * 10 ** (eval_kwargs(chemistry_conf.get('TiH',  0.0 )))
        self.KH         = KH_init_abu   * 10 ** (eval_kwargs(chemistry_conf.get('LH',   0.0 )))
        self.NaH        = NaH_init_abu  * 10 ** (eval_kwargs(chemistry_conf.get('NaH',  0.0 )))
        self.VH         = VH_init_abu   * 10 ** (eval_kwargs(chemistry_conf.get('VH',   0.0 )))
        self.HeH        = HeH_init_abu  * 10 ** (eval_kwargs(chemistry_conf.get('HeH',  0.0 )))
        self.C_frac     = eval_kwargs(chemistry_conf.get('C_frac', 0.2))
        self.CH4        = eval_kwargs(chemistry_conf.get('CH4_frac', (0.45 - self.C_frac)))
        self.CO_frac    = eval_kwargs(chemistry_conf.get('CO_frac', 0.45))
        self.CO2_frac   = eval_kwargs(chemistry_conf.get('CO2_frac', 0.1))
