import itertools
import argparse
import time, math
from helper_funcs import *

"""
Script to generate a trajectory library of cubic spline paths
Outputs a json file with interpolated spline points, spline coefficients, headings and curvature
TODO - add more comprehensive documentation
"""


# ---------------------------------------------------------------------------------
# PARSE USER INPUT
# --------------------------------------------------------------------------------
start = time.process_time()

parser = argparse.ArgumentParser(description='Generate Trajectory Library of C2 Cubic Splines')
parser.add_argument('long_sep', metavar='long_sep', type=float, help='longitudinal separation between layers (meters)')
parser.add_argument('arc_sep', metavar='arc_sep', type=float, help='approximate desired separation between adacent nodes along the arc (meters)')
parser.add_argument('th_spread', metavar='th_spread', type=float, help='angle on each side of zero heading from prev layer nodes (degrees)')
parser.add_argument('num_layers', metavar='num_layers', type=int, help='number of concentric arcs, exclusive of origin point (integer)')
parser.add_argument('--num_interps', metavar='num_interps', default=None, type=int, help='number of interpolated points evaluated for each trajectory (integer)')
parser.add_argument('--outfile', type=str, default='./traj_lib.json', help='path to output file with .json suffix (default: ./traj_lib.json)')
parser.add_argument('--plot', type=bool, default=False, help='boolean flag to plot trajectories')
args = parser.parse_args()

# --------------------------------------------------------------------------------

params = {
   'long_sep':   args.long_sep,
   'arc_sep':    args.arc_sep,
   'th_spread':  args.th_spread,
   'num_layers': args.num_layers 
}


base_path_len = 1.3 * args.num_layers * args.long_sep
# Compute default interpolation stepsize == 0.5m
if args.num_interps is None:
   stepsize = 0.5
   num_interps = math.ceil(base_path_len / stepsize)
else:
   num_interps = args.num_interps
   stepsize = base_path_len / num_interps


nodes = grid.gen_circ_grid(**params)
paths = grid.get_paths(nodes, params)
trajs = grid.gen_splines(paths)


# Create output dictionary and save as json
eval_trajs = grid.eval_trajectories(paths, n_interps=num_interps, outfile=args.outfile)
end = time.process_time()
elapsed = end - start

print(f'Generated {len(trajs)} trajectories in {elapsed:.4f} sec')
print(f'Used {num_interps} interpolation points at an approximate spacing of {stepsize} meters')
print(f'Saved trajectory output data to {args.outfile}')

# Plot output
if args.plot:
    all_nodes = list(itertools.chain.from_iterable(nodes))
    plotter.plot_trajectories(all_nodes, paths, trajs)