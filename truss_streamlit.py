# ============================================================
# APLIKASI ANALISIS RANGKA BATANG FEM 2D
# Menggunakan Python + Streamlit
# Penulis : Ir. Darmansyah Tjitradi, MT., IPU
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False
    
# ============================================================
# JUDUL APLIKASI
# ============================================================

# ============================================================
# HEADER DENGAN LOGO
# ============================================================

col1, col2 = st.columns([1,5])

with col1:
    st.image("Logo_ULM.png", width=150)

with col2:
    
    st.markdown(
    "<h2 style='margin-bottom:0;'>Analisis Rangka Batang FEM 2D</h2>",
    unsafe_allow_html=True
    )
    
    st.markdown(
    "<h5 style='margin-bottom:0;'>Pengembang: Ir. Darmansyah Tjitradi, M.T., IPU</h5>",
    unsafe_allow_html=True
    )

    st.markdown(
    "<h5 style='margin-top:0;'>Fakultas Teknik Universitas Lambung Mangkurat</h5>",
    unsafe_allow_html=True
    )

    st.markdown(
    "<h5 style='text-align:left'>========================================================</h5>",
    unsafe_allow_html=True
    )

    st.markdown(
    "<h5 style='margin-top:0;'>Disclaimer:</h5>",
    unsafe_allow_html=True
    )    
    
    st.warning(
    """
    - Aplikasi ini dikembangkan sebagai alat bantu pembelajaran dan penelitian dalam analisis struktur menggunakan Metode Elemen Hingga (Finite Element Method).
    
    - Hasil analisis harus diverifikasi lebih lanjut oleh insinyur profesional yang kompeten sebelum digunakan dalam perancangan struktur.
    
    - Pengguna bertanggung jawab sepenuhnya atas interpretasi dan penggunaan hasil analisis yang diperoleh dari aplikasi ini.
    """
    )


# ============================================================
# KONTROL SKALA DEFORMASI
# ============================================================

st.sidebar.markdown(
    "<p style='font-size:30px;font-weight:bold;text-align:center'>Skala Deformasi</p>",
    unsafe_allow_html=True
)

if "scale" not in st.session_state:
    st.session_state.scale = 25
    
scale = st.sidebar.slider(
    " ",
    min_value=1,
    max_value=1000,
    step=1,
    key="scale"
)

st.sidebar.markdown(
    f"<p style='font-size:40px;font-weight:bold;text-align:center'>{scale}</p>",
    unsafe_allow_html=True
)


# ============================================================
# UPLOAD FILE EXCEL
# ============================================================

uploaded = st.file_uploader("Upload file input data dalam format Excel:", type=["xlsx"])

if "last_file" not in st.session_state:
    st.session_state.last_file = None

if uploaded is not None:

    # jika file baru diupload maka reset kondisi analisis
    if uploaded != st.session_state.last_file:

        st.session_state.last_file = uploaded
        st.session_state.run_analysis = False
        st.session_state.izin_analisis = False

        # reset skala deformasi ke default
        if "scale" in st.session_state:
            del st.session_state["scale"] 
        
        # reset hasil FEM
        for key in ["u", "force", "stress", "deform", "R", "K"]:
            if key in st.session_state:
                del st.session_state[key]

# ============================================================
# PROGRAM DIJALANKAN SETELAH FILE DIUPLOAD
# ============================================================

