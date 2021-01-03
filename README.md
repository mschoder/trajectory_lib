# Trajectory Library

Working project to build a trajectory library using curvature-continuous (C2) cubic splines

![](example.png)


### Dependencies

```
- numpy
- scipy
- matplotlib
```

### Usage

`python generate_traj_lib.py long_sep arc_sep th_spread num_layers --outfile --plot=True`

Example:

`python generate_traj_lib.py  20 5 30 4 --plot=True`

### Output Data Structure
```
Dictionary of enumerated trajectories each of the form:
{   'x':       list of x-coordinates (meters),
    'y':       list of y-coordinates (meters),
    'x_coef':  array of x-spline coefficients ( (num_layers + 1) x 4 ),
    'y_coef':  array of y-spline coefficients,
    'psi':     heading angle (radians),
    'k':       curvature
    'k_max':   maximum curvature
}
    
```

