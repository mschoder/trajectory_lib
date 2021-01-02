import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline


def plot_trajectories(all_nodes, paths, trajs):
    ## PLOT all trajs
    stepsize = 0.1
    ts = np.arange(0, len(paths[0])-1+stepsize, stepsize)
    ts_plus = np.arange(ts[0]-.5, ts[-1]+.3, stepsize)

    plt.figure(figsize=(15,10))
    plt.scatter([x[0] for x in all_nodes],[x[1] for x in all_nodes])
    plt.axis('equal');
    plt.xlabel('y (m)')
    plt.ylabel('x (m)')

    for traj in trajs:
        cx, cy = traj
        plt.plot(cx(ts), cy(ts))
    plt.show()