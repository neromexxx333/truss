# ============================================================
# APLIKASI ANALISIS RANGKA BATANG FEM 2D
# Menggunakan Python + Streamlit
# Penulis : Ir. Darmansyah Tjitradi, MT., IPU
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# HEADER
# ============================================================

col1, col2 = st.columns([1,5])

with col1:
    st.image("Logo_ULM.png", width=140)

with col2:

    st.markdown("<h2 style='margin-bottom:0'>Analisis Rangka Batang FEM 2D</h2>", unsafe_allow_html=True)
    st.markdown("<h5 style='margin-bottom:0'>Pengembang: Ir. Darmansyah Tjitradi, M.T., IPU</h5>", unsafe_allow_html=True)
    st.markdown("<h5 style='margin-top:0'>Fakultas Teknik Universitas Lambung Mangkurat</h5>", unsafe_allow_html=True)

    st.warning("""
    Aplikasi ini dikembangkan untuk pembelajaran dan penelitian metode elemen hingga.
    Hasil analisis harus diverifikasi oleh insinyur profesional sebelum digunakan untuk perancangan struktur.
    """)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
"<p style='font-size:28px;font-weight:bold;text-align:center'>Skala Deformasi</p>",
unsafe_allow_html=True
)

scale = st.sidebar.slider(" ",1,1000,25,1)

st.sidebar.markdown(
f"<p style='font-size:36px;font-weight:bold;text-align:center'>{scale}</p>",
unsafe_allow_html=True
)

# ============================================================
# UPLOAD FILE
# ============================================================

uploaded = st.file_uploader("Upload file Excel input data",type=["xlsx"])

# ============================================================
# PROGRAM SETELAH FILE DIUPLOAD
# ============================================================

