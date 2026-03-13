import numpy as np
import matplotlib.pyplot as plt

# ======================
# DATA MATERIAL
# ======================

E = 200e9
rho = 7850

# ======================
# GEOMETRI STRUKTUR
# ======================

nodes = np.array([
[0,0],
[5,0],
[10,0],
[2.5,3],
[7.5,3]
])

elements = [
(0,3),
(1,3),
(1,4),
(2,4),
(3,4),
(0,1),
(1,2)
]

n_node = len(nodes)
n_elem = len(elements)

# ======================
# LUAS PENAMPANG
# ======================

A = np.ones(n_elem)*0.005

# ======================
# BEBAN
# ======================

F = np.zeros(2*n_node)
F[7] = -100000
F[9] = -100000

# ======================
# FEM ANALYSIS
# ======================

def fem_analysis():

    K = np.zeros((2*n_node,2*n_node))

    for i,(n1,n2) in enumerate(elements):

        x1,y1 = nodes[n1]
        x2,y2 = nodes[n2]

        L = np.sqrt((x2-x1)**2 + (y2-y1)**2)

        c = (x2-x1)/L
        s = (y2-y1)/L

        k = (E*A[i]/L)*np.array([
        [c*c,c*s,-c*c,-c*s],
        [c*s,s*s,-c*s,-s*s],
        [-c*c,-c*s,c*c,c*s],
        [-c*s,-s*s,c*s,s*s]
        ])

        dof = [2*n1,2*n1+1,2*n2,2*n2+1]

        for a in range(4):
            for b in range(4):
                K[dof[a],dof[b]] += k[a,b]

    fixed = [0,1,4,5]

    free = list(set(range(2*n_node)) - set(fixed))

    Kff = K[np.ix_(free,free)]
    Ff = F[free]

    uf = np.linalg.solve(Kff,Ff)

    u = np.zeros(2*n_node)
    u[free] = uf

    stress = []
    force = []

    for i,(n1,n2) in enumerate(elements):

        x1,y1 = nodes[n1]
        x2,y2 = nodes[n2]

        L = np.sqrt((x2-x1)**2 + (y2-y1)**2)

        c = (x2-x1)/L
        s = (y2-y1)/L

        dof = [2*n1,2*n1+1,2*n2,2*n2+1]

        u_elem = u[dof]

        B = np.array([-c,-s,c,s])/L

        strain = B @ u_elem

        sigma = E*strain
        N = sigma*A[i]

        stress.append(sigma)
        force.append(N)

    return u, np.array(force), np.array(stress)

# ======================
# VISUALISASI
# ======================

def plot_truss(u,scale=100):

    plt.figure()

    # bentuk awal
    for (n1,n2) in elements:

        x = [nodes[n1][0],nodes[n2][0]]
        y = [nodes[n1][1],nodes[n2][1]]

        plt.plot(x,y,'k--')

    # bentuk deformasi
    new_nodes = nodes.copy()

    for i in range(n_node):

        new_nodes[i,0] += u[2*i]*scale
        new_nodes[i,1] += u[2*i+1]*scale

    for (n1,n2) in elements:

        x = [new_nodes[n1][0],new_nodes[n2][0]]
        y = [new_nodes[n1][1],new_nodes[n2][1]]

        plt.plot(x,y,'r')

    plt.title("Deformasi Rangka Batang")
    plt.axis('equal')
    plt.show()

# ======================
# ANALISIS
# ======================

u,force,stress = fem_analysis()

print("\nPERPINDAHAN NODE")

for i in range(n_node):

    ux = u[2*i]
    uy = u[2*i+1]

    print("Node",i,"Ux =",ux,"Uy =",uy)

print("\nGAYA AKSIAL BATANG")

for i,f in enumerate(force):

    print("Batang",i,"=",f,"N")

print("\nTEGANGAN AKSIAL BATANG")

for i,s in enumerate(stress):

    print("Batang",i,"=",s,"Pa")

plot_truss(u)