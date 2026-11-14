# Night Merchant: InstantGram SF — Design Document

Night Merchant: InstantGram SF is a reskin of **Night Merchant: All Roads Lead to Rome**. It keeps the
Rome edition's rules and engine. This document lists what changes. Anything not listed here works
the same as in the Rome edition.

---

## 1. Goods (Market layout, top to bottom)

| Row | InstantGram SF | Rome track (internal id) | Contents | Notes |
| :-- | :--- | :--- | :--- | :--- |
| 1 | **Weed** (+ hallucinogens) | Grain | Dime bags, pre-rolls, shrooms, LSD, edibles | Easy to sell, low risk, low violence, low profit. Can be sold in bulk. |
| 2 | **Party** | Marble | Molly, ketamine, GHB, 2C-B, tusi | Profitable, but a high price floor and limited demand. Safer. |
| 3 | **Uppers** — *Pill* / *Powder* | Animals (Meat / Exotic) | Addys, Abu Hilalain, Moda… / coke, crack, meth, speed | Almost all Uppers (17 of 18 across both Pill and Powder) have mandatory combat effects ranging from `2(R)-3(R)` up to `4(R)-2(R)`. Uppers with negative/poor combat effects are cheaper and have better resale profitability than high-CP Uppers. |
| 4 | **Opiates** — *Street* / *Pharma* | Wine (Cheap / Fine) | Heroin, tranq, fentanyl… / OC 80s, Hospital Heroin, Percs, Vikes | Highest margins: the **largest gap between the Abundant Wholesale Price (`-₿`) and the Precious Retail Price (`+₿`)**. Most dangerous; biggest enforcement. |
| 5 | **Weapons** | Weapons | Switchblade, Taser, Pipe Bomb … Draco AK, Bearcat .50 Cal | 16 Weapons spanning the full combat spectrum (`Use once for 1`, `Use once for (R)`, `Use once for 2(R)`, `(R)-1`, `1`, `2(R)-(R)`, `(R)`, `2(R)-1`, `(R)+1`, `2`, `3(R)-(R)`, `2(R)`, `3`, `(R)+2`, `2(R)+1`, `3(R)-1`). Single-use and low-CP weapons are cheap with high resale margins; heavy high-CP weapons (`2–3■`) are expensive with tight resale margins. |
| 6 | **Henchmen** | Henchmen | Big Mike, Lil' Tony, Rosa "La Flaca"… | Almost unchanged. |

> Implementation note: the engine keeps the Rome track ids. A display layer (`sfReskinText` in
> `app.js`) shows the InstantGram SF names everywhere in the UI.

## 2. Art Direction

- **Market board:** a **cheap opened suitcase sitting on a motel bed** (`ostia_market_board_bg.jpg`), with the motel floor and edge of the bed in the left-hand column, the central vertical spine splitting the 6×6 grid into 3 left and 3 right columns, and the 6 horizontal compartments stained with each row's trade (Row 1 Weed: kief, weed flakes, oil stains; Rows 2–3 Party/Uppers: scattered pills, capsules, crystals, gummies; Rows 3–4 Uppers/Opiates: smudges and streaks of white powder; Rows 4–5 Opiates/Weapons: droplets and light smudges of blood; Row 5 Weapons: gun-grease stains and fabric tears; Row 6 Henchmen: counterfeit-document ink stains and smeared lipstick).
- **Drug cards:** each border looks like a life-size bag of the drug, in the container or form it
  normally comes in, fitted to a square.
- **Weapon cards:** the borders carry fine-print spec details for the weapon.
- **Henchman cards:** look like a California driver's license.
- **Card backs (text-free artwork so deck titles can be overlaid/translated separately):**
  - **GOODS** (square): two stuffed black tactical duffel bags side-by-side filling the entire printable square edge-to-edge, leaving room across the center perpendicular to the bags for `GOODS`.
  - **INFLUENCE** (`2.25" × 3.5"`): hyper-realistic back of a dark matte-titanium smartphone matching the Influence card front, with the camera bump in the top-left corner and lock/volume buttons at the edge of the printable space, leaving the vertical center open for `INFLUENCE`.
  - **MISSIONS** (`2.25" × 3.5"`): hyper-realistic closed matte-black ThinkSlab laptop lid filling the printable space edge-to-edge, leaving the center open for `MISSIONS`.
  - **Criminals / Cops / Celebrities** (`2.25" × 3.5"`): hyper-realistic street-level vehicles seen from a very high overhead angle filling the printable space — a **white cargo van** (Criminals), an **SFPD police cruiser** (Cops), and a **sleek silver Tezla** (Celebrities).
