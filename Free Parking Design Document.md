# Night Merchant: Free Parking — Design Document

Night Merchant: Free Parking is a reskin of **Night Merchant: All Roads Lead to Rome**. It keeps the
Rome edition's rules and engine. This document lists what changes. Anything not listed here works
the same as in the Rome edition.

---

## 1. Goods (Market layout, top to bottom)

| Row | Free Parking | Rome track (internal id) | Contents | Notes |
| :-- | :--- | :--- | :--- | :--- |
| 1 | **Weed** (+ hallucinogens) | Grain | Dime bags, pre-rolls, shrooms, LSD, edibles | Easy to sell, low risk, low violence, low profit. Can be sold in bulk. |
| 2 | **Party** | Marble | Molly, ketamine, GHB, 2C-B, tusi | Profitable, but a high price floor and limited demand. Safer. |
| 3 | **Uppers** — *Pill* / *Powder* | Animals (Meat / Exotic) | Adderall, Captagon… / coke, crack, meth, speed | Powder Uppers affect combat, for better or worse (like Exotic Animals). |
| 4 | **Opiates** — *Street* / *Pharma* | Wine (Cheap / Fine) | Heroin, tranq, fentanyl… / Oxy, Dilaudid, fentanyl patches | Highest margins: the **largest gap between the Abundant buy price and the Precious sell price**. Most dangerous; biggest enforcement. |
| 5 | **Weapons** | Weapons | Brass knuckles … AR-15 | Almost unchanged. The **Kevlar Vest** has a high purchase floor and very low profitability. The **Pipe Bomb** can't be used in combat (0 CP) but is very profitable. |
| 6 | **Henchmen** | Guards | Big Mike, Lil' Tony, Rosa "La Flaca"… | Almost unchanged. |

> Implementation note: the engine keeps the Rome track ids. A display layer (`sfReskinText` in
> `app.js`) shows the Free Parking names everywhere in the UI.

## 2. Art Direction

- **Market board:** a **briefcase**.
- **Drug cards:** each border looks like a life-size bag of the drug, in the container or form it
  normally comes in, fitted to a square.
- **Weapon cards:** the borders carry fine-print spec details for the weapon.
- **Henchman cards:** look like a California driver's license.
- **SUV board** (replaces the cart mat): a large black SUV seen from above. Henchmen ride in the
  **front seats**; drugs and weapons go in the **back seats and trunk**.
- **Style:** a uniform board-game look in the spirit of Dope Wars.

## 3. Factions (short names: MAGA, ISIS, DSA, TECH, MS13)

| Rome faction (gem) | Free Parking | Celebrities / Cops / Criminals |
| :--- | :--- | :--- |
| Caracalla (Ruby) | **MAGA** | 3 / **14** / 2 |
| Geta (Emerald) | **ISIS** (rarest) | 4 / 1 / 4 |
| Domna (Diamond) | **TECH** (Tech Bros) | 7 / 8 / 4 |
| Plautilla (Sapphire) | **DSA** | **9** / 3 / 6 |
| Aurelius (Amethyst) | **MS13** | 2 / 2 / **6** |

### Alignment consequences

"Work for" means a positive encounter outcome. "Work against" means a negative one. These are applied to
encounter outcomes and to mission completion and failure.

| Faction | Work **for** them | Work **against** them |
| :--- | :--- | :--- |
| **ISIS** | Sometimes makes everyone except MS13 like you | Sometimes the DSA dislikes you; MAGA often likes you |
| **MS13** | MAGA likely dislikes you | Sometimes the DSA and the Tech Bros dislike you |
| **TECH** | MAGA often likes you; the DSA often dislikes you | MAGA dislikes you; the DSA likes you |
| **MAGA** | **Everyone hates you** | **Everyone likes you** |
| **DSA** | TECH sometimes likes you; ISIS and MAGA often hate you | TECH sometimes likes you; MAGA sometimes likes you |

- Work for DSA, TECH, or MAGA → ISIS likely hates you (−Emerald).
- What you do for or against anyone except MS13 usually doesn't change how MS13 feels.

### Behavior

| Faction | Attacks when your favor is | Notes |
| :--- | :--- | :--- |
| MS13 | ≤ −1 | Never attacks at 0 |
| ISIS | ≤ 0 | Poor: cash rewards ×0.6 |
| MAGA | ≤ −1 | |
| DSA | ≤ −2 | |
| TECH | ≤ −2 | Rich: cash rewards ×1.5 |

