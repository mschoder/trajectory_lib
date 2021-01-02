
import numpy as np
from scipy.interpolate import CubicSpline



def gen_c2_spline(x, y, init_heading, slen_start, slen_end):
    '''
    Generates a C2 continuous spline using scipy CubicSpline lib
    x: np.array of x-coordinate points
    y: np.array of y-coordinate points
    '''
    
    # define mu, a virtual path variable of length 1 for each spline segment
    assert(len(x) == len(y))
    mu = np.arange(0,len(x), 1.0)

    # build splines
    cs_x = CubicSpline(mu, x, 
                   bc_type=((1, slen_start * np.cos(init_heading)), 
                            (2, 0.0)))
    cs_y = CubicSpline(mu, y, 
                   bc_type=((1, slen_start * np.sin(init_heading)), 
                            (2, 0.0)))
    return cs_x, cs_y



def calc_c2_traj(x, y, init_heading, eps = 0.005):
    '''
    Iteratively compute spline coefficients until spline length of first and last segment converges
    x, y: 1D numpy array of control coordinates (x,y) through which spline must pass
    '''

    # Start with euclidean dist as slen approx for first and last segments
    slen_start = np.sqrt((x[1] - x[0])**2 + (y[1] - y[0])**2)
    slen_end = np.sqrt((x[-1] - x[-2])**2 + (y[-1] - y[-2])**2)

    while True:
        cx, cy = gen_c2_spline(x, y, init_heading, slen_start, slen_end)
        coeffs_x_start = np.flip(cx.c[:,0])
        coeffs_y_start = np.flip(cy.c[:,0])
        coeffs_x_end = np.flip(cx.c[:,-1])
        coeffs_y_end = np.flip(cy.c[:,-1])

        slen_start_new = calc_spline_length(coeffs_x_start, coeffs_y_start)
        slen_end_new = calc_spline_length(coeffs_x_end, coeffs_y_end)

        if abs(slen_start_new - slen_start) < eps and abs(slen_end_new - slen_end) < eps:
            break
        else:
            slen_start = slen_start_new
            slen_end = slen_end_new
    return cx, cy


def calc_spline_length(x_coeffs, y_coeffs, n_ips=20):
    '''
    Returns numerically computed length along cubic spline
    x_coeffs: array of 4 x coefficients
    y_coeffs: array of 4 y coefficients
    '''
    
    t_steps = np.linspace(0.0, 1.0, n_ips)
    spl_coords = np.zeros((n_ips, 2))
    
    spl_coords[:,0] = x_coeffs[0] \
                        + x_coeffs[1] * t_steps \
                        + x_coeffs[2] * np.power(t_steps, 2) \
                        + x_coeffs[3] * np.power(t_steps, 3)
    spl_coords[:,1] = y_coeffs[0] \
                        + y_coeffs[1] * t_steps \
                        + y_coeffs[2] * np.power(t_steps, 2) \
                        + y_coeffs[3] * np.power(t_steps, 3)
        
    slength = np.sum(np.sqrt(np.sum(np.power(np.diff(spl_coords, axis=0), 2), axis=1)))
    return slength

def compute_spline_heading(x, y, t):
    '''
    Evaluate heading (psi) using parametric spline representation at each interpolated point in t
    Ensure returned angles are between [-pi, pi]
        t = path variable, a 1D numpy array

    '''
    psi = np.arctan2(x(t,1), y(t,1))
    psi[psi >= np.pi] -= 2 * np.pi
    psi[psi < -np.pi] += 2 * np.pi
    return psi



def compute_spline_curvature(x, y, t):
    '''
    Evaluate K using parametric curvature equation at each point in t
        Splines are given as parametric equations: x = x(t), y = y(t)
        t = path variable, a 1D numpy array
    Returns an array of curvatures along the spline with same shape as t
    '''
    K = np.abs( x(t,1)*y(t,2) - y(t,1)*x(t,2) ) / ( (x(t,1)**2) + y(t,1)**2 )**(3/2)
    return K