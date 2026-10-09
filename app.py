import base64, io
from pathlib import Path
import streamlit as st, pandas as pd, numpy as np
import plotly.express as px, plotly.graph_objects as go
import seaborn as sns, matplotlib.pyplot as plt
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="El Fenómeno Emery", page_icon="🦁", layout="wide")

# Paleta Aston Villa: PMS 283 C (azul), PMS 222 C (bordó), PMS 107 C (amarillo)
BLUE, CLARET, YELLOW = "#95BFE5", "#670E36", "#FEE505"
CLARET_L, BG, CARD, WHT = "#A3195B", "#0B0507", "#160A10", "#F4F1F2"
BASE = Path(__file__).parent

# ---------- IMÁGENES (desde la raíz del repo) ----------
def find(name):
    hits = sorted(BASE.glob(name))
    return hits[0] if hits else None

def load(name, h=900):
    f = find(name)
    if not f:
        return None
    im = Image.open(f).convert("RGB")
    return im.resize((round(im.width * h / im.height), h))  # misma altura → filas parejas, sin recortes

def show(name, caption=None):
    im = load(name)
    if im:
        st.image(im, caption=caption, width="stretch")

def row(names, h=460, gap=20):
    """Fotos lado a lado, centradas, con la misma altura exacta y sin recortes."""
    ims = [im for im in map(load, names) if im]
    if not ims:
        return
    r = [im.width / im.height for im in ims]
    tags = []
    for im, ri in zip(ims, r):
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
        w = f"calc((100% - {gap * (len(ims) - 1)}px) * {ri / sum(r):.4f})"
        tags.append(f'<img style="width:{w}" src="data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}">')
    st.markdown(f'<div class="gal" style="gap:{gap}px;max-width:{h * sum(r) + gap * (len(ims) - 1):.0f}px">'
                f'{"".join(tags)}</div>', unsafe_allow_html=True)

def uri(name):
    f = find(name)
    if not f:
        return ""
    mime = "png" if f.suffix.lower() == ".png" else "jpeg"
    return f"data:image/{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"

LOGO = uri("Aston-Villa-FC-Logo-PNG.png")

# ---------- ESTILOS ----------
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Bebas+Neue&family=Inter:wght@400;600;800;900&display=swap');
.stApp{{background:
  radial-gradient(ellipse at 0% 0%,{CLARET}66 0%,transparent 45%),
  radial-gradient(ellipse at 100% 100%,{BLUE}22 0%,transparent 40%),{BG};color:{WHT};font-family:Inter,sans-serif}}