- **SUV board** (replaces the suv mat): a large black SUV seen from above. Henchmen ride in the
  **front seats**; drugs and weapons go in the **back seats and trunk**.
- **SUV token** (replaces the Cart token): top-down dark SUV icon on the map.
- **Style:** a uniform board-game look in the spirit of Dope Wars.

## 3. Factions (short names: MAGA, ISIS, DSA, TECH, MS13)

| Rome faction (gem) | InstantGram SF | Celebrities / Cops / Criminals |
| :--- | :--- | :--- |
| Caracalla (Ruby) | **MAGA** | 3 / **14** / 2 |
| Geta (Emerald) | **ISIS** (rarest) | 4 / 1 / 4 |
| Domna (Diamond) | **TECH** (Tech Bros) | 7 / 8 / 4 |
| Plautilla (Sapphire) | **DSA** | **9** / 2 / 7 |
| Aurelius (Amethyst) | **MS13** | 2 / 2 / **6** |

### Alignment consequences

"Work for" means a positive encounter outcome. "Work against" means a negative one. These are applied to
encounter outcomes and to job completion and failure.

| Faction | Alignment Philosophy |
| :--- | :--- |
| **MAGA** | Likes TECH, but doesn't want the player to work with MS13, DSA, or ISIS |
| **TECH** | Ambivalent to MAGA; generally likes it when the player has hostile interactions with the other factions |
| **MS13** | Doesn't really care if the player has positive or hostile interactions with the other factions |
| **ISIS** | Doesn't want the player to have any positive interactions with any group other than MS13 and ISIS |
| **DSA** | Doesn't want the player to work with MAGA, TECH, and sometimes ISIS |

- **Simplified Pentagonal Rulebook Graphic Reference (low priority):**
  - `MAGA` → *likes* `TECH`, *hates* `MS13`
  - `TECH` → *doesn't hate* `MAGA`, *hates* `DSA`
  - `DSA` → *doesn't hate* `TECH`, *hates* `ISIS`
  - `ISIS` → *kinda likes* `DSA`, *likes* `MS13`
  - `MS13` → *doesn't hate* `MAGA`, *doesn't like* `ISIS`

### Faction Leaders

