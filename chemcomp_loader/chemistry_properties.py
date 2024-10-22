# Elemental abundances. Taken from chemcomp/helpers/units/chemistry_const.py
OH_init_abu = 4.9e-4  # O/H abundance, solar value
CH_init_abu = 2.69e-4  # C/H abundance, solar value
SiH_init_abu = 3.24e-5  # Si/H adundance, solar value
FeH_init_abu = 3.16e-5  # Fe/H adundance, solar value
SH_init_abu = 1.32e-5  # S/H adundance, solar value
MgH_init_abu = 3.98e-5  # Mg/H adundance, solar value
HeH_init_abu = 0.085 
AlH_init_abu = 2.82e-6
TiH_init_abu = 8.91e-8
KH_init_abu = 1.07e-7
NaH_init_abu = 1.74e-6
NH_init_abu = 6.76e-5
VH_init_abu = 8.59e-9

# array of species names. Taken from chemcomp/helpers/analysis_helper.py
element_array = ["C_elem", "O", "Fe", "S", "Mg", "Si", "Na", "K", "N", "Al", "Ti", "V", "H", "He"]
molecule_array = [ 
    "rest",
    "CO",
    "N2",
    "CH4",
    "CO2",
    "NH3",
    "trapped_CO_water",
    "H2O",
    "Fe3O4",
    "C",
    "FeS",
    "NaAlSi3O8",
    "KAlSi3O8",
    "Mg2SiO4",
    "Fe2O3",
    "VO",
    "MgSiO3",
    "Al2O3",
    "TiO",
]
iceline_names = [
                "CO & N2",
                "CH4",
                "CO2",
                "H2O & H2S",
                "Fe3O4",
                "NaAlSi3O8 & KAlSi3O8",
                "Mg2SiO4 & Fe2O3",
                "VO",
                "MgSiO3",
                "Al2O3",
                "TiO",
            ]
iceline_temperatures = [20, 30, 70, 150, 371, 970, 1354, 1423, 1500, 1653, 2000]