.block-container{{max-width:1250px;padding-top:2.5rem}}
[data-testid=stSidebar]{{background:linear-gradient(180deg,{CLARET} 0%,#1a0610 60%);border-right:3px solid {BLUE}}}
h2,h3{{font-family:'Bebas Neue',sans-serif!important;letter-spacing:2px;color:{BLUE}!important}}
.corner{{position:fixed;top:4.3rem;right:1.6rem;width:64px;z-index:999;
  filter:drop-shadow(0 0 8px {BLUE}88)}}
@keyframes rise{{from{{opacity:0;transform:translateY(40px);filter:blur(8px)}}to{{opacity:1;transform:none;filter:blur(0)}}}}
@keyframes shine{{0%{{background-position:0% 50%}}100%{{background-position:200% 50%}}}}
@keyframes grow{{from{{width:0}}to{{width:min(420px,70vw)}}}}
@keyframes pulse{{0%,100%{{text-shadow:0 0 0 transparent}}50%{{text-shadow:0 0 18px {YELLOW}aa}}}}
@keyframes track{{from{{letter-spacing:22px;opacity:0}}to{{letter-spacing:9px;opacity:1}}}}
.heroWrap{{text-align:center;padding:2.5rem 0 1.5rem;position:relative}}
.heroWrap:before{{content:"";position:absolute;inset:0;margin:auto;width:min(760px,90vw);height:70%;
  background:radial-gradient(ellipse,{CLARET}88 0%,transparent 65%);filter:blur(30px);z-index:-1}}
.hero{{font-family:'Anton',Impact,sans-serif!important;font-size:clamp(3rem,8.5vw,8.5rem)!important;line-height:.9;word-break:keep-all;overflow-wrap:normal;margin:0;text-transform:uppercase;
  letter-spacing:2px;background:linear-gradient(90deg,{BLUE},#ffffff,{CLARET_L},{BLUE},#ffffff,{CLARET_L});
  background-size:200% auto;-webkit-background-clip:text;color:transparent;
  animation:rise 1.1s cubic-bezier(.2,.8,.2,1) both,shine 6s linear infinite;
  filter:drop-shadow(0 6px 28px {CLARET}cc)}}
.hero span{{display:block;-webkit-text-stroke:2px {BLUE};color:transparent;background:none;
  -webkit-background-clip:initial;animation:rise 1.1s .25s cubic-bezier(.2,.8,.2,1) both}}
.bar{{height:5px;margin:26px auto;border-radius:3px;animation:grow 1.2s .6s ease-out both;
  background:linear-gradient(90deg,{CLARET} 0 40%,{BLUE} 40% 85%,{YELLOW} 85%)}}
.sub{{font-family:Inter,sans-serif;font-weight:900;font-size:clamp(1.5rem,3.4vw,2.6rem)!important;line-height:1.15;color:{WHT};
  margin:0 auto;max-width:900px;animation:rise 1s .8s both}}
.sub b{{color:{YELLOW};animation:pulse 2.8s 2s ease-in-out infinite}}
.tag{{color:{BLUE};font-weight:800;letter-spacing:9px;font-size:.9rem;margin-top:18px;animation:track 1.4s 1.1s both}}
[data-testid=stImage] img,.gal img{{border-radius:14px}}
.gal{{display:flex;margin:8px auto}}
.gal img{{height:auto;border:1px solid {BLUE}55;
  box-shadow:0 10px 40px #000a,0 0 0 4px {CLARET}55;animation:rise 1s both}}
.kicker{{font-family:'Bebas Neue';color:{YELLOW};letter-spacing:4px;font-size:1rem;margin:5.5rem 0 -12px}}
[data-testid=stMetric]{{background:linear-gradient(145deg,{CARD},#22101a);border:1px solid {CLARET_L}55;
  border-top:4px solid {BLUE};padding:16px 18px;border-radius:12px;box-shadow:0 8px 30px #00000088}}
[data-testid=stMetricValue]{{font-family:'Anton';color:{WHT};font-size:2.3rem}}
[data-testid=stMetricLabel]{{color:{BLUE}!important;text-transform:uppercase;letter-spacing:2px}}
.stTabs [data-baseweb=tab-list]{{gap:6px;flex-wrap:wrap}}
.stTabs [data-baseweb=tab]{{background:{CARD};border:1px solid {CLARET_L}55;border-radius:999px;padding:6px 16px}}
.stTabs [aria-selected=true]{{background:{CLARET}!important;border-color:{BLUE}!important;color:{WHT}!important}}
.card{{background:linear-gradient(145deg,{CARD},#1f0c16);border:1px solid {BLUE}44;border-left:5px solid {CLARET_L};
  padding:20px 22px;border-radius:12px;line-height:1.6}}
.card b.h{{color:{YELLOW};font-family:'Anton';font-size:1.5rem;letter-spacing:1px}}
[data-testid=stImage] img{{border-radius:14px;border:1px solid {BLUE}55;box-shadow:0 10px 40px #000a,0 0 0 4px {CLARET}55}}
[data-testid=stCaptionContainer]{{color:#b9aab1}}
.src{{text-align:center;max-width:760px;margin:0 auto;border-left:1px solid {BLUE}44;border-top:4px solid {CLARET_L}}}
.src a{{color:{BLUE}!important;text-decoration:none!important;border:none}}
.src a:hover{{color:{YELLOW}!important}}
@keyframes neon{{0%,100%{{filter:drop-shadow(0 0 4px {BLUE}) drop-shadow(0 0 12px {CLARET_L})}}
  50%{{filter:drop-shadow(0 0 8px {BLUE}) drop-shadow(0 0 22px {YELLOW}77)}}}}
.foot{{text-align:center;margin:6rem 0 2rem}}
.foot img{{width:72px;animation:neon 3s ease-in-out infinite}}
.foot p{{font-size:.75rem;color:#9c8c94;margin-top:3rem;letter-spacing:1px}}
</style>""", unsafe_allow_html=True)
if LOGO:
    st.markdown(f'<img class="corner" src="{LOGO}">', unsafe_allow_html=True)

# ---------- DATOS (Premier League; salarios en £m según cuentas anuales) ----------
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
COL = {"Pre-Emery": "#55505a", "Transición": CLARET_L, "Emery": BLUE}

def style(fig, h=440):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(22,10,16,.55)",
                      font=dict(family="Inter", color=WHT, size=13), height=h, margin=dict(l=10, r=10, t=50, b=10),
                      legend=dict(orientation="h", y=1.12, x=0, title=None), hoverlabel=dict(bgcolor=CLARET, font_color=WHT))
    fig.update_xaxes(gridcolor="#2a1820", zeroline=False); fig.update_yaxes(gridcolor="#2a1820", zeroline=False)
    return fig

def emery_zone(fig):
    fig.add_vrect(x0=2.5, x1=6.5, fillcolor=BLUE, opacity=.07, line_width=0)
    fig.add_vline(x=3, line_dash="dot", line_color=YELLOW,
                  annotation_text="🦁 Llega Emery (nov-22)", annotation_font_color=YELLOW)
    return fig

def kicker(num, text):
    st.markdown(f'<p class="kicker">{num}</p>', unsafe_allow_html=True); st.markdown(f"## {text}")

# ---------- SIDEBAR ----------
with st.sidebar:
    if LOGO:
        st.markdown(f'<div style="text-align:center"><img src="{LOGO}" width="90"></div>', unsafe_allow_html=True)
    st.markdown("## ⚙️ Panel de control")
    LBL = {"Pts": "Puntos", "PPP": "Puntos por partido", "G": "Victorias", "DG": "Diferencia de gol"}
    metric = st.selectbox("Métrica de la serie temporal", list(LBL), format_func=LBL.get)
    k = st.slider("Clusters (K-means)", 2, 4, 3)
    st.caption("Salarios 19-20, 20-21 y 25-26 estimados; 23-24 cubre 13 meses.")

# ---------- HERO ----------
st.markdown(f"""<div class="heroWrap"><div class="hero">El fenómeno<span>Emery</span></div><div class="bar"></div>
<div class="sub">El villano que llevó a los <b>villanos</b> a la cima</div>
<div class="tag">ASTON VILLA · 2019–2026 · PREMIER LEAGUE</div></div>""", unsafe_allow_html=True)
row(["poster-emery.jfif"], h=600)

st.markdown('<div style="height:3.5rem"></div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
ppp_pre, ppp_em = pre.Pts / pre.PJ, emy.Pts / emy.PJ
c1.metric("Puntos por partido", f"{ppp_em:.2f}", f"{(ppp_em / ppp_pre - 1) * 100:+.0f}% vs antes ({ppp_pre:.2f})")
c2.metric("% de victorias", f"{emy.G / emy.PJ * 100:.0f}%", f"{(emy.G / emy.PJ - pre.G / pre.PJ) * 100:+.0f} pp")
c3.metric("Puesto medio", f"{S.Pos[4:].mean():.1f}º", f"{S.Pos[:3].mean() - S.Pos[4:].mean():+.1f} puestos")
c4.metric("Europa", "4 de 4", "🏆 Europa League 2026")

# ---------- 01 · EL VILLANO ----------
kicker("01", "El villano")
row(["villain.jfif", "5-europas-league.jpeg"])
st.write("")
_, mid, _ = st.columns([1, 4, 1])
mid.markdown(f"""<div class="card" style="text-align:center;border-left:1px solid {BLUE}44;border-top:4px solid {CLARET_L}">
<b class="h">Noviembre 2022</b><br>
El Villa estaba a tres puntos del descenso. Emery llegó desde Villarreal con un método obsesivo:
video, presión alta y una línea defensiva adelantada que vive del offside.<br><br>
<b class="h">Mayo 2026</b><br>Cuatro temporadas seguidas en Europa, Champions League tras 41 años
y el primer título en tres décadas.</div>""", unsafe_allow_html=True)

# ---------- 02 · MÁQUINA DEL TIEMPO ----------
kicker("02", "Máquina del tiempo")
t = st.select_slider("Elegí una temporada", S.Temporada, value="25-26")
r = S.set_index("Temporada").loc[t]
st.markdown(f"""<div class="card"><b class="h">{t} · {r.Pos}º · {r.Pts} pts</b><br>
{r.G}G {r.E}E {r.P}P · {r.GF}-{r.GC} (DG {r.DG:+d}) · DT: {r.Entrenador}<br>
<span style="color:{BLUE}">Europa:</span> {r.Europa} · <span style="color:{BLUE}">Salarios:</span> £{r.Salarios}m</div>""",
            unsafe_allow_html=True)

# ---------- 03 · LOS DATOS ----------
kicker("03", "Los datos")
t1, t2, t3, t4, t5, t6 = st.tabs(["📈 Puntos", "🧠 Entrenadores", "🏁 Posiciones",
                                  "⚔️ Ataque vs Defensa", "💷 Salarios", "🤖 Clusters"])
with t1:
    f = px.bar(S, x="Temporada", y=metric, color="Era", color_discrete_map=COL, text=metric,
               labels={metric: LBL[metric]})
    f.add_scatter(x=S.Temporada, y=S[metric], mode="lines+markers", line=dict(color=YELLOW, width=3),
                  marker=dict(size=8), showlegend=False)
    f.update_traces(marker_line_width=0, selector=dict(type="bar"))
    st.plotly_chart(emery_zone(style(f)), width="stretch")

with t2:
    g, im = st.columns([2.3, 1])
    with g:
        m = st.radio("Comparar por", ["Puntos por partido", "% Victorias", "Goles a favor / PJ", "Goles en contra / PJ"],
                     horizontal=True)
        f = px.bar(C, x="Entrenador", y=m, text=C[m].round(2), color="Entrenador",
                   color_discrete_sequence=["#55505a", CLARET_L, BLUE])
        f.update_layout(showlegend=False)
        st.plotly_chart(style(f, 380), width="stretch")
    with im:
        show("Emery.jfif", "Unai Emery, 139 partidos de Premier con el Villa")
    st.dataframe(C[["Entrenador", "PJ", "G", "E", "P", "GF", "GC", "Pts"]], hide_index=True, width="stretch")

with t3:
    f = go.Figure(go.Scatter(x=S.Temporada, y=S.Pos, mode="lines+markers+text", text=S.Pos.astype(str) + "º",
                             textposition="top center", textfont=dict(color=WHT, size=14),
                             line=dict(color=BLUE, width=4, shape="spline"),
                             marker=dict(size=18, color=[COL[e] for e in S.Era], line=dict(color=YELLOW, width=2))))
    f.add_hrect(y0=0.5, y1=4.5, fillcolor=BLUE, opacity=.12, line_width=0, annotation_text="Zona Champions")
    f.add_hrect(y0=17.5, y1=20.5, fillcolor=CLARET, opacity=.35, line_width=0, annotation_text="Descenso")
    f.update_yaxes(autorange="reversed", range=[20.5, 0.5], dtick=2, title="Puesto")
    st.plotly_chart(emery_zone(style(f)), width="stretch")

with t4:
    f = go.Figure(go.Scatter(x=S.GF, y=S.GC, mode="lines+markers+text", text=S.Temporada, textposition="top right",
                             line=dict(color="#5a4650", dash="dot"),
                             marker=dict(size=S.Pts / 2, color=[COL[e] for e in S.Era], line=dict(color=YELLOW, width=1.5)),
                             customdata=S[["Pts", "Pos"]],
                             hovertemplate="GF %{x} · GC %{y}<br>%{customdata[0]} pts · %{customdata[1]}º<extra></extra>"))
    f.add_vline(x=S.GF.mean(), line_color="#4a3440"); f.add_hline(y=S.GC.mean(), line_color="#4a3440")
    f.update_yaxes(autorange="reversed", title="Goles en contra (↑ mejor defensa)")
    f.update_xaxes(title="Goles a favor (→ mejor ataque)")
    st.plotly_chart(style(f, 480), width="stretch")
    st.caption("Arriba a la derecha = élite. Tamaño de la burbuja = puntos.")

with t5:
    f = px.scatter(S, x="Salarios", y="Pts", text="Temporada", size="Pts", color="Era", color_discrete_map=COL,
                   labels={"Salarios": "Gasto salarial (£m)", "Pts": "Puntos"})
    f.update_traces(textposition="top center", marker_line=dict(color=YELLOW, width=1))
    st.plotly_chart(style(f), width="stretch")
    st.caption("El salario casi se duplicó desde 21-22: los puntos subieron, pero la eficiencia por libra cayó. "
               "Emery convirtió inversión en élite, no en un milagro low-cost.")

with t6:
    feats = pd.DataFrame({"PPP": S.PPP, "GF/PJ": S.GF / 38, "GC/PJ": S.GC / 38, "Pos": S.Pos, "Win%": S.G / 38})
    S["cl"] = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(StandardScaler().fit_transform(feats))
    names = {2: ["Zona gris", "Élite"], 3: ["Supervivencia", "Transición", "Élite"],
             4: ["Supervivencia", "Media tabla", "Europa", "Élite"]}[k]
    order = S.groupby("cl").PPP.mean().rank(method="first").astype(int) - 1
    S["Cluster"] = S.cl.map(lambda c: names[order[c]])
    pal = dict(zip(names, {2: ["#55505a", BLUE], 3: ["#55505a", CLARET_L, BLUE],
                           4: ["#55505a", CLARET_L, BLUE, YELLOW]}[k]))
    f = px.scatter(S, x="GF", y="PPP", color="Cluster", text="Temporada", size="Pts", color_discrete_map=pal,
                   labels={"GF": "Goles a favor", "PPP": "Puntos por partido"})
    f.update_traces(textposition="top center")
    st.plotly_chart(style(f), width="stretch")
    cA, cB = st.columns(2)
    cA.dataframe(S[["Temporada", "Entrenador", "Cluster"]], hide_index=True, width="stretch")
    sns.set_theme(style="dark", rc={"figure.facecolor": BG, "axes.facecolor": BG, "text.color": WHT,
                                    "xtick.color": WHT, "ytick.color": WHT})
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(S[["Pts", "GF", "GC", "DG", "Pos", "Salarios"]].corr(), annot=True, fmt=".2f", ax=ax, cbar=False,
                cmap=sns.blend_palette([CLARET, BG, BLUE], as_cmap=True), vmin=-1, vmax=1, linewidths=1, linecolor=BG)
    ax.set_title("Correlaciones (Seaborn)", color=BLUE)
    cB.pyplot(fig)

# ---------- 04 · VEREDICTO ----------
kicker("04", "¿Ataque, defensa o consistencia?")
atk = (emy.GF / emy.PJ) / (pre.GF / pre.PJ) - 1
dfn = 1 - (emy.GC / emy.PJ) / (pre.GC / pre.PJ)
con = 1 - S.Pos[4:].std() / S.Pos[:3].std()
D = pd.DataFrame({"Dimensión": ["Ataque", "Defensa", "Consistencia"],
                  "Mejora %": np.round([atk * 100, dfn * 100, con * 100], 1)})
f = px.bar(D, x="Mejora %", y="Dimensión", orientation="h", text="Mejora %", color="Dimensión",
           color_discrete_sequence=[CLARET_L, "#7a6f75", BLUE])
f.update_traces(texttemplate="%{x:+.0f}%", textposition="outside")
f.update_layout(showlegend=False, xaxis_range=[0, D["Mejora %"].max() * 1.2])
st.plotly_chart(style(f, 300), width="stretch")
v1, v2 = st.columns([2.2, 1], vertical_alignment="center")
v1.markdown(f"""<div class="card">
<b style="color:{BLUE}">Ataque</b>: de {pre.GF / pre.PJ:.2f} a {emy.GF / emy.PJ:.2f} goles por partido.<br>
<b style="color:{BLUE}">Defensa</b>: de {pre.GC / pre.PJ:.2f} a {emy.GC / emy.PJ:.2f} recibidos, una mejora real pero modesta.<br>
<b style="color:{BLUE}">Consistencia</b>: la dispersión del puesto final cayó {con * 100:.0f}% (de oscilar entre 11º y 17º a vivir entre 4º y 6º).<br><br>
<b class="h">Veredicto</b><br>Emery no construyó un muro: construyó un equipo que gana más seguido
(+{(ppp_em / ppp_pre - 1) * 100:.0f}% de puntos por partido), con un ataque mucho más productivo y una
regularidad de club de Champions. La Europa League 2026 es la consecuencia, no la excepción.</div>""",
            unsafe_allow_html=True)
with v2:
    show("Emery-2.jfif")
st.caption("Ataque y defensa: por partido de Premier, Emery (139 PJ) vs Smith + Gerrard + Danks (127 PJ). "
           "Consistencia: desvío estándar del puesto, 19-22 vs 23-26 (22-23 excluida por mixta).")

# ---------- 05 · ESTAMBUL ----------
kicker("05", "Estambul, 20 de mayo de 2026")
st.markdown('<p style="text-align:center">Aston Villa 3–0 Freiburg. Primer título europeo desde 1982 '
            'y quinta Europa League para Emery.</p>', unsafe_allow_html=True)
row(["Unai-Emery-campeon*", "campeones-aston-villa.jpg"])

# ---------- 06 · FUENTES ----------
kicker("06", "Fuentes")
st.markdown(f"""<div class="card src">
<b style="color:{YELLOW}">Oficiales</b><br>
<a href="https://www.premierleague.com/en/stats" target="_blank">Premier League · Estadísticas</a><br>
<a href="https://www.premierleague.com/en/tables" target="_blank">Premier League · Tablas por temporada</a><br>
<a href="https://www.uefa.com/uefaeuropaleague/" target="_blank">UEFA Europa League</a><br>
<a href="https://www.avfc.co.uk" target="_blank">Aston Villa FC · Sitio oficial</a><br><br>
<b style="color:{YELLOW}">Finanzas y contexto</b><br>
<a href="https://swissramble.substack.com/p/aston-villa-finances-202324" target="_blank">The Swiss Ramble · Aston Villa Finances 2023/24</a><br>
<a href="https://www.avfchistory.co.uk/aston-villa-club-finances" target="_blank">AVFC History · Club finances</a><br>
<a href="https://myoldmansaid.com/the-hidden-financial-story-behind-aston-villas-greatest-modern-day-season/" target="_blank">My Old Man Said · Salarios 2021-22 a 2024-25</a><br>
<a href="https://en.wikipedia.org/wiki/2026_UEFA_Europa_League_final" target="_blank">Final de la Europa League 2026</a>
</div>""", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown(f"""<div class="foot">{f'<img src="{LOGO}">' if LOGO else ''}
<p>Análisis de datos hechos por Valentín Gerold en colaboración con IA</p></div>""", unsafe_allow_html=True)
