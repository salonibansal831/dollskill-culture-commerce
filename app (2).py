"""
Culture & Commerce Snapshot, built for Dolls Kill by Saloni Bansal.
Public data only: Google Trends exports + hand-collected public product prices.
"""
from datetime import date, timedelta
from io import StringIO
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

HERE = Path(__file__).parent
# data files live in ./data, but also work if they were uploaded next to app.py
DATA = HERE / "data" if (HERE / "data" / "festivals.csv").exists() else HERE

# ---------- palette (dark surface, validated categorical slots) ----------
SURFACE = "#0e0e0d"
INK = "#f5f5f2"
INK_2 = "#c3c2b7"
MUTED = "#8a8980"
GRID = "#2a2a28"
ACCENT = "#ff3d9a"            # Dolls Kill focus color (used for DK only)
CONTEXT = "#6b6a64"           # competitors = context gray
SERIES = ["#3987e5", "#d95926", "#199e70"]  # trends terms, fixed order, max 3
BAND = "rgba(255,61,154,0.18)"

st.set_page_config(page_title="Culture & Commerce Snapshot | Dolls Kill",
                   page_icon="🖤", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
<style>
.block-container {{max-width: 1180px; padding-top: 3.6rem;}}
h1, h2, h3 {{letter-spacing: -0.01em;}}
.kicker {{color:{ACCENT}; font-weight:700; letter-spacing:.14em; font-size:.78rem; text-transform:uppercase;}}
.sub {{color:{INK_2}; font-size:1.05rem; max-width: 780px;}}
.tile {{background:#1a1a19; border:1px solid {GRID}; border-radius:14px; padding:18px 20px; height:100%;}}
.tile .n {{font-size:2.1rem; font-weight:800; color:{INK}; line-height:1.1;}}
.tile .l {{color:{INK_2}; font-size:.9rem; margin-top:4px;}}
.rec {{background:#1a1a19; border-left:4px solid {ACCENT}; border-radius:10px; padding:16px 18px; margin-bottom:12px;}}
.rec b {{color:{INK};}}
.rec .why {{color:{INK_2}; font-size:.92rem; margin-top:6px;}}
.foot {{color:{MUTED}; font-size:.85rem;}}
</style>
""", unsafe_allow_html=True)


# ---------- loaders ----------
@st.cache_data
def load_festivals() -> pd.DataFrame:
    f = pd.read_csv(DATA / "festivals.csv", parse_dates=["start", "end"])
    return f


def parse_trends(text: str) -> pd.DataFrame:
    """Accepts a raw Google Trends 'Interest over time' CSV export
    (with its 'Category:' preamble) or a tidy CSV with a date column."""
    lines = text.splitlines()
    start = 0
    for i, ln in enumerate(lines):
        head = ln.split(",")[0].strip().lower()
        if head in ("week", "day", "month", "date", "time"):
            start = i
            break
    df = pd.read_csv(StringIO("\n".join(lines[start:])))
    date_col = df.columns[0]
    df = df.rename(columns={date_col: "date"})
    df["date"] = pd.to_datetime(df["date"])
    clean = {}
    for c in df.columns[1:]:
        name = c.split(":")[0].strip()
        clean[c] = name
        df[c] = pd.to_numeric(df[c].astype(str).str.replace("<1", "0.5"), errors="coerce")
    return df.rename(columns=clean).dropna(subset=["date"]).sort_values("date")


@st.cache_data
def load_trends_file() -> pd.DataFrame | None:
    p = DATA / "trends.csv"
    if not p.exists() or p.stat().st_size < 20:
        return None
    return parse_trends(p.read_text(encoding="utf-8-sig"))


@st.cache_data
def load_prices() -> pd.DataFrame:
    p = DATA / "prices.csv"
    df = pd.read_csv(p) if p.exists() else pd.DataFrame()
    if df.empty:
        return df
    for col in ("price", "sale_price"):
        if col in df:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r"[$,]", "", regex=True),
                                    errors="coerce")
    if "sale_price" not in df:
        df["sale_price"] = df["price"]
    df["sale_price"] = df["sale_price"].fillna(df["price"])
    df["brand"] = df["brand"].str.strip()
    df["category"] = df["category"].str.strip().str.title()
    return df.dropna(subset=["price"])


# ---------- analytics ----------
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
STATE_ABBR = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO",
"Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL","Georgia":"GA","Hawaii":"HI",
"Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA",
"Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
"Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ",
"New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
"Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD",
"Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
"West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"}


def seasonality(tr: pd.DataFrame, terms: list) -> pd.DataFrame:
    """Share of each full calendar year's searches that fall in each month, averaged over full years."""
    d = tr.copy()
    d["y"], d["m"] = d["date"].dt.year, d["date"].dt.month
    full = d.groupby("y")["m"].nunique()
    d = d[d["y"].isin(full[full == 12].index)]
    share = d.groupby(["y", "m"])[terms].sum().div(d.groupby("y")[terms].sum(), level=0) * 100
    return share.groupby("m").mean(), sorted(d["y"].unique())


def same_period_growth(tr: pd.DataFrame, terms: list):
    """Average interest over the same months in the first full year vs the latest year."""
    d = tr.copy()
    d["y"], d["m"] = d["date"].dt.year, d["date"].dt.month
    last_y = d["y"].max()
    last_m = d.loc[d["y"] == last_y, "m"].max()
    first_y = d.groupby("y")["m"].nunique().loc[lambda x: x == 12].index.min()
    per = d[d["m"] <= last_m]
    avg = per.groupby("y")[terms].mean()
    return avg, first_y, last_y, last_m


@st.cache_data
def load_states() -> pd.DataFrame | None:
    p = DATA / "trends_by_state.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df.columns = [c.split(":")[0].strip() for c in df.columns]
    df["code"] = df.iloc[:, 0].map(STATE_ABBR)
    return df.dropna(subset=["code"])


# ---------- header ----------
st.markdown('<div class="kicker">Culture & Commerce Snapshot · built for Dolls Kill</div>',
            unsafe_allow_html=True)
st.title("When the culture moves, when should Dolls Kill?")
st.markdown(
    '<div class="sub">A one-page look at what a Culture & Commerce Analyst would bring: '
    'reading festival and rave culture as a demand signal, benchmarking price position '
    'against the market, and turning both into moves. Built entirely on public data.</div>',
    unsafe_allow_html=True)
st.write("")

fests = load_festivals()
trends = load_trends_file()
prices = load_prices()

with st.sidebar:
    st.markdown("### About the data")
    st.caption("Sources: Google Trends (US, monthly, Sep 2021–Sep 2026), public product listings, "
               "published festival dates. No internal Dolls Kill data used.")

findings = {}

# ================= PANEL 1: culture → demand =================
st.header("1 · Culture is a demand calendar")
if trends is None or trends.empty:
    st.info("Add a Google Trends export at `data/trends.csv` to light this panel up (see README).")
else:
    terms = list(trends.columns[1:])[:3]
    seas, seas_years = seasonality(trends, terms)
    growth, g0, g1, gm = same_period_growth(trends, terms)
    mult = (growth.loc[g1] / growth.loc[g0])
    fest_t = next((t for t in terms if "festival" in t.lower()), terms[0])
    rave_t = next((t for t in terms if "rave" in t.lower()), terms[0])
    edc_t = next((t for t in terms if "edc" in t.lower()), None)
    spring = seas.loc[[3, 4, 5]].sum()
    findings["trend"] = dict(mult=mult, g0=g0, g1=g1, gm=gm, fest_t=fest_t, rave_t=rave_t,
                             edc_t=edc_t, spring=spring, seas=seas, years=seas_years)

    t1, t2, t3 = st.columns(3)
    t1.markdown(f'<div class="tile"><div class="n" style="color:{ACCENT}">{mult[fest_t]:.1f}x</div>'
                f'<div class="l">“{fest_t}” searches, {MONTHS[0]}–{MONTHS[gm-1]} {g1} vs the same '
                f'months in {g0}</div></div>', unsafe_allow_html=True)
    t2.markdown(f'<div class="tile"><div class="n">{(mult[rave_t]-1)*100:+.0f}%</div>'
                f'<div class="l">“{rave_t}” searches over the same comparison</div></div>',
                unsafe_allow_html=True)
    if edc_t:
        t3.markdown(f'<div class="tile"><div class="n">{spring[edc_t]:.0f}%</div>'
                    f'<div class="l">of a year\'s “{edc_t}” searches land in March–May, '
                    f'before EDC Las Vegas in mid-May</div></div>', unsafe_allow_html=True)
    st.write("")

    # --- timeline with festival bands ---
    fig = go.Figure()
    lo, hi = trends["date"].min(), trends["date"].max()
    for _, f in fests[(fests["end"] >= lo) & (fests["start"] <= hi)
                      & (fests["festival"] != "Halloween")].iterrows():
        fig.add_vrect(x0=f["start"] - timedelta(days=4), x1=f["end"] + timedelta(days=4),
                      fillcolor="rgba(255,255,255,0.07)", line_width=0, layer="below")
    for i, t in enumerate(terms):
        fig.add_trace(go.Scatter(x=trends["date"], y=trends[t], name=t, mode="lines+markers",
                                 line=dict(color=SERIES[i], width=2), marker=dict(size=5),
                                 hovertemplate="%{x|%b %Y}: %{y}<extra>" + t + "</extra>"))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10),
                      paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
                      font=dict(color=INK_2), hovermode="x unified",
                      legend=dict(orientation="h", y=1.12, x=0),
                      yaxis=dict(title="Search interest (0–100)", gridcolor=GRID, zeroline=False),
                      xaxis=dict(gridcolor=GRID))
    st.subheader("Five years of rave and festival search")
    st.caption("Monthly US Google search interest, all three terms on one scale (100 = the single "
               "highest month). Gray bands mark Ultra, Coachella, EDC, Lollapalooza and Burning Man.")
    st.plotly_chart(fig, use_container_width=True)

    # --- seasonal calendar ---
    fig2 = go.Figure()
    fig2.add_vrect(x0=1.5, x1=4.5, fillcolor=BAND, line_width=0, layer="below")
    for i, t in enumerate(terms):
        fig2.add_trace(go.Scatter(x=MONTHS, y=seas[t].values, name=t, mode="lines+markers",
                                  line=dict(color=SERIES[i], width=2), marker=dict(size=8),
                                  hovertemplate="%{x}: %{y:.1f}% of the year<extra>" + t + "</extra>"))
    fig2.add_hline(y=100/12, line=dict(color=MUTED, dash="dot", width=1))
    fig2.add_annotation(x="Dec", y=100/12, text="an average month", showarrow=False,
                        yshift=10, font=dict(color=MUTED, size=11), xanchor="right")
    fig2.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10),
                       paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, font=dict(color=INK_2),
                       hovermode="x unified", legend=dict(orientation="h", y=1.12, x=0),
                       xaxis=dict(gridcolor=GRID, tickmode="array", tickvals=MONTHS,
                                  ticktext=[m + ({"Mar": "<br>Ultra", "Apr": "<br>Coachella",
                                                  "May": "<br>EDC", "Aug": "<br>Lolla, BM",
                                                  "Oct": "<br>Halloween"}.get(m, "")) for m in MONTHS]),
                       yaxis=dict(title="% of the year's searches", ticksuffix="%",
                                  gridcolor=GRID, zeroline=False, rangemode="tozero"))
    st.subheader("When in the year people shop for it")
    st.caption(f"Share of each year's searches falling in each month, averaged over "
               f"{seas_years[0]}–{seas_years[-1]}. Pink = spring festival season.")
    st.plotly_chart(fig2, use_container_width=True)

    # --- state map ---
    states = load_states()
    if states is not None and rave_t in states.columns and fest_t in states.columns:
        states["rave_share"] = states[rave_t] / (states[rave_t] + states[fest_t]) * 100
        top = states.sort_values("rave_share", ascending=False)
        findings["states"] = top
        st.subheader("Rave or festival? It depends where you are")
        st.caption(f"“Rave” is the bigger word in every state, but the Mountain West and Southwest "
                   f"lean hardest into it ({top.iloc[0, 0]} {top['rave_share'].iloc[0]:.0f}%), while "
                   f"places like {top.iloc[-2, 0]} and {top.iloc[-3, 0]} are close to 50/50. Same "
                   f"customer, different vocabulary, which is useful for regional keywords and ad copy.")
        med = states["rave_share"].median()
        show = pd.concat([top.head(8), top.tail(5)])
        colors = [ACCENT] * 8 + ["#3987e5"] * 5
        figS = go.Figure(go.Bar(
            y=show.iloc[:, 0], x=show["rave_share"], orientation="h",
            marker=dict(color=colors, cornerradius=4),
            text=[f"{v:.0f}%" for v in show["rave_share"]], textposition="outside",
            textfont=dict(color=INK),
            hovertemplate="%{y}: %{x:.0f}% of searches say rave<extra></extra>"))
        figS.add_vline(x=med, line=dict(color=MUTED, dash="dot", width=1))
        figS.add_annotation(x=med, y=-0.02, yref="paper", yanchor="top", text=f"median state {med:.0f}%",
                            showarrow=False, font=dict(color=MUTED, size=11))
        figS.update_layout(height=430, margin=dict(l=10, r=40, t=30, b=10),
                           paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, font=dict(color=INK_2),
                           xaxis=dict(range=[0, 100], ticksuffix="%", gridcolor=GRID,
                                      title=dict(text="Share of searches that say “rave” (vs “festival”)",
                                                 standoff=28)),
                           yaxis=dict(autorange="reversed", gridcolor=GRID))
        st.plotly_chart(figS, use_container_width=True)
        if edc_t and edc_t in states.columns:
            e_top = states.sort_values(edc_t, ascending=False).iloc[0]
            st.caption(f"Pink = the 8 states that lean hardest into “rave”; blue = the 5 closest to 50/50. "
                       f"“{edc_t}” is most concentrated in {e_top.iloc[0]}, home of EDC Las Vegas.")

# ================= PANEL 2: price position =================
st.divider()
st.header("2 · Where Dolls Kill sits on price")
if prices.empty:
    st.info("Add hand-collected products to `data/prices.csv` to light this panel up (see README).")
else:
    is_dk = prices["brand"].str.lower().str.replace(" ", "") == "dollskill"
    dk_name = prices.loc[is_dk, "brand"].iloc[0] if is_dk.any() else "Dolls Kill"
    cats = sorted(prices["category"].unique())
    brands = [dk_name] + sorted(b for b in prices["brand"].unique() if b != dk_name)

    md = (prices["sale_price"] < prices["price"] - 0.01).groupby(prices["brand"]).mean() * 100
    findings["markdown"] = md
    comp_md = md.drop(dk_name, errors="ignore")
    top_comp = comp_md.idxmax() if len(comp_md) else None
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="tile"><div class="n">{len(prices)}</div>'
                f'<div class="l">real products across {prices["brand"].nunique()} brands and '
                f'{len(cats)} categories</div></div>', unsafe_allow_html=True)
    if top_comp:
        k2.markdown(f'<div class="tile"><div class="n">{comp_md[top_comp]:.0f}%</div>'
                    f'<div class="l">of {top_comp} listings are marked down right now</div></div>',
                    unsafe_allow_html=True)
    k3.markdown(f'<div class="tile"><div class="n" style="color:{ACCENT}">{md.get(dk_name, 0):.0f}%</div>'
                f'<div class="l">of Dolls Kill listings are.</div></div>',
                unsafe_allow_html=True)
    st.write("")
    basis = st.radio("Compare on", ["What shoppers pay today", "List price"], horizontal=True)
    pcol = "sale_price" if basis.startswith("What") else "price"
    findings["basis"] = basis

    # gap table: DK median vs competitor median per category
    rows = []
    for c in cats:
        d = prices[prices["category"] == c]
        dk = d[d["brand"] == dk_name][pcol]
        comp = d[d["brand"] != dk_name][pcol]
        if len(dk) and len(comp):
            gap = (dk.median() / comp.median() - 1) * 100
            rows.append({"Category": c, "Dolls Kill median": dk.median(),
                         "Market median": comp.median(), "Gap %": gap,
                         "n (DK / market)": f"{len(dk)} / {len(comp)}"})
    gap_df = pd.DataFrame(rows)
    findings["gaps"] = gap_df

    left, right = st.columns([1.35, 1])
    with left:
        fig3 = go.Figure()
        for b in brands:
            d = prices[prices["brand"] == b]
            focus = b == dk_name
            fig3.add_trace(go.Box(
                y=d["category"], x=d[pcol], name=b, orientation="h",
                boxpoints="all", jitter=0.4, pointpos=0,
                marker=dict(color=ACCENT if focus else CONTEXT, size=8,
                            line=dict(color=SURFACE, width=2)),
                line=dict(color=ACCENT if focus else CONTEXT, width=2),
                fillcolor="rgba(0,0,0,0)",
                customdata=d[["product"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>" + b + ": $%{x:.2f}<extra></extra>"))
        fig3.update_layout(boxmode="group", height=120 + 70 * len(cats),
                           margin=dict(l=10, r=10, t=30, b=10),
                           paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, font=dict(color=INK_2),
                           legend=dict(orientation="h", y=1.08, x=0, traceorder="normal"),
                           xaxis=dict(title="Price (USD)", tickprefix="$", gridcolor=GRID, zeroline=False),
                           yaxis=dict(gridcolor=GRID, autorange="reversed"))
        st.caption("Every dot is one real product (hover for the name). Dolls Kill in pink, competitors in gray.")
        st.plotly_chart(fig3, use_container_width=True)
    with right:
        if not gap_df.empty:
            g = gap_df.sort_values("Gap %")
            fig4 = go.Figure(go.Bar(
                y=g["Category"], x=g["Gap %"], orientation="h",
                marker=dict(color=[ACCENT if v >= 0 else "#3987e5" for v in g["Gap %"]],
                            cornerradius=4),
                text=[f"{v:+.0f}%" for v in g["Gap %"]], textposition="outside",
                textfont=dict(color=INK),
                hovertemplate="%{y}: %{x:+.1f}% vs market median<extra></extra>"))
            m = max(10, g["Gap %"].abs().max() * 1.35)
            fig4.update_layout(height=120 + 50 * len(g), margin=dict(l=10, r=30, t=30, b=10),
                               paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, font=dict(color=INK_2),
                               xaxis=dict(title="Dolls Kill median vs market median", range=[-m, m],
                                          ticksuffix="%", gridcolor=GRID, zerolinecolor=INK_2),
                               yaxis=dict(gridcolor=GRID), showlegend=False)
            st.caption("Dolls Kill median vs competitor median. Pink = Dolls Kill costs more, blue = less. Small samples, so read as directional.")
            st.plotly_chart(fig4, use_container_width=True)
    with st.expander("See the data table"):
        st.dataframe(gap_df.style.format({"Dolls Kill median": "${:.2f}",
                                          "Market median": "${:.2f}", "Gap %": "{:+.1f}%"}),
                     hide_index=True, use_container_width=True)
        st.dataframe(prices, hide_index=True, use_container_width=True)

# ================= PANEL 3: recommendations =================
st.divider()
st.header("3 · What I'd dig into first")

recs = []
if "trend" in findings:
    t = findings["trend"]
    if t["edc_t"]:
        e = t["seas"][t["edc_t"]]
        recs.append(("Spring is rave season, and the shopping starts a month before the festival.",
                     f"{t['spring'][t['edc_t']]:.0f}% of a year's “{t['edc_t']}” searches land in "
                     f"March–May, and they jump from {e.loc[3]:.0f}% of the year in March to "
                     f"{e.loc[4]:.0f}% in April, a full month before EDC. With EDC 2027 on May 14, "
                     "that puts the window for spring drops at early April, with March as the build-up. "
                     "With internal data, I'd check how closely drop dates line up with it."))
    recs.append((f"Festival demand is growing fast: “{t['fest_t']}” searches are up "
                 f"{t['mult'][t['fest_t']]:.1f}x since {t['g0']}.",
                 f"Comparing the same months (Jan–{MONTHS[t['gm']-1]}), “{t['fest_t']}” grew "
                 f"{t['mult'][t['fest_t']]:.1f}x and “{t['rave_t']}” grew "
                 f"{(t['mult'][t['rave_t']]-1)*100:+.0f}% from {t['g0']} to {t['g1']}. Festival searches "
                 f"also hold up through the summer ({t['seas'][t['fest_t']].loc[[6,7,8,9]].sum():.0f}% of "
                 "the year lands June–September), so the season is longer than just spring."))
if "gaps" in findings and not findings["gaps"].empty and "markdown" in findings:
    g = findings["gaps"]; md = findings["markdown"]
    dkn = [b for b in md.index if b.lower().replace(" ", "") == "dollskill"]
    dk_md = md[dkn[0]] if dkn else 0
    comps = md.drop(dkn, errors="ignore").sort_values(ascending=False)
    comp_txt = " and ".join(f"{v:.0f}% of {k}{chr(39) if k.endswith('s') else chr(39) + 's'}"
                            for k, v in comps.items())
    hi_ = g.loc[g["Gap %"].idxmax()]; lo_ = g.loc[g["Gap %"].idxmin()]
    recs.append(("Dolls Kill holds full price while rave competitors discount almost everything.",
                 f"Right now {comp_txt} listings are marked down, vs {dk_md:.0f}% of Dolls Kill's. "
                 f"On what shoppers actually pay, Dolls Kill sits {hi_['Gap %']:+.0f}% vs the market in "
                 f"{hi_['Category'].lower()} and {lo_['Gap %']:+.0f}% in {lo_['Category'].lower()}. "
                 "That looks like a real brand strength. The question I'd love to answer with internal "
                 "data: how much of it is driven by newness landing inside the demand window above."))

custom = DATA / "my_takeaways.md"
if custom.exists() and custom.read_text().strip():
    st.markdown(custom.read_text())
elif recs:
    for i, (head, why) in enumerate(recs[:3], 1):
        st.markdown(f'<div class="rec"><b>{i}. {head}</b><div class="why">{why}</div></div>',
                    unsafe_allow_html=True)
else:
    st.info("Recommendations appear once the data above is loaded.")

st.markdown(
    "<br><div class='foot'>With internal data (sell-through, traffic, returns, email and "
    "paid-social performance), each of these becomes measurable, and that's the work I'd love "
    "to do as Dolls Kill's Culture & Commerce Analyst.</div>", unsafe_allow_html=True)

# ---------- footer ----------
st.divider()
st.markdown(
    "<div class='foot'><b style='color:#f5f5f2'>Saloni Bansal</b> · Business Data Analytics, "
    "W. P. Carey School of Business, ASU · "
    "<a href='https://linkedin.com/in/saloni-bansal2003' style='color:#ff3d9a'>LinkedIn</a> · "
    "<a href='https://sbansa46b4f9.myportfolio.com/work' style='color:#ff3d9a'>Portfolio</a> · "
    "<a href='https://github.com/salonibansal831' style='color:#ff3d9a'>GitHub</a><br>"
    "Built on public data only (Google Trends; public product listings collected Sep 29, 2026 from each brand's own site; published festival dates). "
    "Not affiliated with or endorsed by Dolls Kill. Directional, not a forecast.</div>",
    unsafe_allow_html=True)