| Leader | Faction | Deck | Friendly Outcome | Hostile Outcome | Negative (`≤ -1`) | Neutral (`= 0`) | Positive (`≥ +1`) | Combat Formula |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Donald Trump** | MAGA | Celebrities | −Sapphire −Emerald *(no +Ruby: doesn't reward loyalty)* | +Sapphire +Diamond | Threat (`!!`) *(never attacks unless you refuse)* | Offer (`?`) | Deal (`?`: *Buy 1 Influence for ₿0.5?*) | `3(R)+3` |
| **Mark Zuckerberg** | TECH | Celebrities | +Ruby −Sapphire *(no +Diamond: rest of TECH doesn't like you)* | −Ruby −Diamond | Attack at `≤ -2`; Threat (`!!`) at `-1` | Threat (`!!`) | Threat (`!!`) | `4(R)+1` |
| **Nayib Bukele** | MS13 | Cops | +Amethyst −Ruby | −Amethyst | Attack (`⚔`) | Threat (`!!`) | Offer (`?`) | `3X` |
| **Jared Kushner** | ISIS | Cops | +Emerald −Diamond | −Emerald −Ruby | Attack (`⚔`) | Offer (`?`) *(undercover)* | Threat (`!!`) *(ride or die)* | `2X(R)` |
| **Ocasio-Cortez** | DSA | Criminals | +Sapphire −Ruby −Emerald | −Sapphire +Diamond | Attack (`⚔`) | Demand (`!`) | Deal (`?`) | `3X(R)-3` |

### Behavior

| Faction | Attacks when your favor is | Notes |
| :--- | :--- | :--- |
| MS13 | ≤ −1 | Never attacks at 0 |
| ISIS | ≤ 0 | Poor: cash rewards ×0.6 (Kushner is undercover at 0 and offers instead of attacking) |
| MAGA | ≤ −1 | Trump never attacks automatically unless you refuse his threat |
| DSA | ≤ −2 | Ocasio-Cortez attacks at ≤ −1 |
| TECH | ≤ −2 | Rich: cash rewards ×1.5 |

## 4. Combat Strength

Each Rome die `R` has faces `[0, 0, 1, 1, 2, 3]` with expected value $E[R] = 7/6 \approx 1.167$.
- **Celebrities** encounter spaces always have 1 icon, so **Celebrities combat formulas never contain `X`**: they span 25 distinct non-`X` formulas from `1`, `3(R)-2(R)`, `2(R)-(R)`, `(R)`, `2(R)-1`, `2`, `(R)+1`, `3(R)-(R)`, `2(R)`, `3(R)-1`, `3`, `(R)+2`, `2(R)+1`, `3(R)`, `4`, `(R)+3`, `2(R)+2`, `3(R)+1`, `4(R)`, `2(R)+3`, `3(R)+2`, `4(R)+1` (**Zuckerberg**), `5(R)`, `3(R)+3` (**Trump**), up to `6(R)` (**Elon Musk**).
- **Cops** and **Criminals** encounter spaces range from `1–4` icons, so **all Cops and Criminals combat formulas are functions of `X`**: spanning `X(R)-X`, `X-1`, `X(R)-1`, `X`, `X(R)`, `2X(R)-X(R)`, `2X(R)-3`, `2X(R)-2`, `X+1`, `X(R)+1`, `2X-1`, `2X(R)-X`, `2X(R)-1`, `X(R)+2`, `2X`, `X(R)+X-1`, `X(R)+X`, `2X+1`, `X(R)+3`, `X(R)+X+1`, `2X(R)` (**Kushner**), `2X(R)+1`, `3X-1`, `2X(R)+2`, `3X(R)-3` (**Ocasio-Cortez**), `X(R)+2X`, `2X(R)+X`, `3X` (**Bukele**), `3X(R)` (**Mayor Lurie**), and `3X(R)+X` (**Sam Altman**).

## 5. Job Trends & Rewards

Each list runs from most likely to least likely.

| Faction | Jobs | Rewards |
| :--- | :--- | :--- |
| **DSA** | Sell Weed at a discount, sell Party at a discount, deliveries, kill Celebrities, kill Cops | Influence, Henchmen, Weapons |
| **MAGA** | Sell Uppers at a premium, sell Opiates at a discount, sell Weed at a premium, kill Criminals, kill Celebrities | Weapons, Uppers, Opiates, cash |
| **TECH** | Sell Party at a premium, sell Uppers at a premium, sell Weed at a premium, deliveries, hold 6 Influence cards, kill Celebrities | Cash, faction standing, Influence, Party, Weed |
| **MS13** | Sell Opiates at a premium, kill Cops, kill Criminals, kill Celebrities, sell Uppers at a premium, sell Weed, sell Party, deliveries | Opiates, Uppers, Party, Henchmen, cash, Weapons |
| **ISIS** | Sell Weapons at a premium, deliver Weapons, kill Celebrities, kill Cops, deliver Opiates, deliver Weed | Opiates, cash, Weed, Henchmen, Weapons, Influence |

- **Influencer**: Hold 6 Influence cards in your hand (Influence cards tucked under Schizophrenic jobs don't count). Reward: `1(R)` Influence cards + `₿0.2`, `+Diamond`, `-Emerald`.
- **Regime Change** (was Regicide): completed if Donald Trump or Jared Kushner is defeated by any
player. **Witness Protection** (was Regime Change) cancels it.

## 6. Encounter Decks

| Rome | InstantGram SF |
| :--- | :--- |
| Celebrities | **Celebrities** |
| Criminals | **Criminals** |
| Cops | **Cops** |
| Protesters | **Protesters** |
| Theatre Troupe | **Stand-Up Comic** |
| Schizophrenic | **Schizophrenic** |

### Celebrities

| Faction | Characters |
| :--- | :--- |
| TECH | Mark Zuckerberg *(Leader)*, Brian Chesky *(T1)*, Dario Amodei *(T2)*, Daniela Amodei *(T2)*, Crypto Influencer, Startup Founder, AI Ethicist |
| MAGA | Donald Trump *(Leader)*, Elon Musk *(T1)*, Peter Thiel *(T1)* |
| DSA | Jensen Huang *(T2)*, Bernie Sanders, Cornel West, Drag Queen, Tenured Professor, Indie Podcaster, Burning Guy Artist, Muralist, Climate Activist |
| MS13 | Steph Curry *(T1)*, Chesa Boudin |
| ISIS | Alice Huang *(T1)*, Dr. Oz, Edgelord Streamer, Radicalized YouToober |

### Cops

| Faction | Characters |
| :--- | :--- |
| TECH | Mayor Lurie *(Top)*, Scott Wiener *(T2)*, Paul Graham, FBI, CIA, Meter Maid, Traffic Cop, Rookie |
| MS13 | Nayib Bukele *(Leader)*, Dirty Cop |
| ISIS | Jared Kushner *(Leader)* |
| DSA | Dean Preston, Firefighters |
| MAGA | Harmeet Dhillon, Vivek Ramaswamy, Rudy Giuliani, SFPD, DEA, ICE, Homeland Security, SFPD Narcotics Unit, DEA Task Force, ICE Raid Team, Border Patrol, CHP Trooper, Sheriff's Deputy, Muni Fare Inspector |

### Criminals

| Faction | Characters |
| :--- | :--- |
| TECH | Sam Altman *(Top)*, Palmer Luckey, VC Capitalist, Crypto Scammer |
| MAGA | KKK *(T1)*, Pot Farmers *(T3)* |
| ISIS | International Terrorist *(T1)*, Domestic Terrorist *(T2)*, Bashar al-Assad, Abu Bakr al-Baghdadi |
| DSA | Ocasio-Cortez *(Leader)*, Pimp *(T1)*, London Breed, Homeless *(T2)*, Illegal *(T2)*, Unhoused *(T3)*, Undocumented *(T3)* |
| MS13 | Elmer Rodriguez *(Top)*, Clique Enforcer, Sicario, Gang Banger, Bad Hombre, Coyote |

### Reserve cards

`src/data/reserve_cards.json` holds cards that were pulled from the decks, with all their stats, so they can be added back later. If other factions grow, these can regrow ISIS.

| Card | Faction & deck | Why it was pulled |
| :--- | :--- | :--- |
| Hamas, Hezbollah, Houthis, Iran | ISIS Criminals | Removed to keep ISIS the rarest faction |

## 7. Ballot Initiatives (was Political Climate)

See the in-game board. The Rome mechanics stay, retitled for the new factions:

| Faction | Option 1 | Option 2 | Option 3 |
| :--- | :--- | :--- | :--- |
| MAGA | Mass Deportation | Recall Election | Back the Blue |
| ISIS | Decapitation (Most ISIS favor loses ₿2.5) | Fatwa (was Infidel Tax) | Sanctuary City (everyone starts with a free Emerald) |
| TECH | Series A | Conflict of Interest | Lobbying Blitz (Diamonds → Rubies or Sapphires) |
| DSA | Billionaire Tax | Mutual Aid | Rent Control |
| MS13 | Protection Racket | Plata o Plomo | Clique Fence |
| Gigs | Five-Star Courier | Full Time Employee (receive A × B ₿: A = your gems of one faction, B = jobs completed for it) | Surge Pricing |

## 8. Currency & Price Terminology

**1 Denarius = 0.1 Bitcoin (₿).** All amounts are shown in ₿. Physical edition tokens: about 100 × ₿0.1, about 100 × ₿1, and 10 × ₿10.
- **Wholesale Price (`-₿`):** Buy price row on Goods cards (and Hire cost on Henchman cards).
- **Retail Price (`+₿`):** Sell price row on Goods cards (and Fenced payout row on Encounter Job cards).
- **Scarcity Influence Cards:** Both **Surprise Shipment** (`inf_35`) and **Puffery** (`inf_46`) remain in effect for the **whole Night**.

## 9. The Map (6×6, north at the top)

| | A | B | C | D | E | F |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **1** | Land's End (+Celeb +Cop) | **Presidio** 🌉 GG Bridge | Marina (++Celeb) | Wharf (+Celeb +Cop +Crim) | Telegraph (+Celeb +Cop) | **Treasure** 🌉 Bay Bridge |
| **2** | Richmond (+Cop) | Pac Heights (+Celeb) | Russian (++Celeb) | Nob Hill (++Crim) | Chinatown (++Cop) | Embarcadero (+Celeb +Cop) |
| **3** | GG Park (+Crim +Celeb +Cop) | Japantown (+Celeb +Cop) | **Civic Center** 💊 market | **Tenderloin** 💊 market | SoMa (++Crim) | Ball Park (++Cop +Celeb, stadium gambling) |
| **4** | Sunset (+Cop) | Haight (+Celeb) | Castro (+Celeb +Crim) | **Job** 💊 market | Potrero (+Celeb) | Dogpatch (+Crim) |
| **5** | **Merced** 🛣 Route 1 | Twin Peaks (+Celeb) | Noe (+Celeb +Cop) | Dolores (+Celeb +Crim) | Bernal (+Crim) | **Bayview** 🛣 US-101 (+Crim +Cop) |
| **6** | Daly City (+Crim) | Ingleside (+Crim) | Sunnyside (+Crim) | **Excelsior** 🛣 I-280 (+Crim +Cop) | Visitacion (+Crim) | Hunter's (++Crim +Cop) |

### Neighborhood markers, Reachability & Danger Hierarchy

- **+ / ++ / +++:** the share of the cell's 12 tiles that carry that encounter type (3, 5, or 7 tiles). More pluses also allow higher encounter multipliers.
- **💊 Open-air markets** follow the Rome Forum rules. Their edges carry **+++ Criminals** and **++ Cops**.
- **Difficult-to-Reach Tiles:**
  - **Treasure Island (`F1`):** Almost impossible to reach from Chinatown (`E2`) or Telegraph (`E1`) (requires paying a high toll or facing a high-count Cops/Criminals encounter at a minimum, mostly blocked `red`). Similarly, almost impossible to go anywhere from Treasure Island (`F1`) except Embarcadero (`F2`) (and off-board Bay Bridge exit `E`).
  - **Presidio (`B1`):** Generally only connects to Marina (`C1`) and Richmond (`A2`), and vice-versa (`B1` edges to `A1`, `B2`, `C2` and `A1:E`, `B2:N`, `C2:NW` are nearly always `red`).
  - **Ball Park (`F3`):** Very hard to get to from any direction (`F2:S`, `E2:SE`, `E3:E`, `E4:NE`, `F4:N`).
  - **Steep Hills — Potrero (`E4`), Nob Hill (`D2`), Twin Peaks (`B5`), Telegraph (`E1`), and Pac Heights (`B2`):** Hard to get to from any direction.
- **Tile Danger Hierarchy (Blocked Exits, Cops/Criminals Exits & `X` Multipliers):**
  - **Tier 1 (Most Dangerous):** **Civic Center (`C3`)**, **Tenderloin (`D3`)**, **Job (`D4`)**, **SoMa (`E3`)**, and **Hunter's (`F6`)** — highest number of blocked exits (`red`), most exits with Cops and Criminals encounters, and largest numbers (`X = 3–4`) of Criminals and Cops per encounter.
  - **Tier 2 (Second Most Dangerous):** **Chinatown (`E2`)**, **Daly City (`A6`)**, **Bayview (`F5`)**, **Ball Park (`F3`)**, **Ingleside (`B6`)**, **Sunnyside (`C6`)**, **Excelsior (`D6`)**, **Visitacion (`E6`)**, and **Bernal (`E5`)** — follow right behind Tier 1 in blocked exits, Cops/Criminals exits, and encounter multipliers (`X = 2–3`).

### Entry points and escape routes

- Players enter only at the 5 entry points: Presidio (GG Bridge), Treasure (Bay Bridge), Merced (Route 1), Bayview (US-101), and Excelsior (I-280).
- **West (Pacific):** essentially no exits; a rare, expensive Speedboat (8–10).
- **North & East (Bay):** more and cheaper boats: Sailboat (1), Ferry (2), Cargo Ship (3).
- **South (Peninsula):** the most exits by far, generally free.


## 10. Days, Boards & Card Styles

- **Days replace nights:** Thursday becomes **Thursday**, Friday **Friday**, Saturday **Saturday**. Sunday Reckoning becomes **Sunday Morning Reckoning**.
- **Ballot Initiatives board:** styled after **Civic Center** (City Hall dome, ballot-measure placards).
- **Clock board:** styled as a **parking meter**, with the 10 night hours as the meter's time scale and a symbol key explaining `[computer]` (Top Job Deck) and `[cash]` (Job).
- **Job cards:** look like emails, text messages, contracts, dossiers, or handwritten notes.
- **Influence cards:** look like InstantGram posts, ClockTok posts, YouToob pages, FaceSpace profiles, or LinkedOut profiles.
- **Job, Influence & Encounter cards (2.25" × 3.5"):**
  - On **Encounter cards**, Friendly and Hostile Outcomes and Job/Combat Rewards sit in the top and bottom outcome bars / phone bezels (with a black border around symbols and white text when printed on a light background):
    1. **Friendly Outcome & Job Reward (Top Bar / Bezel):**
       - **Top-Left:** Large **Green Thumbs-Up** (`👍` in green) + `:` + large **Friendly Outcome Faction Gems** (`54px`, with a bold red diagonal line crossed through negated gems).
       - **Top-Right:** All-white **Cash Stack (`[cash]`)** symbol + **Job/Friendly Reward** (`:₿...`) in bold white text.
    2. **Combat Loot & Hostile Outcome (Bottom Bar / Bezel):**
       - **Bottom-Left:** All-white **Pistol (`[pistol]`)** symbol + **Combat Reward / Loot** (`:₿...`) in bold white text.
       - **Bottom-Right:** **Red Thumbs-Up pointing UP** on the right, with large **Hostile Outcome Faction Gems** (with a bold red diagonal line crossed through negated gems) + `:` to its left (so that when the card is turned 180° upside-down and tucked under the player's SUV mat, the red thumb points downward on the top-left and precedes the hostile gems).
    3. **Name & Bio**
    4. **Large Combat Formula** (`[pistol] : Formula`, sized as large as or larger than the posture bar numbers)
    5. **Faction Posture Bar** (Single uniform color bar matching the card's faction — MAGA Ruby, TECH Diamond, DSA Sapphire, MS13 Amethyst, ISIS Emerald — divided into vertical compartments):
       - At most **one** Attack cell (`[pistol]`).
       - At most **one** bespoke Job cell (`[cash]?`, `[cash]!`, or `[cash]!!`), meaning the NPC is offering/demanding/threatening the bespoke job described in the lower card area.
       - At most **one** bespoke Deal/Demand cell (`?`, `!`, or `!!`), meaning the NPC is requesting/demanding/threatening the deal described in the lower card area.
       - Zero, one, or more Top Job Deck cells (`[computer][cash]?`, `[computer][cash]!`, or `[computer][cash]!!`), signaling that the top card from the Job deck is offered/demanded/threatened at that favor level.
    6. **Lower Detail Section** (Reserved strictly for explaining the bespoke demand(s), job(s), and/or deal(s) specific to that card, tracking with the NPC's faction flavor, plus optional 5-column Retail Price `+₿` table; does not repeat the `[computer]`/`[cash]` key).
  - **Card Face Archetypes by Deck:**
    - **Cops:** Police identification card (**inside the upper section of the phone screen**, filling the same upper space as the WikiBio infobox), `SF Chronicler` article, `SF Standpoint` article, `Californiac Post` article, `SF Inquirer` article, police department `FaceSpace` page, police department `InstantGram` account.
    - **Celebrities:** `WikiBio` (light gray `#eaecf0`/`#f8f9fa` & blue `#3366cc`) page, `New York Chimes` article, `Washington Roast` article, `Stall Street Journal` article, `LinkedOut` bio, `YouToob` profile, `FaceSpace` profile, `InstantGram` account.
    - **Criminals:** `SnatchTap` profile, `VendMo` account, `$CashNet` account, `CubePay` account, `PayPals` account, `greg's list` ad, `InstantGram` account, `ClockTok` account, `OnlyStans` account.
- **Card titles:** forms and strains go in helper text under the name, e.g. **OG Kush** with *Flower* underneath.

## 11. SUV Space

| Category | SUV space |
| :-- | :-- |
| Weed | 1–2 ■ |
| Party | 1–2 ■ (reduced) |
| Pill Uppers | 1 ■ |
| Powder Uppers | 1–2 ■ (reduced) |
| Opiates | 1 ■ |
| Weapons | 1–3 ■ |

## 12. Contraband Threats (Cops & Criminals)

| Cargo | Threats | Notes |
| :-- | :-- | :-- |
| Opiates | **20** | 16 are attacks if you are carrying (on the strongest cards); 4 are threats to take it all |
| Weapons | 16 | |
| Uppers | 14 | |
| Party | 5 | |
| Weed | 2 | |
| Henchmen | 1 | **ICE** takes all of your Henchmen |

- One ISIS Celebrity (**Radicalized YouToober**) attacks at neutral, so zero standing is *almost* safe with Celebrities.

## 13. Henchmen

- The Henchmen who add a henchman seat (+▲) or raise sale prices are women: **Big Tina** (+▲), **Rosa "La Flaca"** (Street Opiates sell +1 step), and **Nurse Keisha** (Pill Uppers sell +1 step).
- **Felicia** is the strongest Henchman: 3(R) +1 CP and ignores 1 wound (a nod to *The Wire*).

## 14. Positive vs Hostile Outcomes (Stand-Up Comic)

Every gem change is tagged by how it happened.

| Outcome type | What counts |
| :-- | :-- |
| **Positive** | Satisfying demands, accepting offers, buying or selling with NPCs, playing Influence cards, completing jobs |
| **Hostile** | Refusing threats or demands, combat, being unable to pay, failing or abandoning jobs |

The Stand-Up Comic table now works on outcomes, not on gem signs:

| Roll | Effect |
| :-- | :-- |
| **0 (Roasted)** | Undo every gem change from **Positive outcomes** |
| **I (The Bit)** | Undo every gem change from **Hostile outcomes** |


## 15. Job Locations & Delivery Rewards

Direct sale and delivery destinations come from the patron faction's turf:

| Faction | Turf |
| :-- | :-- |
| **MAGA** | Wharf, Ball Park, Hunter's, Presidio, Russian, Telegraph, Pac Heights, Twin Peaks, Daly City, Chinatown |
| **DSA** | Castro, Richmond, Haight, SoMa, Bernal, Noe, Dolores, Dogpatch, Civic Center, Mission, Merced |
| **ISIS** | Ball Park, Civic Center, Embarcadero, Castro, Treasure, Land's End, Sunset, Sunnyside, Mission, Bayview, Excelsior |
| **TECH** | Embarcadero, SoMa, Japantown, Dolores, Nob Hill, Marina, Tenderloin, Twin Peaks, Mission, Dogpatch, Potrero, Telegraph |
| **MS13** | Mission, Potrero, Visitacion, Hunter's, Bayview, Ingleside, Treasure, Richmond, GG Park, Wharf, Merced, Sunnyside, Excelsior, SoMa, Tenderloin, Dolores |

- **Pick-ups:** placed at least 3 spaces from the destination, preferring neighborhoods with no other pick-up, sale, or delivery tied to them. Routes are spread across directions.
- **Delivery reward:** `(6 × distance + 5 × cargo size) × risk` in ₿0.1 units.

  | Cargo | Risk |
  | :-- | :-- |
  | Opiates | 1.5 |
  | Uppers | 1.25 |
  | Party | 1.0 |
  | Weed | 0.8 |
  | Weapons | 1.2 × 0.6 |

  Weapon deliveries are discounted because the weapon gives 1(R) CP while you carry it.