## 4. Combat Strength

**By faction:**

| Faction | Typical combat formula |
| :--- | :--- |
| TECH | Weakest: `XR−1` (meter maid), `XR−X` (traffic cop), `X` (rookie). Billionaires with bodyguards are outliers at `4XR` to `6XR`. |
| DSA | Next weakest: usually `XR`, sometimes ±1 |
| MAGA & ISIS | All over the map, but more often positive (`XR+1`, `XR+2`, `XR+X`) |
| MS13 | Always strong. `XR+X` by default; leaders `2X–3X` |

**By tier:** Leader / Top use 3× dice, Tier 1 uses 2×, Tier 2 uses 1×, and Tier 3 uses 1× with −1.

**By deck:** Cops +1 CP per icon (tougher than Criminals). Celebrities −1 (more vulnerable).
**Lurie** (`6XR+1`), **Musk** (`6XR+X`), and **Zuckerberg** (`6XR`) are the strongest NPCs in the
game.

## 5. Mission Trends & Rewards

Each list runs from most likely to least likely.

| Faction | Missions | Rewards |
| :--- | :--- | :--- |
| **DSA** | Sell Weed at a discount, sell Party at a discount, deliveries, kill Celebrities, kill Cops | Influence, Henchmen, Weapons |
| **MAGA** | Sell Uppers at a premium, sell Opiates at a discount, sell Weed at a premium, kill Criminals, kill Celebrities | Weapons, Uppers, Opiates, cash |
| **TECH** | Sell Party at a premium, sell Uppers at a premium, sell Weed at a premium, deliveries, kill Celebrities | Cash, faction standing, Influence, Party, Weed |
| **MS13** | Sell Opiates at a premium, kill Cops, kill Criminals, kill Celebrities, sell Uppers at a premium, sell Weed, sell Party, deliveries | Opiates, Uppers, Party, Henchmen, cash, Weapons |
| **ISIS** | Sell Weapons at a premium, deliver Weapons, kill Celebrities, kill Cops, deliver Opiates, deliver Weed | Opiates, cash, Weed, Henchmen, Weapons, Influence |

**Regime Change** (was Regicide): completed if Donald Trump or Jared Kushner is defeated by any
player. **Witness Protection** (was Regime Change) cancels it.

## 6. Encounter Decks

| Rome | Free Parking |
| :--- | :--- |
| Patricii | **Celebrities** |
| Nefarii | **Criminals** |
| Legiones | **Cops** |
| Angry Mob | **Protesters** |
| Theatre Troupe | **Stand-Up Comic** |
| Soothsayer | **Schizophrenic** |

### Celebrities

| Faction | Characters |
| :--- | :--- |
| TECH | Mark Zuckerberg *(Leader)*, Brian Chesky *(T1)*, Dario Amodei *(T2)*, Daniela Amodei *(T2)*, Crypto Influencer, Startup Founder, AI Ethicist |
| MAGA | Donald Trump *(Leader)*, Elon Musk *(T1)*, Peter Thiel *(T1)* |
| DSA | Jensen Huang *(T2)*, Bernie Sanders, Cornel West, Drag Queen, Tenured Professor, Indie Podcaster, Burning Man Artist, Muralist, Climate Activist |
| MS13 | Steph Curry *(T1)*, Chesa Boudin |
| ISIS | Alice Huang *(T1)*, Dr. Oz, Edgelord Streamer, Radicalized YouTuber |

### Cops

| Faction | Characters |
| :--- | :--- |
| TECH | Mayor Lurie *(Top)*, Scott Wiener *(T2)*, Paul Graham, FBI, CIA, Meter Maid, Traffic Cop, Rookie |
| MS13 | Nayib Bukele *(Leader)*, Dirty Cop |
| ISIS | Jared Kushner *(Leader)* |
| DSA | Ocasio-Cortez *(Leader)*, Dean Preston, Firefighters |
| MAGA | Harmeet Dhillon, Vivek Ramaswamy, Rudy Giuliani, SFPD, DEA, ICE, Homeland Security, SFPD Narcotics Unit, DEA Task Force, ICE Raid Team, Border Patrol, CHP Trooper, Sheriff's Deputy, Muni Fare Inspector |

