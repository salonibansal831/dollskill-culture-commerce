# Culture & Commerce Snapshot: Dolls Kill

**Live dashboard:** _add your Streamlit link here_

An independent analysis of when rave and festival demand happens, and where Dolls Kill sits on price against rave-wear competitors. It's built entirely on public data, as a working example of the Culture & Commerce Analyst role I proposed through Dolls Kill's *Name Your Job* program.

## Key findings

| | Finding |
|---|---|
| **Demand is growing** | "Festival outfit" searches are up **2.3x** (Jan–Sep 2026 vs the same months in 2022); "rave outfits" is up **26%**. |
| **Spring is the season** | **53%** of a year's "EDC outfit" searches fall in March–May, doubling from March to April, a month before EDC Las Vegas. |
| **Regional vocabulary** | "Rave" outpaces "festival" in every state, most strongly in the Mountain West and Southwest (Utah 80%). |
| **Full-price positioning** | **92%** of iHeartRaves listings and **25%** of Rave Wonderland listings were marked down, vs **12%** of Dolls Kill's. |

## What's in the dashboard

1. **Culture is a demand calendar:** five years of search interest, a month-by-month seasonality profile, and a state-level view of rave vs festival language.
2. **Where Dolls Kill sits on price:** 147 products across bodysuits and rompers, tops, bottoms, and platform shoes and boots, compared on list price and on current selling price.
3. **What I'd dig into first:** three data-backed questions I'd pursue with internal data (sell-through, traffic, email and paid-social performance).

## Data and method

| Source | Detail |
|---|---|
| Google Trends | US, monthly, Sep 2021 to Sep 2026; "rave outfits", "festival outfit", "EDC outfit"; plus the by-state breakdown |
| Product prices | Public product listings from dollskill.com, iheartraves.com and ravewonderland.com, collected Sep 29, 2026. Regular and current selling price per product, each with its source URL. |
| Festival calendar | Published dates for Ultra, Coachella, EDC Las Vegas, Lollapalooza, Burning Man and Halloween, 2021 to 2027 |

- **Seasonality** is each month's share of that year's total searches, averaged across complete years (2022–2025).
- **Growth** compares the same months across years, so a partial 2026 isn't compared with full years.
- **Price gaps** compare Dolls Kill's median price with the competitor median in each category. Sample sizes are modest (reported in the dashboard), so the gaps are directional.

No internal Dolls Kill data was used. This project is not affiliated with or endorsed by Dolls Kill.

## Tech

Python · pandas · Plotly · Streamlit

```
pip install -r requirements.txt
streamlit run app.py
```

## Author

**Saloni Bansal**, B.S. Business Data Analytics, W. P. Carey School of Business, Arizona State University
[LinkedIn](https://linkedin.com/in/saloni-bansal2003) · [Portfolio](https://sbansa46b4f9.myportfolio.com/work) · [GitHub](https://github.com/salonibansal831)