if uploaded:

    # ========================================================
    # MEMBACA DATA DARI EXCEL
    # ========================================================

    node_df = pd.read_excel(uploaded, sheet_name="nodes")
    elem_df = pd.read_excel(uploaded, sheet_name="elements")
    load_df = pd.read_excel(uploaded, sheet_name="loads")
    support_df = pd.read_excel(uploaded, sheet_name="tumpuan")

    # normalisasi nama kolom
    node_df.columns = node_df.columns.str.lower().str.strip()
    elem_df.columns = elem_df.columns.str.lower().str.strip()
    load_df.columns = load_df.columns.str.lower().str.strip()
    support_df.columns = support_df.columns.str.lower().str.strip()

    # rename agar konsisten
    node_df = node_df.rename(columns={"x(m)": "x", "y(m)": "y"})
    elem_df = elem_df.rename(columns={"a(m2)": "a", "e(n/m2)": "e"})
    load_df = load_df.rename(columns={"fx(n)": "fx", "fy(n)": "fy"})

    support_df = support_df.rename(columns={
        "rx": "x",
        "ry": "y",
    })


    # ========================================================
    # KONVERSI DATA KE ARRAY NUMPY
    # ========================================================

    nodes = node_df[["x", "y"]].values
    elements = elem_df[["node_i", "node_j"]].values.astype(int) - 1

    A = elem_df["a"].values
    E = elem_df["e"].values

    n_node = len(nodes)
    n_elem = len(elements)


    # ========================================================
    # FORMAT TABEL UNTUK TAMPILAN
    # ========================================================

    elem_display = elem_df.rename(columns={"a": "A(m2)", "e": "E(N/m2)"})
    load_display = load_df.rename(columns={"fx": "Fx(N)", "fy": "Fy(N)"})
    support_display = support_df.rename(columns={"x": "Rx", "y": "Ry"})

    css = [
        {"selector": "table", "props": [("table-layout", "auto"), ("width", "100%")]},
        {"selector": "th", "props": [("text-align", "center")]}
    ]


    # ========================================================
    # TABEL DATA NODE
    # ========================================================

    # dataframe khusus untuk tampilan
    node_display = node_df.rename(columns={
        "x": "x(m)",
        "y": "y(m)"
    })

    styled_node = (
        node_display.style
        .set_properties(subset=["node"], **{"text-align": "center"})
        .set_properties(subset=["x(m)", "y(m)"], **{"text-align": "right"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Node")
    st.markdown(styled_node.to_html(), unsafe_allow_html=True)


    # ========================================================
    # TABEL DATA ELEMEN
    # ========================================================

    styled_elem = (
        elem_display.style
        .set_properties(subset=["element", "node_i", "node_j"], **{"text-align": "center"})
        .set_properties(subset=["A(m2)", "E(N/m2)"], **{"text-align": "right"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Elemen")
    st.markdown(styled_elem.to_html(), unsafe_allow_html=True)


    # ========================================================
    # TABEL DATA BEBAN NODAL
    # ========================================================

    styled_load = (
        load_display.style
        .set_properties(subset=["node"], **{"text-align": "center"})
        .set_properties(subset=["Fx(N)", "Fy(N)"], **{"text-align": "right"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Beban Nodal")
    st.markdown(styled_load.to_html(), unsafe_allow_html=True)


    # ========================================================
    # TABEL DATA TUMPUAN
    # ========================================================

    styled_support = (
        support_display.style
        .set_properties(subset=["node", "Rx", "Ry"], **{"text-align": "center"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Tumpuan")
    st.markdown(styled_support.to_html(), unsafe_allow_html=True)

# ============================================================
# VALIDASI KESTABILAN STRUKTUR
# ============================================================

    def check_stability():

        m = n_elem
        j = n_node

        r = 0
        for _, row in support_df.iterrows():
            r += int(row["x"]) + int(row["y"])

        det = m + r - 2*j
        stab = m - (2*j - 3)

        if "izin_analisis" not in st.session_state:
            st.session_state.izin_analisis = False

        st.subheader("Evaluasi Struktur")

        # ------------------------------------------------
        # CEK KESTABILAN EKSTERNAL
        # ------------------------------------------------

        if det < 0:
            st.error("Struktur tidak stabil secara eksternal (m + r < 2j)")
            st.session_state.izin_analisis = False
            st.stop()

        # ------------------------------------------------
        # INFORMASI DETERMINASI
        # ------------------------------------------------

        if det == 0:
            st.success("Struktur statis tertentu")
        else:
            st.info("Struktur statis tak tentu")

        # ------------------------------------------------
        # CEK STABILITAS INTERNAL
        # ------------------------------------------------

        if stab < 0:

            st.warning("Sistem rangka tidak stabil (mekanisme)")

            if st.checkbox("Tetap lanjutkan analisis"):
                st.session_state.izin_analisis = True
            else:
                st.session_state.izin_analisis = False
                st.stop()

        else:
            st.success("Struktur stabil")
            st.session_state.izin_analisis = True

            
    # ========================================================
    # MEMBENTUK VEKTOR GAYA GLOBAL
    # ========================================================

    F = np.zeros(2 * n_node)

    for _, row in load_df.iterrows():

        n = int(row["node"]) - 1
        F[2 * n] = row["fx"]
        F[2 * n + 1] = row["fy"]


    # ========================================================
    # PLOT GEOMETRI STRUKTUR
    # ========================================================

    def plot_geometry():

            fig, ax = plt.subplots()

            xmin, xmax = nodes[:,0].min(), nodes[:,0].max()
            ymin, ymax = nodes[:,1].min(), nodes[:,1].max()

            offset = 0.01 * max(xmax-xmin, ymax-ymin)
            scale_arrow = 0.08 * max(xmax-xmin, ymax-ymin)

            # gambar batang
            for i,(n1,n2) in enumerate(elements):

                x=[nodes[n1][0],nodes[n2][0]]
                y=[nodes[n1][1],nodes[n2][1]]

                ax.plot(x,y,"k")

                xm=(x[0]+x[1])/2
                ym=(y[0]+y[1])/2

                ax.text(xm,ym+offset,f"E{i+1}",color="blue",ha="center")

            # gambar node
            for i,(x,y) in enumerate(nodes):

                ax.plot(x,y,"ro")
                ax.text(x+offset,y+offset,f"N{i+1}",color="red")

# ========================================================
# GAMBAR SIMBOL TUMPUAN
# ========================================================

            for _, row in support_df.iterrows():

                node = int(row["node"]) - 1
                x, y = nodes[node]

                rx = int(row["x"])
                ry = int(row["y"])

                size = 0.04 * max(xmax-xmin, ymax-ymin)

                # -----------------------------
                # TUMPUAN SENDI
                # -----------------------------
                if rx == 1 and ry == 1:

                    triangle = plt.Polygon(
                        [
                            (x-size, y-size),
                            (x+size, y-size),
                            (x, y)
                        ],
                        color="black"
                    )

                    ax.add_patch(triangle)


                # -----------------------------
                # TUMPUAN ROL VERTIKAL
                # -----------------------------
                elif rx == 0 and ry == 1:

                    triangle = plt.Polygon(
                        [
                            (x-size, y-size),
                            (x+size, y-size),
                            (x, y)
                        ],
                        facecolor="black"
                    )

                    circle = plt.Circle(
                        (x, y-size*1.3),
                        size*0.35,
                        facecolor="black"
                    )

                    ax.add_patch(triangle)

                    circle = plt.Circle(
                        (x, y - size * 1.3),
                        size * 0.35,
                        facecolor="black",
                        edgecolor="black",
                        zorder=2
                    )

                    ax.plot(x, y, "ro", zorder=3)

                    ax.add_patch(circle)


                # -----------------------------
                # ROL HORIZONTAL
                # -----------------------------
                elif rx == 1 and ry == 0:

                    triangle = plt.Polygon(
                        [
                            (x, y-size),
                            (x, y+size),
                            (x-size, y)
                        ],
                        facecolor="black"
                    )

                    circle = plt.Circle(
                        (x, y - size * 1.3),
                        size * 0.35,
                        facecolor="black",
                        edgecolor="black",
                        zorder=2
                    )

                    ax.plot(x, y, "ro", zorder=3)

                    ax.add_patch(triangle)

                    circle = plt.Circle(
                        (x-size*1.3, y),
                        size*0.35,
                        fill=False,
                        color="black"
                    )

                    ax.add_patch(circle)

            # gambar beban
            for _,row in load_df.iterrows():

                node=int(row["node"])-1
                fx=row["fx"]
                fy=row["fy"]

                x,y=nodes[node]

                if abs(fx)>0:
                    direction=np.sign(fx)

                    ax.arrow(
                        x,y,
                        direction*scale_arrow,0,
                        head_width=0.04*scale_arrow,
                        color="green",
                        length_includes_head=True
                    )

                    ax.text(
                        x+direction*scale_arrow,
                        y,
                        f"{fx/1000:.1f} kN",
                        color="green"
                    )

                if abs(fy)>0:
                    direction=np.sign(fy)

                    ax.arrow(
                        x,y,
                        0,direction*scale_arrow,
                        head_width=0.04*scale_arrow,
                        color="green",
                        length_includes_head=True
                    )

                    ax.text(
                        x,
                        y+direction*scale_arrow,
                        f"{fy/1000:.1f} kN",
                        color="green"
                    )

            ax.set_title("Geometri Struktur Rangka")
            ax.axis("equal")

            return fig


    st.subheader("Geometri Struktur Rangka")
    st.pyplot(plot_geometry())


    # ========================================================
    # FUNGSI ANALISIS FEM
    # ========================================================

    def fem():

        # matriks kekakuan global
        K = np.zeros((2 * n_node, 2 * n_node))

        for i, (n1, n2) in enumerate(elements):

            x1, y1 = nodes[n1]
            x2, y2 = nodes[n2]

            L = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            c = (x2 - x1) / L
            s = (y2 - y1) / L

            k = (E[i] * A[i] / L) * np.array([
                [c * c, c * s, -c * c, -c * s],
                [c * s, s * s, -c * s, -s * s],
                [-c * c, -c * s, c * c, c * s],
                [-c * s, -s * s, c * s, s * s]
            ])

            dof = [2 * n1, 2 * n1 + 1, 2 * n2, 2 * n2 + 1]

            for a in range(4):
                for b in range(4):
                    K[dof[a], dof[b]] += k[a, b]


        # menentukan DOF yang dikunci
        fixed = []

        for _, row in support_df.iterrows():

            node = int(row["node"]) - 1

            if int(row["x"]) == 1:
                fixed.append(2 * node)

            if int(row["y"]) == 1:
                fixed.append(2 * node + 1)


        free = list(set(range(2 * n_node)) - set(fixed))


        # sistem persamaan
        Kff = K[np.ix_(free, free)]
        Ff = F[free]

        try:
            uf = np.linalg.solve(Kff, Ff)
        except np.linalg.LinAlgError:
            st.error("Matriks kekakuan singular. Struktur kemungkinan tidak stabil atau tumpuan tidak cukup.")
            st.stop()

        u = np.zeros(2 * n_node)
        u[free] = uf


        # gaya batang
        force = []
        stress = []
        deform = []

        for i, (n1, n2) in enumerate(elements):

            x1, y1 = nodes[n1]
            x2, y2 = nodes[n2]

            L = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            c = (x2 - x1) / L
            s = (y2 - y1) / L

            dof = [2 * n1, 2 * n1 + 1, 2 * n2, 2 * n2 + 1]

            u_elem = u[dof]

            B = np.array([-c, -s, c, s]) / L

            strain = B @ u_elem

            delta = strain * L

            sigma = E[i] * strain
            N = sigma * A[i]

            deform.append(delta)
            force.append(N)
            stress.append(sigma)


        # hitung reaksi tumpuan
        R = K @ u - F

        return u, np.array(force), np.array(stress), np.array(deform), R, K


    # ========================================================
    # MENJALANKAN ANALISIS
    # ========================================================

    st.markdown("""
    <style>
    div.stButton > button {
        font-size: 24px;
        font-weight: bold;
        padding: 14px 28px;
    }
    </style>
    """, unsafe_allow_html=True)

    # tombol analisis   
    if st.button("Jalankan Analisis"):
        st.session_state.run_analysis = True
    
    # jalankan analisis jika status aktif
    if st.session_state.run_analysis:

        check_stability()

        if st.session_state.get("izin_analisis", False):

            u, force, stress, deform, R, K = fem()

            st.session_state.u = u
            st.session_state.force = force
            st.session_state.stress = stress
            st.session_state.deform = deform
            st.session_state.R = R
            st.session_state.K = K

        if not st.session_state.get("izin_analisis", False):
            st.stop()
    
        # ====================================================
        # PERPINDAHAN NODE
        # ====================================================

        ux = u[0::2]
        uy = u[1::2]

        disp_df = pd.DataFrame({
            "node": np.arange(1, len(ux) + 1),
            "ux (mm)": ux * 1000,
            "uy (mm)": uy * 1000
        })

        styled_disp = (
            disp_df.style
            .format({"ux (mm)": "{:.4f}", "uy (mm)": "{:.4f}"})
            .set_properties(subset=["node"], **{"text-align": "center"})
            .set_properties(subset=["ux (mm)", "uy (mm)"], **{"text-align": "right"})
            .set_table_styles(css)
            .hide(axis="index")
        )

        st.subheader("Perpindahan Node")
        st.markdown(styled_disp.to_html(), unsafe_allow_html=True)


        # ====================================================
        # GAYA AKSIAL BATANG
        # ====================================================

        element_result = pd.DataFrame({
            "element": np.arange(1, n_elem + 1),
            "node_i": elements[:, 0] + 1,
            "node_j": elements[:, 1] + 1,
            "Deformasi Aksial (mm)": deform * 1000,
            "Gaya Aksial (kN)": force/1000,
            "Tegangan Aksial (MPa)": stress / 1e6
        })

        styled_table = (
            element_result.style
            .format({
                "Deformasi Aksial (mm)": "{:.4f}",
                "Gaya Aksial (kN)": "{:.4f}",
                "Tegangan Aksial (MPa)": "{:.4f}"
            })
            .set_properties(subset=["element", "node_i", "node_j"], **{"text-align": "center"})
            .set_properties(
                subset=["Deformasi Aksial (mm)", "Gaya Aksial (kN)", "Tegangan Aksial (MPa)"],
                **{"text-align": "right"}
            )
            .set_table_styles(css)
            .hide(axis="index")
        )

        st.subheader("Gaya Aksial dan Tegangan Batang")
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)

        # ====================================================
        # REAKSI TUMPUAN
        # ====================================================

        reaction_data = []

        for _, row in support_df.iterrows():

            node = int(row["node"]) - 1

            rx = 0
            ry = 0

            if int(row["x"]) == 1:
                rx = R[2 * node]
                if abs(rx) < 1e-9:
                    rx = 0

            if int(row["y"]) == 1:
                ry = R[2 * node + 1]
                if abs(ry) < 1e-9:
                    ry = 0

            reaction_data.append([
                node + 1,
                rx / 1000,
                ry / 1000
            ])

        reaction_df = pd.DataFrame(
            reaction_data,
            columns=["node", "Rx (kN)", "Ry (kN)"]
        )

        # ====================================================
        # KESEIMBANGAN GAYA GLOBAL
        # ====================================================

        sumFx = float(np.sum(F[0::2]) + np.sum(R[0::2]))
        sumFy = float(np.sum(F[1::2]) + np.sum(R[1::2]))

        balance_row = pd.DataFrame(
            [["ΣF", sumFx/1000, sumFy/1000]],
            columns=["node", "Rx (kN)", "Ry (kN)"]
        )

        reaction_df = pd.concat([reaction_df, balance_row], ignore_index=True)

        styled_reaction = (
            reaction_df.style
            .format({
                "Rx (kN)": "{:.4f}",
                "Ry (kN)": "{:.4f}"
            })
            .set_properties(subset=["node"], **{"text-align": "center"})
            .set_properties(subset=["Rx (kN)", "Ry (kN)"], **{"text-align": "right"})
            .set_table_styles(css)
            .hide(axis="index")
        )

        st.subheader("Reaksi Tumpuan")
        st.markdown(styled_reaction.to_html(), unsafe_allow_html=True)

# ====================================================
# VISUALISASI REAKSI TUMPUAN
# ====================================================

        def plot_reaction():

            fig, ax = plt.subplots()

            xmin, xmax = nodes[:,0].min(), nodes[:,0].max()
            ymin, ymax = nodes[:,1].min(), nodes[:,1].max()

            offset = 0.01 * max(xmax-xmin, ymax-ymin)

            # gambar rangka
            for (n1,n2) in elements:

                ax.plot(
                    [nodes[n1][0], nodes[n2][0]],
                    [nodes[n1][1], nodes[n2][1]],
                    "k"
                )

            # gambar node
            for i,(x,y) in enumerate(nodes):

                ax.plot(x,y,"ro")
                ax.text(x+offset,y+offset,f"N{i+1}",color="red")

            # gambar reaksi
            for _,row in support_df.iterrows():

                node = int(row["node"]) - 1
                x,y = nodes[node]

                rx = 0
                ry = 0

                if int(row["x"]) == 1:
                    rx = R[2*node]

                if int(row["y"]) == 1:
                    ry = R[2*node+1]

                # normalisasi panjang panah agar tidak terlalu besar
                mag = np.sqrt(rx**2 + ry**2)

                if mag > 0:
                    scale_arrow = 0.2 * max(xmax-xmin, ymax-ymin)

                    ax.arrow(
                        x,
                        y,
                        scale_arrow * rx/mag,
                        scale_arrow * ry/mag,
                        head_width=0.05*scale_arrow,
                        color="green",
                        length_includes_head=True
                    )

                    ax.text(
                        x + scale_arrow * rx/mag,
                        y + scale_arrow * ry/mag,
                        f"{mag/1000:.1f} kN",
                        color="green"
                    )

            ax.set_title("Reaksi Tumpuan Struktur Rangka")
            ax.axis("equal")

            return fig

        st.subheader("Reaksi Tumpuan Struktur Rangka")
        st.pyplot(plot_reaction())

        # ====================================================
        # VISUALISASI REAKSI GLOBAL (Rx dan Ry)
        # ====================================================

        def plot_reaction_components():

            fig, ax = plt.subplots()

            xmin, xmax = nodes[:,0].min(), nodes[:,0].max()
            ymin, ymax = nodes[:,1].min(), nodes[:,1].max()

            offset = 0.01 * max(xmax-xmin, ymax-ymin)
            scale_arrow = 0.2 * max(xmax-xmin, ymax-ymin)

            # gambar batang
            for (n1,n2) in elements:

                ax.plot(
                    [nodes[n1][0],nodes[n2][0]],
                    [nodes[n1][1],nodes[n2][1]],
                    "k"
                )

            # gambar node
            for i,(x,y) in enumerate(nodes):

                ax.plot(x,y,"ro")
                ax.text(x+offset,y+offset,f"N{i+1}",color="red")

            # gambar komponen reaksi
            for _,row in support_df.iterrows():

                node = int(row["node"]) - 1
                x,y = nodes[node]

                rx = 0
                ry = 0

                if int(row["x"]) == 1:
                    rx = R[2*node]

                if int(row["y"]) == 1:
                    ry = R[2*node+1]

                # panah arah X
                if abs(rx) > 0:

                    direction = np.sign(rx)

                    ax.arrow(
                        x,
                        y,
                        direction * scale_arrow,
                        0,
                        head_width=0.05*scale_arrow,
                        color="blue",
                        length_includes_head=True
                    )

                    ax.text(
                        x + direction * scale_arrow,
                        y,
                        f"Rx={rx/1000:.1f} kN",
                        color="blue"
                    )

                # panah arah Y
                if abs(ry) > 0:

                    direction = np.sign(ry)

                    ax.arrow(
                        x,
                        y,
                        0,
                        direction * scale_arrow,
                        head_width=0.05*scale_arrow,
                        color="green",
                        length_includes_head=True
                    )

                    ax.text(
                        x,
                        y + direction * scale_arrow,
                        f"Ry={ry/1000:.1f} kN",
                        color="green"
                    )

            ax.set_title("Reaksi Tumpuan Struktur Rangka (Sumbu Global)")
            ax.axis("equal")

            return fig

        st.subheader("Reaksi Tumpuan Struktur Rangka (Sumbu Global)")
        st.pyplot(plot_reaction_components())


# ====================================================
# DIAGRAM GAYA BATANG + NOMOR NODE
# ====================================================

        def plot_force():

            fig, ax = plt.subplots()

            xmin, xmax = nodes[:, 0].min(), nodes[:, 0].max()
            ymin, ymax = nodes[:, 1].min(), nodes[:, 1].max()

            offset = 0.01 * max(xmax - xmin, ymax - ymin)

            # -----------------------------------------------
            # gambar batang dengan warna tarik dan tekan
            # -----------------------------------------------

            for i, (n1, n2) in enumerate(elements):

                x1, y1 = nodes[n1]
                x2, y2 = nodes[n2]

                color = "blue" if force[i] > 0 else "red"

                ax.plot([x1, x2], [y1, y2], color, linewidth=3)

                xm = (x1 + x2) / 2
                ym = (y1 + y2) / 2

                L = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                nx = -(y2 - y1) / L
                ny = (x2 - x1) / L

                ax.text(
                    xm + offset * nx,
                    ym + offset * ny,
                    f"{force[i] / 1000:.1f} kN",
                    ha="center"
                )

            # -----------------------------------------------
            # gambar node
            # -----------------------------------------------

            for i, (x, y) in enumerate(nodes):

                ax.plot(x, y, "ko")

                ax.text(
                    x + offset,
                    y + offset,
                    f"N{i+1}",
                    color="black"
                )

            ax.set_title("Diagram Gaya Batang (Batang Tarik: Biru, Batang Tekan: Merah)")
            ax.axis("equal")

            return fig
        
        st.subheader("Diagram Gaya Batang Stuktur Rangka")
        st.pyplot(plot_force())

        # ====================================================
        # DIAGRAM DEFORMASI
        # ====================================================

        def plot_deformation():

            fig,ax=plt.subplots()

            xmin,xmax = nodes[:,0].min(),nodes[:,0].max()
            ymin,ymax = nodes[:,1].min(),nodes[:,1].max()

            offset = 0.01*max(xmax-xmin,ymax-ymin)

            # struktur asli
            for (n1,n2) in elements:

                ax.plot(
                    [nodes[n1][0],nodes[n2][0]],
                    [nodes[n1][1],nodes[n2][1]],
                    "k--"
                )

            new_nodes = np.array(nodes,dtype=float)

            for i in range(n_node):

                new_nodes[i,0]+=u[2*i]*scale
                new_nodes[i,1]+=u[2*i+1]*scale

            # struktur deformasi
            for i,(n1,n2) in enumerate(elements):

                x1,y1 = new_nodes[n1]
                x2,y2 = new_nodes[n2]

                # warna berdasarkan gaya batang
                color = "blue" if force[i] > 0 else "red"

                ax.plot(
                    [x1,x2],
                    [y1,y2],
                    color,
                    linewidth=3
                )

                # label elemen
                xm=(x1+x2)/2
                ym=(y1+y2)/2

                ax.text(xm,ym+offset,f"E{i+1}",color="blue",ha="center")

            # label node
            for i,(x,y) in enumerate(new_nodes):

                ax.plot(x,y,"ro")
                ax.text(x+offset,y+offset,f"N{i+1}",color="red")

            ax.set_title("Diagram Deformasi Struktur Rangka")
            ax.axis("equal")

            return fig

        st.subheader("Diagram Deformasi Struktur Rangka")
        st.pyplot(plot_deformation())
