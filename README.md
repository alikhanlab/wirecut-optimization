# Wirecut-optimization
Resource allocation optimization project. 

## Background and Application

The motivation behind this project is there are many application of resource allocation problem. For example, client come to manufacturer and asks some product with required properties and manufacturer go to warehouse and satisfy client's demand with given requirements from inventory. In this project product is wire, with length and quantity as client requirement. Application  performs optimization of usage of inventory and satisfying all given demand from clients. 

## Methodology

Used different heruistics to get optimal solutions.

- FFD (First Fit Decresing)
- Arc-Flow. 

Arc-Flow formulation scaled well on big inputs, and main application file uses arc-flow only.

## Dependencies

- Python packages
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install python dependencies.
```bash
pip install -r requirements.txt
```

- pyvpsolver (see installation instruction). Arc-flow formulation implementation by Filipe Brandao. [here](https://github.com/fdabrandao/vpsolver)

- Linear Optimization Solvers:
  - Gurobi. Commercial solver, get free academic license [here](https://www.gurobi.com/)
  - SCIP. Fast open source solver, download [here](https://www.scipopt.org/)
  - GLPK. Open source solver, download [here](https://www.gnu.org/software/glpk/)
  
 ## License

Licensed under the [MIT License](LICENSE.txt) 
