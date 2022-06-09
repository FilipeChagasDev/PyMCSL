.. PyMCSL documentation master file, created by
   sphinx-quickstart on Mon Jun  6 18:28:26 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyMCSL's documentation!
==================================

Since Monte Carlo simulations can be cumbersome to implement, I created this library to make it easier for you to implement Monte Carlo simulations in Python. PyMCSL (Python Monte Carlo Simulation Library) is a library that provides ready-made simulation environments, dealing internally with the execution of the simulation steps, with the registration of the variable states and with the obtaining of the results. The programmer who uses PyMCSL to develop his simulations only needs to worry about creating functions to define the behavior of the stochastic system.

Articles and tutorials
----------------------

.. toctree::
   :maxdepth: 2

   basic_notions_and_ideas
   examples/galtonboard
   examples/markovchain

Classes
-------

.. toctree::
   :maxdepth: 3

   basic_classes
   aux_classes