Code written to load in simulations from the chemcomp package, including data from .h5 simulation outputs and .yaml config files.

Get started with this by installing via pip in your favourite environment:
```
pip install chemcomp_loader
```

Assuming your file structure looks like this:
```
Parent_folder
    | -- output
    |       | -- simulation.h5
    |       | -- config.yaml
    | -- simulation_loader.py
```

Inside the Python file `simulation_loader.py`, import the Disc Class module to load in your simulation and load the simulation by referencing the relative path:
```
from chemcomp_loader.disc_loader import Disc_class

Disc = Disc_class('output/simulation.h5', 'output/config.yaml)
```

You can then access different attributes of the Disc with ease, such as `Disc.sigma_dust`, `Disc.gas.CO`, `Disc.pebble_flux` etc. For a full list of attributes, call `Disc.print_attritubtes()` and it will print a list of all possible attributes you can access.

Please note that this does *not* load planet data, and is built to only handle discs currently.

If you'd like to add something, please make a pull request so I can integrate it and upload it to PyPi.