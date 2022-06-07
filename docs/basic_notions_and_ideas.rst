Basic notions and ideas
=======================

Monte Carlo Simulation
----------------------

Monte Carlo Simulation is a class of methods that consist of executing a stochastic process several times to obtain numerical results about it.

Basic ideas of PyMCSL
---------------------

PyMCSL's monte carlo simulation has the following components:

* **Monte Carlo Simulation environment**
* **Sub-simulation environment**

A **subsimulation environment** is basically a set of resources used to simulate a stochastic process. A subsimulation environment contains a set of mutable variables, a procedure that initializes the simulation environment and a procedure that simulates the multiple steps of the process. These "steps" are basically the actions taken at each instant of time. At each step of the process, the variables have a state, and the record of states that the variables had at each step along the process is the history of the variables. The history allows us to see the temporal evolution of the variables along the simulation.

A **Monte Carlo simulation environment** is an environment composed of multiple independent subsimulation environments. All nested subsimulation environments have the same set of variables, the same initialization procedure, and the same step procedure, but the subsimulations must run independently, that is, without influencing each other. After executing all subsimulations, the history of each subsimulation is stored within the Monte Carlo simulation environment so that the results are later compiled.

.. image:: imgs/pymcsl-diagram.drawio.png
  :width: 700
  :alt: Illustration of PyMCSL Monte Carlo Simulation Components