if uploaded:

    # ========================================================
    # MEMBACA DATA
    # ========================================================

    node_df = pd.read_excel(uploaded, sheet_name="nodes")
    elem_df = pd.read_excel(uploaded, sheet_name="elements")
    load_df = pd.read_excel(uploaded, sheet_name="loads")
    support_df = pd.read_excel(uploaded, sheet_name="tumpuan")

    node_df.columns = node_df.columns.str.lower().str.strip()
    elem_df.columns = elem_df.columns.str.lower().str.strip()
    load_df.columns = load_df.columns.str.lower().str.strip()
    support_df.columns = support_df.columns.str.lower().str.strip()

    node_df = node_df.rename(columns={"x(m)":"x","y(m)":"y"})
    elem_df = elem_df.rename(columns={"a(m2)":"a","e(n/m2)":"e"})
    load_df = load_df.rename(columns={"fx(n)":"fx","fy(n)":"fy"})
    support_df = support_df.rename(columns={"rx":"x","ry":"y"})

    nodes = node_df[["x","y"]].values
    elements = elem_df[["node_i","node_j"]].values.astype(int)-1

    A = elem_df["a"].values
    E = elem_df["e"].values

    n_node = len(nodes)
    n_elem = len(elements)

    # ========================================================
    # VEKTOR GAYA
    # ========================================================

    F = np.zeros(2*n_node)

    for _,row in load_df.iterrows():
        n=int(row["node"])-1
        F[2*n]=row["fx"]
        F[2*n+1]=row["fy"]

    # ========================================================
    # PLOT GEOMETRI
    # ========================================================

    def plot_geometry():

        fig,ax=plt.subplots()

        for n1,n2 in elements:
            ax.plot([nodes[n1][0],nodes[n2][0]],[nodes[n1][1],nodes[n2][1]],"k")

        for i,(x,y) in enumerate(nodes):
            ax.plot(x,y,"ro")
            ax.text(x,y,f"N{i+1}")

        ax.set_title("Geometri Struktur")
        ax.axis("equal")

        return fig

    # ========================================================
    # FUNGSI FEM
    # ========================================================

    def fem():

        K=np.zeros((2*n_node,2*n_node))

        for i,(n1,n2) in enumerate(elements):

            x1,y1=nodes[n1]
            x2,y2=nodes[n2]

            L=np.sqrt((x2-x1)**2+(y2-y1)**2)

            c=(x2-x1)/L
            s=(y2-y1)/L

            k=(E[i]*A[i]/L)*np.array([
                [c*c,c*s,-c*c,-c*s],
                [c*s,s*s,-c*s,-s*s],
                [-c*c,-c*s,c*c,c*s],
                [-c*s,-s*s,c*s,s*s]
            ])

            dof=[2*n1,2*n1+1,2*n2,2*n2+1]

            for a in range(4):
                for b in range(4):
                    K[dof[a],dof[b]]+=k[a,b]

        fixed=[]

        for _,row in support_df.iterrows():

            node=int(row["node"])-1

            if int(row["x"])==1:
                fixed.append(2*node)

            if int(row["y"])==1:
                fixed.append(2*node+1)

        free=list(set(range(2*n_node))-set(fixed))

        Kff=K[np.ix_(free,free)]
        Ff=F[free]

        uf=np.linalg.solve(Kff,Ff)

        u=np.zeros(2*n_node)
        u[free]=uf

        force=[]
        stress=[]
        deform=[]

        for i,(n1,n2) in enumerate(elements):

            x1,y1=nodes[n1]
            x2,y2=nodes[n2]

            L=np.sqrt((x2-x1)**2+(y2-y1)**2)

            c=(x2-x1)/L
            s=(y2-y1)/L

            dof=[2*n1,2*n1+1,2*n2,2*n2+1]

            u_elem=u[dof]

            B=np.array([-c,-s,c,s])/L

            strain=B@u_elem

            delta=strain*L

            sigma=E[i]*strain
            N=sigma*A[i]

            deform.append(delta)
            force.append(N)
            stress.append(sigma)

        R=K@u-F

        return u,np.array(force),np.array(stress),np.array(deform),R,K

    # ========================================================
    # TAB
    # ========================================================

    tab1,tab2,tab3=st.tabs(["Input Data","Output Tabel","Output Gambar"])

    # ========================================================
    # TAB INPUT
    # ========================================================

    with tab1:

        st.subheader("Data Node")
        st.dataframe(node_df)

        st.subheader("Data Elemen")
        st.dataframe(elem_df)

        st.subheader("Data Beban")
        st.dataframe(load_df)

        st.subheader("Data Tumpuan")
        st.dataframe(support_df)

        st.subheader("Geometri Struktur")
        st.pyplot(plot_geometry())

        if st.button("Jalankan Analisis"):

            u,force,stress,deform,R,K=fem()

            st.session_state["u"]=u
            st.session_state["force"]=force
            st.session_state["stress"]=stress
            st.session_state["deform"]=deform
            st.session_state["R"]=R

    # ========================================================
    # TAB TABEL
    # ========================================================

    with tab2:

        if "u" in st.session_state:

            u=st.session_state["u"]
            force=st.session_state["force"]
            stress=st.session_state["stress"]
            deform=st.session_state["deform"]
            R=st.session_state["R"]

            ux=u[0::2]
            uy=u[1::2]

            disp_df=pd.DataFrame({
            "node":np.arange(1,len(ux)+1),
            "ux (mm)":ux*1000,
            "uy (mm)":uy*1000
            })

            st.subheader("Perpindahan Node")
            st.dataframe(disp_df)

            element_df=pd.DataFrame({
            "element":np.arange(1,n_elem+1),
            "gaya (kN)":force/1000,
            "tegangan (MPa)":stress/1e6
            })

            st.subheader("Gaya Batang")
            st.dataframe(element_df)

        else:
            st.info("Jalankan analisis pada tab Input Data")

    # ========================================================
    # TAB GAMBAR
    # ========================================================

    with tab3:

        if "u" in st.session_state:

            u=st.session_state["u"]
            force=st.session_state["force"]

            def plot_deformation():

                fig,ax=plt.subplots()

                new_nodes=np.array(nodes)

                for i in range(n_node):
                    new_nodes[i,0]+=u[2*i]*scale
                    new_nodes[i,1]+=u[2*i+1]*scale

                for i,(n1,n2) in enumerate(elements):

                    color="blue" if force[i]>0 else "red"

                    ax.plot(
                    [new_nodes[n1][0],new_nodes[n2][0]],
                    [new_nodes[n1][1],new_nodes[n2][1]],
                    color,linewidth=3
                    )

                ax.set_title("Diagram Deformasi")
                ax.axis("equal")

                return fig

            st.subheader("Diagram Deformasi Struktur")
            st.pyplot(plot_deformation())

        else:
            st.info("Jalankan analisis terlebih dahulu")
