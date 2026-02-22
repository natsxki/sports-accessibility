# Génération de positions de caméras pour la simulation 3d conversion sphériques à cartésiennes
from math import sin, cos, pi 
import numpy as np 
import matplotlib.pyplot as plt 

def coo_sph_cart(r, t, p): # r, theta, phi
    x = 37.5 + r * sin(p) * cos(t) # centre du terrain situé en (37.5,59.5,0)
    y = 59.5 + r * sin(p) * sin(t) #
    z = r * cos(p) #
    return round(x, 1), round(y, 1), round(z, 1) # on arrondit à un chiffre après virgule

n = 10 
p = 10 

# on fixe r
r = 300 

# theta, phi en radian pour cos, sin
theta = [j/p for j in range(p)] # angle max condition tri points: 1 rad
phi = [(pi/2)/n for i in range(n)] # détection impossible pour t=pi/2 (=au sol)

x_vals = [] #
y_vals = [] #
z_vals = [] #

for i in range(len(theta)): 
    for j in range(len(phi)): 
        x_vals.append(coo_sph_cart(r, theta[i], phi[j])[0]) 
        y_vals.append(coo_sph_cart(r, theta[i], phi[j])[1]) 
        z_vals.append(coo_sph_cart(r, theta[i], phi[j])[2]) 

# Représentation graphique
fig = plt.figure() 
ax = plt.axes(projection='3d') 

surf = ax.plot_trisurf(np.array(x_vals), np.array(y_vals), np.array(z_vals), linewidth=0, antialiased=True, cmap='summer') 
ax.set_title('Représentation visuelle des coordonnées générées') 
plt.show() 