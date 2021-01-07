import numpy as np
import json
from helper_funcs import spline



def gen_circ_grid(long_sep, arc_sep, th_spread, num_layers):
    '''
    Generate a set of points along a series of circular arcs which defines a path tree
        long_sep:   longitudinal separation between layers along vehicle x-axis (meters)
        arc_sep:    approximate desired separation between adacent nodes along the arc (meters)
        th_spread:  angle on each side of zero heading from prev layer nodes (degrees)
        num_layers: number of concentric arcs, exclusive of origin point (integer)
    Returns a list of lists of tuples (x, y, theta) for each node in the tree
    '''
    
    nodes = [[(0,0,0)]]   # initialize with origin (current pos in car frame)
    th_spread_rad = th_spread/360*2*np.pi
    fan = 0

    for i in range(num_layers):
        layer = i + 1
        r = long_sep * layer
        layer_nodes = []

        # calculate expanded heading angle
        phi = th_spread_rad - np.arcsin((r-long_sep)*np.sin(np.pi - th_spread_rad)/r)
        fan = fan + phi

        th_sep = arc_sep / r   # angular separation between nodes in current layer, radians
        n_pts = int(np.ceil(2*fan / th_sep))
        # Ensure odd number of points so that straight line trajectory is preserved
        if n_pts % 2 == 0:
            n_pts += 1
        ths = np.linspace(-fan, fan, n_pts)

        for th in ths:
            x = r * np.sin(th)
            y = r * np.cos(th)
            layer_nodes.append((x,y,th))
        nodes.append(layer_nodes)
    return nodes



def get_paths(nodes, params, layer=0, idx=0, parent=None, paths=None, current_path=None):
    '''
    Generate all possible node combinations
    Depth-first walk through tree, taking only children nodes at each step that fall within th_spread range
    Returns a list of lists of tuples (x,y,th) describing every path to be considered starting at the root
    '''

    long_sep = params['long_sep']
    th_spread = params['th_spread']

    if paths is None:
        paths = []
    if current_path is None:
        current_path = []
    
    cur_node = nodes[layer][idx]
    
    if parent is None:
        current_path.append(cur_node)
    else:   
        # Filter trajectories by allowable heading range
        r = long_sep * layer
        th_spread_rad = th_spread/360*2*np.pi
        phi = th_spread_rad - np.arcsin((r-long_sep)*np.sin(np.pi - th_spread_rad)/r)
        eps = 0.02
        th_rng = [parent[2] - phi - eps, parent[2] + phi + eps]
        if cur_node[2] >= th_rng[0] and cur_node[2] <= th_rng[1]:
            current_path.append(cur_node)
        else:
            return
        
    if len(nodes) == layer+1:
        paths.append(current_path)
    else:
        for idx in range(len(nodes[layer+1])):
            get_paths(nodes, params, layer+1, idx, cur_node, paths, list(current_path))
    return paths


def gen_splines(paths):
    '''
    Function to generate splines for each set of node paths
    Returns a list of tuples, where each tuple is a (x_spline, y_spline)
        and x_spline, y_spline are scipy CubicSpline objects
    '''
    trajs = []
    long_sep = np.sqrt((paths[0][1][0]-paths[0][0][0])**2 + (paths[0][1][1]-paths[0][0][1])**2)
    
    for path in paths:
        x = np.array([p[0] for p in path])
        y = np.array([p[1] for p in path])

        # init_heading = np.arccos(path[1][0]/long_sep)
        # init_heading = 0
        # print(init_heading)
        init_heading = np.pi/2
        
        cx, cy = spline.calc_c2_traj(x, y, init_heading)
        trajs.append((cx, cy))
    return trajs



def eval_trajectories(paths, n_interps=50, outfile=None):
    '''
    Evaluate all trajectories and save to json object
    '''
    
    splines = gen_splines(paths)

    eval_trajs = {}
    ts = np.linspace(0, len(paths[0])-1, n_interps)

    for i,traj in enumerate(splines):
        cx, cy = traj
        k = spline.compute_spline_curvature(cx,cy,ts).tolist()
        psi = spline.compute_spline_heading(cx,cy,ts).tolist()
        k_max = np.max(np.abs(k))
        eval_trajs[i] = {'x': cx(ts).tolist(),
                         'y': cy(ts).tolist(),
                         'x_coef': cx.c.tolist(),  # spline coefficients array
                         'y_coef': cy.c.tolist(),
                         'psi': psi,
                         'k': k,
                         'k_max': k_max}
    
    if outfile is not None:
        with open(outfile, "w") as outfile:  
            json.dump(eval_trajs, outfile, indent=4) 
    
    return eval_trajs