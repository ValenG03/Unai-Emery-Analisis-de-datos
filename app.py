import streamlit as st, pandas as pd, numpy as np
import plotly.express as px, plotly.graph_objects as go
import seaborn as sns, matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="El Fenómeno Emery", page_icon="⚡", layout="wide")
RED, BLK, GRY, WHT = "#CB3524", "#0A0A0A", "#1A1A1A", "#F2F2F2"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;700&display=swap');
.stApp{{background:radial-gradient(circle at 85% 0%,#2a0806 0%,{BLK} 45%);color:{WHT};font-family:Inter,sans-serif}}
[data-testid=stSidebar]{{background:#0f0f0f;border-right:2px solid {RED}}}
h1,h2,h3{{font-family:'Bebas Neue',sans-serif!important;letter-spacing:2px}}
.hero{{font-family:'Bebas Neue';font-size:clamp(3rem,8vw,6rem);line-height:.9;
 background:linear-gradient(90deg,{WHT} 30%,{RED});-webkit-background-clip:text;color:transparent}}
.tag{{color:{RED};font-weight:700;letter-spacing:4px;font-size:.8rem}}
[data-testid=stMetric]{{background:{GRY};border-left:4px solid {RED};padding:14px;border-radius:4px;box-shadow:0 0 18px {RED}22}}
.stTabs [aria-selected=true]{{color:{RED}!important}}
.card{{background:{GRY};border:1px solid {RED}55;padding:18px;border-radius:4px}}
</style>""", unsafe_allow_html=True)

# ---------- DATOS (Premier League; salarios en £m de cuentas anuales) ----------
S = pd.DataFrame({
    "Temporada": ["19-20", "20-21", "21-22", "22-23", "23-24", "24-25", "25-26"],
    "Entrenador": ["Smith", "Smith", "Smith → Gerrard", "Gerrard → Emery", "Emery", "Emery", "Emery"],
    "Pos": [17, 11, 14, 7, 4, 6, 4], "Pts": [35, 55, 45, 61, 68, 66, 65],
    "G": [9, 16, 13, 18, 20, 19, 19], "E": [8, 7, 6, 7, 8, 9, 8], "P": [21, 15, 19, 13, 10, 10, 11],
    "GF": [41, 55, 52, 51, 76, 58, 56], "GC": [67, 46, 54, 46, 61, 51, 49],
    "Salarios": [110, 129, 143, 194, 252, 273, 280],  # 19-20, 20-21 y 25-26 estimados; 23-24 = 13 meses
    "Europa": ["—", "—", "—", "Clasifica a Conference League", "4º → Champions · semis de Conference",
               "Cuartos de Champions · clasifica a Europa League", "🏆 Campeón de Europa League · vuelve a Champions"]})
S["PPP"], S["DG"] = (S.Pts / 38).round(2), S.GF - S.GC
S["Era"] = ["Pre-Emery"] * 3 + ["Transición"] + ["Emery"] * 3

# Splits por entrenador en Premier (Danks, interino, 2 PJ en 22-23: 1G 1P, 4-4)
C = pd.DataFrame({"Entrenador": ["Dean Smith", "Steven Gerrard", "Unai Emery"],
                  "PJ": [87, 38, 139], "G": [28, 12, 73], "E": [16, 8, 29], "P": [43, 18, 37],
                  "GF": [110, 45, 230], "GC": [133, 50, 187]})
C["Pts"] = C.G * 3 + C.E
C["Puntos por partido"], C["% Victorias"] = C.Pts / C.PJ, C.G / C.PJ * 100
C["Goles a favor / PJ"], C["Goles en contra / PJ"] = C.GF / C.PJ, C.GC / C.PJ

pre = C.iloc[:2][["PJ", "G", "Pts", "GF", "GC"]].sum() + pd.Series({"PJ": 2, "G": 1, "Pts": 3, "GF": 4, "GC": 4})
emy = C.iloc[2]
COL = {"Pre-Emery": "#5a5a5a", "Transición": "#8a2a20", "Emery": RED}

def style(fig, h=430):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter", color=WHT), height=h, margin=dict(l=10, r=10, t=40, b=10),
                      legend=dict(orientation="h", y=1.12, x=0), hoverlabel=dict(bgcolor=RED))
    fig.update_xaxes(gridcolor="#222"); fig.update_yaxes(gridcolor="#222")
    return fig

def emery_zone(fig):
    fig.add_vrect(x0=2.5, x1=6.5, fillcolor=RED, opacity=.08, line_width=0)
    fig.add_vline(x=3, line_dash="dot", line_color=RED,
                  annotation_text="⚡ Llega Emery (nov-22)", annotation_font_color=RED)
    return fig

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## ⚙️ Panel de control")
    metric = st.selectbox("Métrica de la serie temporal",
                          {"Pts": "Puntos", "PPP": "Puntos por partido", "G": "Victorias", "DG": "Diferencia de gol"},
                          format_func=lambda k: {"Pts": "Puntos", "PPP": "Puntos por partido", "G": "Victorias", "DG": "Diferencia de gol"}[k])
    k = st.slider("Clusters (K-means)", 2, 4, 3)
    st.caption("Fuentes: Premier League (premierleague.com/stats) y cuentas anuales del club. "
               "Salarios 19-20, 20-21 y 25-26 estimados; 23-24 cubre 13 meses.")

# ---------- HERO ----------
st.markdown('<p class="tag">ASTON VILLA · 2019–2026 · PREMIER LEAGUE</p>'
            '<p class="hero">EL FENÓMENO<br>EMERY</p>', unsafe_allow_html=True)
st.markdown("#### ¿Qué tan grande fue la transformación deportiva del Villa tras noviembre de 2022?")

c1, c2, c3, c4 = st.columns(4)
ppp_pre, ppp_em = pre.Pts / pre.PJ, emy.Pts / emy.PJ
c1.metric("Puntos por partido", f"{ppp_em:.2f}", f"{(ppp_em / ppp_pre - 1) * 100:+.0f}% vs antes ({ppp_pre:.2f})")
c2.metric("% de victorias", f"{emy.G / emy.PJ * 100:.0f}%", f"{(emy.G / emy.PJ - pre.G / pre.PJ) * 100:+.0f} pp")
c3.metric("Puesto medio", f"{S.Pos[4:].mean():.1f}º", f"{S.Pos[:3].mean() - S.Pos[4:].mean():+.1f} puestos")
c4.metric("Europa", "4 de 4", "🏆 Europa League 2026")

# ---------- MÁQUINA DEL TIEMPO ----------
t = st.select_slider("🕹️ Máquina del tiempo: elegí una temporada", S.Temporada, value="25-26")
r = S.set_index("Temporada").loc[t]
st.markdown(f"""<div class="card"><b style="color:{RED};font-size:1.4rem">{t} · {r.Pos}º · {r.Pts} pts</b>
&nbsp;&nbsp;|&nbsp;&nbsp;{r.G}G {r.E}E {r.P}P · {r.GF}-{r.GC} (DG {r.DG:+d}) · DT: {r.Entrenador}<br>
<span style="opacity:.8">Europa: {r.Europa} · Salarios: £{r.Salarios}m</span></div>""", unsafe_allow_html=True)
st.write("")

# ---------- TABS ----------
t1, t2, t3, t4, t5, t6 = st.tabs(["📈 Puntos", "🧠 Entrenadores", "🏁 Posiciones",
                                  "⚔️ Ataque vs Defensa", "💷 Salarios", "🤖 Clusters"])
with t1:
    f = px.bar(S, x="Temporada", y=metric, color="Era", color_discrete_map=COL, text=metric)
    f.add_scatter(x=S.Temporada, y=S[metric], mode="lines", line=dict(color=WHT, width=2), showlegend=False)
    st.plotly_chart(emery_zone(style(f)), width="stretch")

with t2:
    m = st.radio("Comparar por", ["Puntos por partido", "% Victorias", "Goles a favor / PJ", "Goles en contra / PJ"],
                 horizontal=True)
    f = px.bar(C, x="Entrenador", y=m, text=C[m].round(2), color="Entrenador",
               color_discrete_sequence=["#5a5a5a", "#8a8a8a", RED])
    st.plotly_chart(style(f, 380), width="stretch")
    st.dataframe(C[["Entrenador", "PJ", "G", "E", "P", "GF", "GC", "Pts"]], hide_index=True, width="stretch")

with t3:
    f = go.Figure(go.Scatter(x=S.Temporada, y=S.Pos, mode="lines+markers+text", text=S.Pos.astype(str) + "º",
                             textposition="top center", line=dict(color=RED, width=4, shape="spline"),
                             marker=dict(size=16, color=BLK, line=dict(color=RED, width=3))))
    f.add_hrect(y0=0.5, y1=4.5, fillcolor=RED, opacity=.12, line_width=0, annotation_text="Zona Champions")
    f.add_hrect(y0=17.5, y1=20.5, fillcolor="#555", opacity=.2, line_width=0, annotation_text="Descenso")
    f.update_yaxes(autorange="reversed", range=[20.5, 0.5], dtick=2)
    st.plotly_chart(emery_zone(style(f)), width="stretch")

with t4:
    f = go.Figure(go.Scatter(x=S.GF, y=S.GC, mode="lines+markers+text", text=S.Temporada, textposition="top right",
                             line=dict(color="#444", dash="dot"),
                             marker=dict(size=S.Pts / 2.2, color=[COL[e] for e in S.Era], line=dict(color=WHT, width=1)),
                             customdata=S[["Pts", "Pos"]], hovertemplate="GF %{x} · GC %{y}<br>%{customdata[0]} pts · %{customdata[1]}º"))
    f.add_vline(x=S.GF.mean(), line_color="#333"); f.add_hline(y=S.GC.mean(), line_color="#333")
    f.update_yaxes(autorange="reversed", title="Goles en contra (↑ mejor defensa)")
    f.update_xaxes(title="Goles a favor (→ mejor ataque)")
    st.plotly_chart(style(f, 480), width="stretch")
    st.caption("Arriba a la derecha = élite. Tamaño de la burbuja = puntos.")

with t5:
    S["Pts por £10m"] = (S.Pts / S.Salarios * 10).round(2)
    f = px.scatter(S, x="Salarios", y="Pts", text="Temporada", size="Pts", color="Era", color_discrete_map=COL,
                   trendline=None, labels={"Salarios": "Gasto salarial (£m)"})
    f.update_traces(textposition="top center")
    st.plotly_chart(style(f), width="stretch")
    st.caption("El salario casi se duplicó desde 21-22: los puntos subieron, pero la eficiencia por libra cayó. "
               "Emery convirtió inversión en élite, no en milagro low-cost.")

with t6:
    feats = pd.DataFrame({"PPP": S.PPP, "GF/PJ": S.GF / 38, "GC/PJ": S.GC / 38, "Pos": S.Pos, "Win%": S.G / 38})
    S["cl"] = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(StandardScaler().fit_transform(feats))
    names = {2: ["Zona gris", "Élite"], 3: ["Supervivencia", "Transición", "Élite"],
             4: ["Supervivencia", "Media tabla", "Europa", "Élite"]}[k]
    order = S.groupby("cl").PPP.mean().rank().astype(int) - 1
    S["Cluster"] = S.cl.map(lambda c: names[order[c]])
    f = px.scatter(S, x="GF", y="PPP", color="Cluster", text="Temporada", size="Pts",
                   color_discrete_sequence=["#555", "#8a2a20", RED, WHT])
    f.update_traces(textposition="top center")
    st.plotly_chart(style(f), width="stretch")
    cA, cB = st.columns([1, 1])
    cA.dataframe(S[["Temporada", "Entrenador", "Cluster"]], hide_index=True, width="stretch")
    sns.set_theme(style="dark", rc={"figure.facecolor": BLK, "axes.facecolor": BLK, "text.color": WHT,
                                    "xtick.color": WHT, "ytick.color": WHT})
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(S[["Pts", "GF", "GC", "DG", "Pos", "Salarios"]].corr(), annot=True, fmt=".2f", ax=ax, cbar=False,
                cmap=sns.blend_palette(["#3a3a3a", BLK, RED], as_cmap=True), vmin=-1, vmax=1, linewidths=1, linecolor=BLK)
    ax.set_title("Correlaciones (Seaborn)", color=WHT)
    cB.pyplot(fig)

# ---------- VEREDICTO ----------
st.markdown("---\n## 🎯 El diferencial: ¿ataque, defensa o consistencia?")
guess = st.radio("Antes de ver los datos, apostá:", ["Ataque", "Defensa", "Consistencia"], horizontal=True, index=None)
if guess:
    atk = (emy.GF / emy.PJ) / (pre.GF / pre.PJ) - 1
    dfn = 1 - (emy.GC / emy.PJ) / (pre.GC / pre.PJ)
    con = 1 - S.Pos[4:].std() / S.Pos[:3].std()
    D = pd.DataFrame({"Dimensión": ["Ataque", "Defensa", "Consistencia"], "Mejora %": np.round([atk * 100, dfn * 100, con * 100], 1)})
    f = px.bar(D, x="Mejora %", y="Dimensión", orientation="h", text="Mejora %",
               color="Dimensión", color_discrete_sequence=[RED, "#666", WHT])
    st.plotly_chart(style(f, 300), width="stretch")
    win = D.loc[D["Mejora %"].idxmax(), "Dimensión"]
    (st.success if guess == win else st.error)(f"{'¡Acertaste!' if guess == win else 'No.'} Mayor salto: **{win}**.")
    st.markdown(f"""<div class="card">
    <b>Ataque</b>: de {pre.GF / pre.PJ:.2f} a {emy.GF / emy.PJ:.2f} goles por partido.
    <b>Defensa</b>: de {pre.GC / pre.PJ:.2f} a {emy.GC / emy.PJ:.2f} recibidos — mejora real pero modesta.
    <b>Consistencia</b>: la dispersión del puesto final cayó {con * 100:.0f}% (de oscilar entre 11º y 17º a vivir entre 4º y 6º).<br><br>
    <b style="color:{RED}">Veredicto:</b> Emery no construyó un muro; construyó un equipo que gana más seguido
    (+{(ppp_em / ppp_pre - 1) * 100:.0f}% de puntos por partido) apoyado en un ataque mucho más productivo y en una
    regularidad competitiva de club de Champions. El título de Europa League 2026 es la consecuencia, no la excepción.
    </div>""", unsafe_allow_html=True)
    st.caption("Ataque y defensa: por partido de Premier, Emery (139 PJ) vs Smith + Gerrard + Danks (127 PJ). "
               "Consistencia: desvío estándar del puesto, 19-22 vs 23-26 (22-23 excluida por mixta).")
