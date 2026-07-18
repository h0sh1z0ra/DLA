# -*- coding: utf-8 -*-
"""
Created on Mon May  4 18:51:28 2026

@author: kaela
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# List of probabilities to pass thorugh functions as arguments
p5 = [0.25,0.25,0.25,0.25]

# Probability list with biases; delta is the increase or decrease in a direction
delta = 0.08
p5_left = [0.25+delta, 0.25-delta,0.25,0.25]
p5_right = [0.25-delta,0.25+delta,0.25,0.25]
p5_up = [0.25,0.25,0.25-delta,0.25+delta]
p5_down = [0.25,0.25,0.25+delta,0.25-delta]

# Spawning the walker particle
def spawn_walker(R_max):
    r = R_max + 5           # Radius within which the walker can spawn
    theta = np.random.uniform(0, 2*np.pi)     # random angle
    x = int(np.round(r * (np.cos(theta))))    # x coordinate spawn
    y = int(np.round(r * (np.sin(theta))))    # y coordinate spawn
    # set to integers because lattice positions are discrete
    return x,y

# Walking in random direction with some probability in each direction
# def rwalk(x,y,p):
#     drn_list = [(1,0),(-1,0),(0,1),(0,-1)]      # Depending on a random number from 0-3, advances based on that index in the list
#     direction = np.random.choice(4, p=p)        # chooses random direction with given probabilities
#     dx,dy = drn_list[direction]
    
#     return x+dx,y+dy

# Defining a function that will spawn a walker, and walks it until it sticks
def stuck(cluster, R_max, Pnn, Psnn, p):
    x, y = spawn_walker(R_max)             # Spawn walker
    kill_rad_sq = max(3*R_max,8)**2
    path = []                              # For extension; tracks the path taken by a sticking particle
    
    # Variables for the walk
    batch_size = 1000                                   # Using batches instead of r_walk improves runtime!
    batch = np.random.choice(4, p=p, size=batch_size) 
    pointer = 0
    drn_list = [(1,0),(-1,0),(0,1),(0,-1)]
    
    # Defining the conditions for the walk
    while True:                             
        if pointer==batch_size:
            batch = np.random.choice(4, p=p, size=batch_size)     # Reset batch if pointer matches batch size;
            # basically if the walker takes too many steps it can exhaust the batch of walks; this resets that
            pointer=0
        
        # Defines direction to walk
        dx, dy = drn_list[batch[pointer]]
        pointer+=1
        x,y = x+dx, y+dy                    # Walk!
        path.append((x,y))
        
        # Conditions for kill radius and sticking...
        dist_sq = x**2 + y**2                       # Leave squared for efficieny; square root R_max later
        
        # Condition to reset particle
        if dist_sq >= kill_rad_sq:                 # Check if particle is threshold radius
            path.clear()                           # Reset path list since particle didn't stick
            x,y = spawn_walker(R_max)              # Kill particle and restart
            kill_rad_sq = max(3*R_max,8)**2
        
        # If within the max radius, checks if it sticks to neighbours
        elif dist_sq < (R_max+2)**2:
            nn = ((x+1, y), (x-1, y), (x,y+1), (x,y-1))             # Nearest neighbour
            snn = ((x+1, y+1), (x-1, y+1), (x+1, y-1), (x-1, y-1))  # Second nearest neighbour
            neighbours = [*zip(nn,[Pnn]*4), *zip(snn, [Psnn]*4)]   # Make a list with the neighbour and its corresponding sticking probability
            
            # Combing through neighbours, and rolling to see if it sticks
            for (nx, ny), P in neighbours:
                if (nx, ny) in cluster:
                    roll = np.random.rand()
                    if roll < P:
                        return (x,y), path      # Attaches to cluster
                    elif roll > P:
                        break                   # Return to while True loop

# Executing the above commands to form a cluster
def run_dla(N, Pnn, Psnn, p):
    cluster = {(0,0)}                      # Set cluster to (0,0)
    R_max = 0                              # Initial R_max = 0
    order = []
    order.append((0,0))                    # For the animation; the first point should be (0,0)

    # Loops until the cluster reaches the desired size
    while len(cluster) < N:
        (x, y), path = stuck(cluster, R_max, Pnn, Psnn, p)
        cluster.add((x, y))
        order.append((x,y))
        
        # Updates R_max if new value exceeds old value
        dist =  (x**2 + y**2)**0.5
        if dist > R_max:
            R_max = dist
        
        # # Print update every 200 particles mapped
        # if len(cluster)%200==0:
        #     print(f"Still working! Mapped particles: {len(cluster)}/{N}")
            
    return cluster, order

def C(cluster):
    cluster_arr = np.array(list(cluster[0]))
    N = len(cluster_arr)
    
    # Defining shell
    max_r = max((np.sum(cluster_arr**2,axis=1))**0.5)                # Compute max distance
    r = np.linspace(1, max_r, 100)                                   # Length of linspace controls shell thickness
    dr = (r[1] - r[0])/2
    
    C_r = np.zeros(len(r))
    
    # Computing the distances for each point on the cluster to every other point
    # all_dist = []
    for x1, y1 in cluster_arr:
        diff_sq = (cluster_arr - (x1, y1))**2           # Square of distance; broadcasting (x1,y1) subtraction
        sums = np.sum(diff_sq,axis=1)                   # Summing to find square of distances
        dist = (sums)**0.5
        dist = dist[dist!=0]                            # Removes 0 values
        
        # Looping through r
        for i, ri in enumerate(r):
            shell_count = np.sum((ri - dr <= dist) & (dist < ri + dr))   # Within shell; & for elementwise
                  
            shell_area = np.pi * ((ri+dr)**2 - (ri-dr)**2)               # Computing area of the shell
            C_r[i] += shell_count / (N * shell_area)
    
    # Computing average over N
    C_r /= N
    return r, C_r

# For creativity; finding the fractal dimension
def find_D(r, C_r):
    
    # Removing zeros to avoid log issues...
    mask = C_r > 0
    r_masked = r[mask]
    C_masked = C_r[mask]
    
    # Using middle region, since after r>30 the plot becomes extremely noisy and distorted
    r_trim = r_masked[r_masked<50]          # Cutting noisy sections
    C_trim = C_masked[r_masked<50]
    
    # Plotting fit to find D
    log_r = np.log(r_trim)
    log_C = np.log(C_trim)
    m, c = np.polyfit(log_r, log_C, 1)
    
    # Calculating D
    D = m + 2
    # plt.loglog(r_masked,C_masked)               # loglog as per Equation (2)
    # plt.title("ln(C(r)) vs ln(r)")
    # plt.xlabel("ln(r)")
    # plt.ylabel("ln(C(r))")    
    return D

# Price path generator
def price_path(p, n_paths):
    x_list=[]
    for i in range(n_paths):
        (xc,yc), path = stuck({(0,0)}, 0, 1, 0, p)      # Use a simple cluster where it's just the origin point
        x,y = zip(*path)
        x_list.append(x)    # Only return x values
    return x_list

# =============================================================================
# Part (a): Normal plot; comparing Pnn = 1 and Pnn = 0.3
# =============================================================================
# cluster1 = run_dla(500, 1, 0, p5)
# cluster2 = run_dla(500, 0.3, 0, p5)
# fig, axs = plt.subplots(1,2, figsize=(20,10))
# x1, y1 = zip(*cluster1[1])
# x2, y2 = zip(*cluster2[1])

# axs[0].scatter(x1,y1, s=7, color='r')
# axs[0].set_title('Cluster with Pnn = 1')
# axs[0].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# axs[1].scatter(x2,y2, s=7, color='c')
# axs[1].set_title('Cluster with Pnn = 0.3')
# axs[1].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)


# =============================================================================
# Part (b): Effect of applied magnetic field on cluster
# =============================================================================
# cluster1 = run_dla(5000, 1, 0, p5_left)
# cluster2 = run_dla(5000, 1, 0, p5_right)
# cluster3 = run_dla(5000, 1, 0, p5_up)
# cluster4 = run_dla(5000, 1, 0, p5_down)

# cluster_list = [cluster1, cluster2, cluster3, cluster4]
# fig, axs = plt.subplots(2,2, figsize=(20,20))
# axs = axs.flat        # Fixes issue with subplots 2,2

# i=0
# for cluster in cluster_list:
#     cx, cy = zip(*cluster[1])
#     axs[i].scatter(cx,cy,s=10)
#     axs[i].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)    # Disabling axis ticks
#     i+=1


# axs[0].set_title(f"Cluster with {delta} bias to the left")
# axs[1].set_title(f"Cluster with {delta} bias to the right")
# axs[2].set_title(f"Cluster with {delta} bias upwards")
# axs[3].set_title(f"Cluster with {delta} bias downwards")

# =============================================================================
# Part (c), finding ln(C(r)) vs r
# =============================================================================
# C_avg1 = []
# C_avg2 = []
# r_list = []

# # Loop to make 20 clusters
# for i in range(20):
#     cluster1 = run_dla(5000, 1, 0, p5)
#     r1, C_r1 = C(cluster1)
#     C_avg1.append(C_r1)
#     r_list.append(r1)

# # Same loop for Pnn = 0.3
# for j in range(20):
#     cluster2 = run_dla(5000, 0.3, 0, p5)
#     r2, C_r2 = C(cluster2)
#     C_avg2.append(C_r2)

# C_avg1 = np.mean(C_avg1, axis=0)          # Average over cluster
# r = r_list[0]                           # Choose one to plot, shouldn't matter which since they're all approximately the same

# C_avg2 = np.mean(C_avg2, axis=0)          # Average over cluster

# plt.semilogy(r, C_avg1, color='c', alpha=0.6)
# plt.semilogy(r, C_avg2, color='m', alpha=0.6)
# plt.title("C(r) vs r, for Psnn=0")
# plt.xlabel("Distance to reference particle r")
# plt.ylabel("Normalised probability density C(r)")
# plt.legend(
#     ['Pnn = 1, Psnn = 0', 'Pnn = 0.3, Psnn=0'],
#     loc='best',
#     facecolor='lightyellow')
# plt.savefig('Cr_vs_r_no_Psnn.png')
# plt.show()
# plt.close()

# =============================================================================
# Part (d), incorporating Psnn
# =============================================================================
# cluster1 = run_dla(5000, 1, 0.5, p5)
# cluster2 = run_dla(5000, 0.3, 0.15, p5)
# fig, axs = plt.subplots(1,2, figsize=(20,10))
# x1, y1 = zip(*cluster1[1])
# x2, y2 = zip(*cluster2[1])

# axs[0].scatter(x1,y1,s=10,color='r')
# axs[0].set_title('Cluster with Pnn = 1, Psnn = 0.5')
# axs[0].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# axs[1].scatter(x2,y2,s=10,color='c')
# axs[1].set_title('Cluster with Pnn = 0.3, Psnn = 0.15')
# axs[1].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# ---------------------------------------------------------------------------------

# cluster1 = run_dla(5000, 1, 0, p5_left)
# cluster2 = run_dla(5000, 1, 0, p5_right)
# cluster3 = run_dla(5000, 1, 0, p5_up)
# cluster4 = run_dla(5000, 1, 0, p5_down)

# cluster_list = [cluster1, cluster2, cluster3, cluster4]
# fig, axs = plt.subplots(2,2, figsize=(20,20))
# axs=axs.flat

# i=0
# for cluster in cluster_list:
#     cx, cy = zip(*cluster[1])
#     axs[i].scatter(cx,cy,s=10,c='r')
#     axs[i].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
#     i+=1

# axs[0].set_title(f"Cluster with Pnn = 1, Psnn=0.5 with {delta} bias to the left")
# axs[1].set_title(f"Cluster with Pnn = 1, Psnn=0.5 with {delta} bias to the right")
# axs[2].set_title(f"Cluster with Pnn = 1, Psnn=0.5 with {delta} bias upwards")
# axs[3].set_title(f"Cluster with Pnn = 1, Psnn=0.5 with {delta} bias downwards")

# ---------------------------------------------------------------------------------
# bC_avg1 = []
# bC_avg2 = []
# br_list = []

# # Loop to make 20 clusters
# for i in range(20):
#     bcluster1 = run_dla(5000, 1, 0.5, p5)
#     br1, bC_r1 = C(bcluster1)
#     bC_avg1.append(bC_r1)
#     br_list.append(br1)

# # Same loop for Pnn = 0.3
# for j in range(20):
#     bcluster2 = run_dla(5000, 0.3, 0.15, p5)
#     br2, bC_r2 = C(bcluster2)
#     bC_avg2.append(bC_r2)

# bC_avg1 = np.mean(bC_avg1, axis=0)          # Average over cluster
# br = br_list[0]                           # Choose one to plot, shouldn't matter which since they're all approximately the same

# bC_avg2 = np.mean(bC_avg2, axis=0)          # Average over cluster

# plt.semilogy(br, bC_avg1, color='r', alpha=0.6)
# plt.semilogy(br, bC_avg2, color='g', alpha=0.6)
# plt.title("C(r) vs r, for Psnn = 0.5Pnn")
# plt.xlabel("Distance to reference particle r")
# plt.ylabel("Normalised probability density C(r)")
# plt.legend(
#     ['Pnn = 1, Psnn = 0.5', 'Pnn = 0.3, Psnn=0.15'],
#     loc='best',
#     facecolor='lightyellow')
# plt.savefig('Cr_vs_r_Psnn.png')
# plt.show()
# plt.close()

# =============================================================================
# Fractal Dimension
# =============================================================================
# Loop to make 6 clusters
D_list = []
for i in range(6):
    cluster1 = run_dla(500, 1, 0, p5)
    r, C_r = C(cluster1)
    D_list.append(find_D(r,C_r))
    
D_mean = np.mean(D_list)
D_std = np.std(D_list)/(len(D_list))**0.5
print(f"Fractal dimension D = {D_mean} +/- {D_std}")
# =============================================================================
# Finance
# =============================================================================
# def mean_path(x_list):
#     max_len = max(len(x) for x in x_list)
#     padded = [list(x) + [x[-1]] * (max_len - len(x)) for x in x_list]     # Pads out list to avoid list length error
#     # Convert x to a list, then append last value for however many times required to match the length
#     return np.mean(padded, axis=0)

# Pnn = 1; Psnn = 0.5*Pnn

# x_list1 = price_path(p5, 30)            # 30 toy models
# x_list2 = price_path(p5_left, 30)       # p5_left biases upwards, because paths plots x-axis of cluster data only

# fig,(ax1,ax2) = plt.subplots(2,1, figsize=(16,16))
# for x in x_list1:
#     ax1.plot(range(len(x)), x,alpha=0.6)

# mean1 = mean_path(x_list1)
# mean2 = mean_path(x_list2)

# ax1.plot(range(len(mean1)), mean1, 'k-', linewidth=3)
# ax1.set_xticks([]); ax1.set_yticks([])
# ax1.set_title('Stock price evolution for no bias')

# for x in x_list2:
#     ax2.plot(range(len(x)), x)

# mean2 = mean_path(x_list2)
# ax2.plot(range(len(mean2)), mean2, 'k-', linewidth=3)
# ax2.set_xticks([]); ax2.set_yticks([])
# ax2.set_title('Stock price evolution for left bias on x')

# =============================================================================
# Animation
# =============================================================================
# import time
# start = time.time()
# cluster1 = run_dla(5000, 1, 0.5, p5)

# fig, axs = plt.subplots(1,1, figsize=(8,8))

# def update(i):
#     axs.clear()                      # Wipes plot clean each frame, so axis limits update
#     axs.set_aspect('equal')          # Forces square plot
#     axs.text(0.02, 0.95, f'N = {i}, Pnn = 1, Psnn = 0.5', color="white", transform=axs.transAxes, fontsize=10, verticalalignment='top')
#     axs.set_facecolor('#0d0d2b')
#     fig.patch.set_facecolor('#0d0d2b')
    
#     # Formatting
#     axs.set_xlim(-170, 170)
#     axs.set_ylim(-170, 170)
#     axs.set_xticks([]); axs.set_yticks([])
#     axs.axis('off')
    
#     # Zipping through cluster to extract x and y values
#     x, y = zip(*cluster1[1][:i+1])
#     axs.scatter(x,y,s=2, c=np.arange(i+1), cmap='plasma')

# # Freeze the gif at the end so the final cluster can be observed
# N = len(cluster1[1])
# frames = list(range(0, N, 20))
# frames += [N-1] * 30    # 1 second pause at 30 fps (what we're using)


# anime = FuncAnimation(fig, update, frames=frames)
# anime.save('dla.gif', writer=PillowWriter(fps=30))
# print(f"Took {time.time()-start} sec")