import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Analisis Rangka Batang FEM")

scale = st.sidebar.slider(
    "Skala deformasi",
    min_value=1,
    max_value=1000,
    value=100,
    step=1
)

uploaded = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded:

    node_df = pd.read_excel(uploaded, sheet_name="nodes")
    elem_df = pd.read_excel(uploaded, sheet_name="elements")
    load_df = pd.read_excel(uploaded, sheet_name="loads")
    support_df = pd.read_excel(uploaded, sheet_name="tumpuan")

    node_df.columns = node_df.columns.str.lower().str.strip()
    elem_df.columns = elem_df.columns.str.lower().str.strip()
    load_df.columns = load_df.columns.str.lower().str.strip()
    support_df.columns = support_df.columns.str.lower().str.strip()

    node_df = node_df.rename(columns={"x(m)": "x", "y(m)": "y"})
    elem_df = elem_df.rename(columns={"a(m2)": "a", "e(n/m2)": "e"})
    load_df = load_df.rename(columns={"fx(n)": "fx", "fy(n)": "fy"})

    support_df = support_df.rename(columns={
        "rx": "x",
        "ry": "y",
    })

    nodes = node_df[["x", "y"]].values
    elements = elem_df[["node_i", "node_j"]].values.astype(int) - 1

    A = elem_df["a"].values
    E = elem_df["e"].values

    n_node = len(nodes)
    n_elem = len(elements)

    elem_display = elem_df.rename(columns={"a": "A(m2)", "e": "E(N/m2)"})
    load_display = load_df.rename(columns={"fx": "Fx(N)", "fy": "Fy(N)"})
    support_display = support_df.rename(columns={
    "x": "Rx",
    "y": "Ry"
    })

    css = [
        {"selector": "table", "props": [("table-layout", "auto"), ("width", "100%")]},
        {"selector": "th", "props": [("text-align", "center")]}
    ]

    styled_node = (
        node_df.style
        .set_properties(subset=["node"], **{"text-align": "center"})
        .set_properties(subset=["x", "y"], **{"text-align": "right"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Node")
    st.markdown(styled_node.to_html(), unsafe_allow_html=True)

    styled_elem = (
        elem_display.style
        .set_properties(subset=["element", "node_i", "node_j"], **{"text-align": "center"})
        .set_properties(subset=["A(m2)", "E(N/m2)"], **{"text-align": "right"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Elemen")
    st.markdown(styled_elem.to_html(), unsafe_allow_html=True)

    styled_load = (
        load_display.style
        .set_properties(subset=["node"], **{"text-align": "center"})
        .set_properties(subset=["Fx(N)", "Fy(N)"], **{"text-align": "right"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Beban")
    st.markdown(styled_load.to_html(), unsafe_allow_html=True)

    styled_support = (
        support_display.style
        .set_properties(subset=["node","Rx","Ry"], **{"text-align": "center"})
        .set_table_styles(css)
        .hide(axis="index")
    )

    st.subheader("Data Tumpuan")
    st.markdown(styled_support.to_html(), unsafe_allow_html=True)

    F = np.zeros(2 * n_node)

    for _, row in load_df.iterrows():
        n = int(row["node"]) - 1
        F[2 * n] = row["fx"]
        F[2 * n + 1] = row["fy"]

    def plot_geometry():

        fig, ax = plt.subplots()

        xmin, xmax = nodes[:, 0].min(), nodes[:, 0].max()
        ymin, ymax = nodes[:, 1].min(), nodes[:, 1].max()

        offset = 0.02 * max(xmax - xmin, ymax - ymin)

        for i, (n1, n2) in enumerate(elements):

            x = [nodes[n1][0], nodes[n2][0]]
            y = [nodes[n1][1], nodes[n2][1]]

            ax.plot(x, y, "k")

            xm = (x[0] + x[1]) / 2
            ym = (y[0] + y[1]) / 2

            ax.text(xm, ym + offset, f"E{i+1}", color="blue", ha="center")

        for i, (x, y) in enumerate(nodes):

            ax.plot(x, y, "ro")
            ax.text(x + offset, y + offset, f"N{i+1}", color="red")

        ax.set_title("Geometri Rangka")
        ax.axis("equal")

        return fig

    st.subheader("Geometri Rangka")
    st.pyplot(plot_geometry())

    def fem():

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

        fixed = []

        for _, row in support_df.iterrows():

            node = int(row["node"]) - 1

            if int(row["x"]) == 1:
                fixed.append(2 * node)

            if int(row["y"]) == 1:
                fixed.append(2 * node + 1)

        free = list(set(range(2 * n_node)) - set(fixed))

        Kff = K[np.ix_(free, free)]
        Ff = F[free]

        uf = np.linalg.solve(Kff, Ff)

        u = np.zeros(2 * n_node)
        u[free] = uf

        force = []
        stress = []

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
            sigma = E[i] * strain
            N = sigma * A[i]

            force.append(N)
            stress.append(sigma)

        return u, np.array(force), np.array(stress)

    if st.button("Jalankan Analisis"):

        u, force, stress = fem()

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

        element_result = pd.DataFrame({
            "element": np.arange(1, n_elem + 1),
            "node_i": elements[:, 0] + 1,
            "node_j": elements[:, 1] + 1,
            "Gaya Aksial (N)": force,
            "Tegangan Aksial (MPa)": stress / 1e6
        })

        styled_table = (
            element_result.style
            .format({
                "Gaya Aksial (N)": "{:.4f}",
                "Tegangan Aksial (MPa)": "{:.4f}"
            })
            .set_properties(subset=["element", "node_i", "node_j"], **{"text-align": "center"})
            .set_properties(subset=["Gaya Aksial (N)", "Tegangan Aksial (MPa)"], **{"text-align": "right"})
            .set_table_styles(css)
            .hide(axis="index")
        )

        st.subheader("Gaya Aksial dan Tegangan Batang")
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)

        def plot_force():

            fig, ax = plt.subplots()

            xmin, xmax = nodes[:, 0].min(), nodes[:, 0].max()
            ymin, ymax = nodes[:, 1].min(), nodes[:, 1].max()

            offset = 0.03 * max(xmax - xmin, ymax - ymin)

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

                ax.text(xm + offset * nx, ym + offset * ny,
                        f"{force[i] / 1000:.1f} kN",
                        ha="center")

            ax.set_title("Diagram Gaya Batang (Tarik Biru, Tekan Merah)")
            ax.axis("equal")

            return fig

        st.subheader("Diagram Tarik dan Tekan")
        st.pyplot(plot_force())

        def plot_deformation():

            fig,ax=plt.subplots()

            xmin,xmax = nodes[:,0].min(),nodes[:,0].max()
            ymin,ymax = nodes[:,1].min(),nodes[:,1].max()

            offset = 0.03*max(xmax-xmin,ymax-ymin)

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

                ax.plot([x1,x2],[y1,y2],"r",linewidth=3)

                # label elemen
                xm=(x1+x2)/2
                ym=(y1+y2)/2

                ax.text(xm,ym+offset,f"E{i+1}",color="blue",ha="center")

            # label node
            for i,(x,y) in enumerate(new_nodes):

                ax.plot(x,y,"ro")
                ax.text(x+offset,y+offset,f"N{i+1}",color="red")

            ax.set_title("Struktur Asli (Hitam) dan Deformasi (Merah)")
            ax.axis("equal")

            return fig

        st.subheader("Diagram Deformasi")
        st.pyplot(plot_deformation())