### Criminals

| Faction | Characters |
| :--- | :--- |
| TECH | Sam Altman *(Top)*, Palmer Luckey, VC Capitalist, Crypto Scammer |
| MAGA | KKK *(T1)*, Pot Farmers *(T3)* |
| ISIS | International Terrorist *(T1)*, Domestic Terrorist *(T2)*, Bashar al-Assad, Abu Bakr al-Baghdadi |
| DSA | Pimp *(T1)*, London Breed, Homeless *(T2)*, Illegal *(T2)*, Unhoused *(T3)*, Undocumented *(T3)* |
| MS13 | Elmer Rodriguez *(Top)*, Clique Enforcer, Sicario, Gang Banger, Bad Hombre, Coyote |

### Reserve cards

`src/data/reserve_cards.json` holds cards that were pulled from the decks, with all their stats, so they can be added back later. If other factions grow, these can regrow ISIS.

| Card | Faction & deck | Why it was pulled |
| :--- | :--- | :--- |
| Hamas, Hezbollah, Houthis, Iran | ISIS Criminals | Removed to keep ISIS the rarest faction |
| [removed] [removed] | DSA/ISIS Celebrity | Removed to keep the roster to clear public figures |

## 7. Ballot Initiatives (was Political Climate)

See the in-game board. The Rome mechanics stay, retitled for the new factions:

| Faction | Option 1 | Option 2 | Option 3 |
| :--- | :--- | :--- | :--- |
| MAGA | Mass Deportation | Recall Election | Back the Blue |
| ISIS | Fatwa | Infidel Tax | Threat Level Red |
| TECH | Series A | Conflict of Interest | Lobbying Blitz (Diamonds → Rubies or Sapphires) |
| DSA | Billionaire Tax | Mutual Aid | Rent Control |
| MS13 | Protection Racket | Plata o Plomo | Clique Fence |
| Gigs | Five-Star Courier | Yelp Reviews | Surge Pricing |

## 8. Currency

**1 Denarius = 0.1 Bitcoin (₿).** The ₿ display is not built yet.

## 9. The Map (6×6, north at the top)

| | A | B | C | D | E | F |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **1** | Land's End (+Celeb +Cop) | **Presidio** 🌉 GG Bridge | Marina (++Celeb) | Wharf (+Celeb +Cop +Crim) | Telegraph (+Celeb +Cop) | **Embarcadero** 🌉 Bay Bridge |
| **2** | Richmond (+Cop) | Laurel (+Celeb) | Pac Heights (++Celeb) | Nob Hill (++Crim) | Chinatown (++Cop) | Ballpark (++Cop +Celeb, stadium gambling) |
| **3** | GG Park (+Crim +Celeb +Cop) | Fillmore (+Celeb +Cop) | **Tenderloin** 💊 market | **Civic Center** 💊 market | SoMa (++Crim) | Potrero (+Celeb) |
| **4** | Sunset (+Cop) | Haight (+Celeb) | Diamond (++Celeb) | **Castro** 💊 market | Mission (++Crim) | Dogpatch (+Crim) |
| **5** | **Merced** 🛣 Route 1 | Ingleside (+Crim) | Miraloma (+Crim) | Noe (+Celeb +Cop) | Bernal (+Crim) | **Hunter's** 🛣 US-101 |
| **6** | Daly City (+Crim) | Crocker (+Crim) | Balboa (+Crim +Cop) | **Glen Park** 🛣 I-280 (+Crim +Cop) | Portola (+Celeb +Crim) | Bayview (++Crim) |

### Neighborhood markers

- **+ / ++ / +++:** the share of the cell's 12 tiles that carry that encounter type (3, 5, or 7 tiles). More pluses also allow higher encounter multipliers.
- **💊 Open-air markets** follow the Rome Forum rules. Their edges carry **+++ Criminals** and **++ Cops**.

### Entry points and escape routes

- Players enter only at the 5 entry points: Presidio, Embarcadero, Merced, Hunter's, and Glen Park.
- **West (Pacific):** essentially no exits; a rare, expensive Speedboat (8–10).
- **North & East (Bay):** more and cheaper boats: Sailboat (1), Ferry (2), Cargo Ship (3).
- **South (Peninsula):** the most exits by far, generally free.
