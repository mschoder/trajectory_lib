import itertools
import argparse
from helper_funcs import *

"""
Script to generate a trajectory library of cubic spline paths
Outputs a json file with interpolated spline points, spline coefficients, headings and curvature
TODO - add more comprehensive documentation
"""


# ---------------------------------------------------------------------------------
# PARSE USER INPUT
# --------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Generate Trajectory Library of C2 Cubic Splines')
parser.add_argument('long_sep', metavar='long_sep', type=float, help='longitudinal separation between layers (meters)')
parser.add_argument('arc_sep', metavar='arc_sep', type=float, help='approximate desired separation between adacent nodes along the arc (meters)')
parser.add_argument('th_spread', metavar='th_spread', type=float, help='angle on each side of zero heading from prev layer nodes (degrees)')
parser.add_argument('num_layers', metavar='num_layers', type=int, help='number of concentric arcs, exclusive of origin point (integer)')
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

nodes = grid.gen_circ_grid(**params)
paths = grid.get_paths(nodes, params)
trajs = grid.gen_splines(paths)

# Plot output
if args.plot:
    all_nodes = list(itertools.chain.from_iterable(nodes))
    plotter.plot_trajectories(all_nodes, paths, trajs)

# Create output dictionary and save as json
eval_trajs = grid.eval_trajectories(paths, outfile=args.outfile)

print(f'Generated {len(trajs)} trajectories.')
print(f'Saved trajectory output data to {args.outfile}')