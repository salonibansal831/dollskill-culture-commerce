# Culture & Commerce Snapshot: built for Dolls Kill
by Saloni Bansal

A one-page Streamlit dashboard built only on public data:
- **Google Trends** (US, monthly, Sep 2021 to Sep 2026): "rave outfits", "festival outfit", "EDC outfit", plus the by-state split
- **147 real product prices** collected Sep 29, 2026 from the Dolls Kill, iHeartRaves and Rave Wonderland websites
- **Published festival dates** (Ultra, Coachella, EDC, Lollapalooza, Burning Man, Halloween)

All data is already inside the `data/` folder. Nothing to fill in.

---

## STEP 1: Put the code on GitHub (10 min)

1. Unzip this folder on your laptop.
2. Go to **github.com**, then **+** (top right), then **New repository**
   - Name: `dollskill-culture-commerce`
   - Set it to **Public**. Don't tick "Add a README" (you already have one).
   - Click **Create repository**
3. On the next page, click **"uploading an existing file"**
4. Drag in **everything inside** the unzipped folder: `app.py`, `requirements.txt`, `README.md`, and the `data` folder.
5. **The `.streamlit` folder is hidden on Mac.** In the Finder window press **Cmd + Shift + .** (period) to show it, then drag it in too. (It holds the dark theme. Without it the app still works, just in light mode.)
6. Click **Commit changes**.

Check: your repo page should show `app.py`, `requirements.txt`, `README.md`, `data/`, `.streamlit/`.

## STEP 2: Make it a live website (5 min, free)

1. Go to **share.streamlit.io** and **Continue with GitHub**
2. Click **Create app**, then **Deploy a public app from GitHub**
3. Repository: `salonibansal831/dollskill-culture-commerce` · Branch: `main` · Main file: `app.py`
4. **App URL:** type something clean, like `dollskill-snapshot`, which gives you `dollskill-snapshot.streamlit.app`
5. Click **Deploy** and wait 2 to 3 minutes.

Check: open the link **on your phone**. Scroll top to bottom and make sure every chart loads.

> Streamlit free apps "go to sleep" after a few days without visitors. Open your link yourself
> the morning you send it (and every couple of days after) so Bobby never sees a "wake up" screen.

## STEP 3: Record a 60 to 90 second walkthrough (20 min)

1. Install **Loom** (loom.com, free) and choose **Screen + Camera**
2. Open your live dashboard in the browser, then record. Rough flow (talk, don't read):
   - **Intro (5s):** "Hi Bobby, I'm Saloni. I built this for Dolls Kill to show what a Culture & Commerce Analyst would actually do."
   - **Growth (20s):** "'Festival outfit' searches are up 2.3x since 2022, so the category is growing fast."
   - **Timing (20s):** "More than half of EDC outfit searches happen March to May, and they double from March to April, a full month before the festival. That's when the shopping actually happens."
   - **Price (20s):** "92% of iHeartRaves' listings are marked down right now, vs 12% of Dolls Kill's. Dolls Kill holds full price, and that says a lot about the brand."
   - **Close (10s):** "With your internal data, all of this becomes measurable. That's the job I'd love to do."
3. Trim the start and end in Loom. That's all the editing it needs.
4. Copy the Loom share link.

## STEP 4: Send it to Bobby on LinkedIn

Reply in the same LinkedIn thread with a short message, the Loom link and the dashboard link.

---

## Before you hit send
- [ ] Dashboard opened on your phone today and every chart loads
- [ ] Footer links (LinkedIn / portfolio / GitHub) work
- [ ] You can explain every number in your own words (he may ask)
- [ ] Loom is under 90 seconds and the link opens without a login

## If he asks "how did you get this?"
- Search data: Google Trends export, monthly, US, 5 years.
- Prices: each brand's own public product listings on Sep 29, 2026 (regular price and current selling price). Around 20 products per brand per category. Samples are small, so the price gaps are directional.
- Nothing internal, nothing scraped at scale. Every product row has its URL in `data/prices.csv`.

## Files
| File | What it is |
|---|---|
| `app.py` | the dashboard |
| `data/trends.csv` | Google Trends, interest over time |
| `data/trends_by_state.csv` | Google Trends, by state |
| `data/prices.csv` | 147 products with URLs |
| `data/festivals.csv` | festival dates 2021 to 2027 |
| `.streamlit/config.toml` | dark theme and pink accent |
| `requirements.txt` | what Streamlit Cloud installs |
