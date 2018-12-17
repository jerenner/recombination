import numpy as np
import matplotlib        as mpl
import matplotlib.pyplot as plt
import sys
from mpl_toolkits.mplot3d import Axes3D
plt.switch_backend('agg')

# Arguments
r0 = int(sys.argv[1])
r1 = int(sys.argv[2])
rng = (r0, r1)
print("Running calculation with range = {}".format(rng))

# Constants
trk_dir = "/home/jrenner/recombination/tracks"
fig_dir = "/home/jrenner/recombination/fig"
arr_dir = "/home/jrenner/recombination/arrays"
sigma_T = 10 # mm / sqrt(m)
sigma_L = 3  # mm / sqrt(m)
r2recomb = 2e-3   # in mm^2
zdrift_cut = 10   # in mm

A_nelec = []; A_nrecomb = []
A_zlength = []
for itrk in range(*rng):

    # Load the track file and electron/ion positions.
    # NOTE: distances will be handled in mm.
    trk = np.loadtxt("{}/electron_{}.dat".format(trk_dir,itrk))
    trk_x0 = trk[:,0]*10
    trk_y0 = trk[:,1]*10
    trk_z0 = trk[:,2]*10

    # Determine whether each electron has recombined.
    nelec = len(trk_x0)
    l_recomb = []
    for x0, y0, z0 in zip(trk_x0, trk_y0, trk_z0):

        zdrift = np.maximum((trk_z0 - z0),np.zeros(nelec))
        xdiff = np.random.normal(x0*np.ones(nelec), sigma_T*np.sqrt(zdrift*1e-3))
        ydiff = np.random.normal(y0*np.ones(nelec), sigma_T*np.sqrt(zdrift*1e-3))

        dist = (xdiff-trk_x0)**2 + (ydiff-trk_y0)**2
        recomb = not(np.all(dist[zdrift > zdrift_cut] > r2recomb))
        if(recomb):
            recomb_all = (dist > r2recomb) & (zdrift > zdrift_cut)
            print("-- Recombination with drift distance {}".format(np.max(zdrift[recomb_all])))

        l_recomb.append(recomb)
    l_recomb = np.array(l_recomb)

    zlength = np.max(trk_z0) - np.min(trk_z0)
    nrecomb = len(l_recomb[l_recomb])
    print("{} recombinations for track of length {}".format(nrecomb, zlength))

    # Save the important values for this track.
    A_nelec.append(nelec)
    A_nrecomb.append(nrecomb)
    A_zlength.append(zlength)

    trk_x0_recomb = trk_x0[l_recomb]
    trk_y0_recomb = trk_y0[l_recomb]
    trk_z0_recomb = trk_z0[l_recomb]

    fig = plt.figure()
    fig.set_figheight(6.0)
    fig.set_figwidth(6.0)

    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(trk_x0,trk_y0,trk_z0,marker='.',s=1)
    ax.scatter(trk_x0_recomb, trk_y0_recomb, trk_z0_recomb, marker='*', color='red')
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("z (mm)")

    plt.savefig("{}/trk_{}.pdf".format(fig_dir,itrk), bbox_inches='tight')
    plt.close()

# Convert to numpy arrays.
A_nelec = np.array(A_nelec)
A_nrecomb = np.array(A_nrecomb)
A_zlength = np.array(A_zlength)

# Save the arrays to file.
np.savez("{}/arr_{}.npz".format(arr_dir,rng[0]), A_nelec=A_nelec, A_nrecomb=A_nrecomb, A_zlength=A_zlength)
