# Night Merchant: Free Parking — Design Document

*Working titles from the notes: "Night Merchant: San Francisco" / "Free Parking SF".*

Night Merchant: Free Parking is a reskin of **Night Merchant: All Roads Lead to Rome**. It keeps the
rules, mechanics, and code of the Rome edition. This document lists what changes. Anything not listed
here stays the same.

> Transcription notes: Text in *[brackets]* marks a word that is hard to read in the handwritten pages,
> or a gap that the editor filled in. Each one is labeled.

---

## 1. Goods → Drugs

| Rome category | Free Parking category | Contents | Design notes (verbatim intent) |
| :--- | :--- | :--- | :--- |
| **Grain** | **Weed** (+ hallucinogens) | Weed, hallucinogens | Easy to sell, low risk, low violence, low profit. |
| **Animals** | **Uppers** | Cocaine, crack, meth, speed | Like exotic animals, they **affect the players in combat**, for better or worse. |
| **Wine** | **Opiates** | Heroin, fentanyl, barbiturates | Highest price margins and the most dangerous. They have the **largest difference between the Abundant purchase price and the Precious sale price**. Demand is in the dangerous parts of town. **Biggest enforcement.** |
| **Weapons** | **Weapons** | (unchanged category) | Almost nothing changes. The **bulletproof vest** has a high purchase floor and very low profitability (it replaces the *Lorica*). **Unusable weapons (a bomb)** are very profitable. |
| **Marble** | **Party Drugs** | Molly, ketamine | Profitable but a high price floor and limited demand. Safer. |
| **Guards** | **Henchmen** | — | Almost nothing changes. |

---

## 2. Card & Board Art Direction

- **Market board** looks like a **briefcase**.
- **Drug cards**: Each card's border makes it look like a **life-size bag of that drug**, in the
  container or form the drug normally comes in, fitted to a square.
- **Weapon cards**: The borders have **fine-text details about the weapon's specifications**
  (generally firearms).
- **Henchman cards** look like a **California driver's license**.
- **Cart board → SUV board** *(added note)*: Replace the cart mat with a board that looks like a
  **large black SUV** seen from above.
  - **Henchman storage** = the **front seats** (replaces the 2 Guard seats `▲`).
  - **Drug & weapon storage** = the **back seats and trunk** (replaces the 6 Cargo blocks `■`).
- **Overall art style**: A uniform board-game look that recalls **Dope Wars**: gritty
  late-'90s/2000s street style, bold flat colors, heavy ink outlines, a slightly pixel-retro feel.

---

## 3. Factions

The new factions only loosely follow the Rome factions. Each one keeps the old faction's gem and decree column.

| Rome faction (gem) | Free Parking faction | Favored goods | Deck representation (Celebrities / Cops / Criminals) |
| :--- | :--- | :--- | :--- |
| Caracalla (Ruby) | **MAGA** | Uppers | 2 / **14** / 3 — huge among Cops; a tiny bit of Celebrity (Musk); low among Criminals (pot farmers, KKK) |
| Geta (Emerald) | **ISIS** | Weapons | 4 / 2 / 5 — **the rarest faction**; mostly Criminals, then Celebrities, then Cops |
| Domna (Diamond) | **Tech Bros** | Party Drugs | 7 / 6 / 6 — equal across all three decks |
| Plautilla (Sapphire) | **DSA** | Weed | **10** / 3 / 3 — mostly Celebrities, some Criminals, very few Cops (the Firefighters) |
| Aurelius (Amethyst) | **MS-13** | Opiates | 3 / 3 / **9** — mostly Criminals; lowest among Celebrities and Cops |

**Members:** DSA: leftists, feminists, gays, natives, locals. Tech Bros: Lurie, Zuckerberg.

### Alignments

| Faction | Aligned with | Averse to |
| :--- | :--- | :--- |
| **MAGA** | Tech Bros; ISIS sometimes | MS-13 (primarily), DSA (hugely); ISIS sometimes |
| **ISIS** | MS-13 | Every other faction |
| **Tech Bros** | DSA and MAGA (somewhat) | ISIS (somewhat); indifferent to MS-13 |
| **DSA** | ISIS and MS-13 | MAGA (primarily), Tech Bros (sort of) |
| **MS-13** | DSA and ISIS (slightly) | MAGA (somewhat), Tech Bros (a little). The most indifferent faction. |

### Behavior

- **MAGA:** Back the Blue gives Cops +2 CP and the player +1 CP per positive Ruby.
- **ISIS:** Poor and violent. ISIS characters attack at 0 favor or lower, and their cash rewards are halved.
- **Tech Bros:** Very rich, vulnerable, and influential. Rewards are ×1.5 and combat is −1 CP.
- **MS-13:** Less likely than ISIS to attack at 0 favor, but always attacks at −1 or lower. Always very strong in combat (+1(R)+1 CP).

---

## 4. Political Climate (Decree) Board → **Ballot Initiatives**

The board is now **Ballot Initiatives**. It keeps the 6×3 layout and draft rules, but the decrees have been updated for the new factions.

| Column | Option 1 *(End-Game)* | Option 2 *(End-Game)* | Option 3 *(Mid-Game)* |
| :--- | :--- | :--- | :--- |
| **MAGA (Ruby)** | **Mass Deportation:** Least MAGA favor is eliminated (resolves first). | **Recall Election:** −10d per +Ruby; +5d per −Ruby. | **Back the Blue:** Cops +2 CP; +1 CP per +Ruby. |
| **ISIS (Emerald)** | **Fatwa:** Least ISIS favor loses 25d. | **Infidel Tax:** +15d per +Emerald if MAGA ≤ 0, else −10d per +Emerald; −5d per −Emerald. | **Threat Level Red:** Leaving SF by a Bridge or Freeway costs a 4d checkpoint bribe, waived with +1 Emerald or Shortcut. *(Replaces Divided Tiber.)* |
| **Tech Bros (Diamond)** | **Series A:** Most Tech Bros favor gains +20% wealth. | **Conflict of Interest:** −15d per ±Diamond. | **Lobbying Blitz:** Trade +Diamonds 1-for-1 into +Rubies (MAGA) or **+Sapphires (DSA)**. |
| **DSA (Sapphire)** | **Billionaire Tax:** Most DSA favor takes 15d from the wealthiest rival. | **Mutual Aid:** +10d per completed DSA mission. | **Rent Control:** Spend +Sapphires when selling for +1 Scarcity step per gem. *(Was Senatorial Privilege.)* |
| **MS-13 (Amethyst)** | **Protection Racket:** Most MS-13 favor gains 25d. | **Plata o Plomo:** +10d per ±Amethyst. | **Clique Fence:** Fenced cargo sells +1 Scarcity step higher and doesn't fail the mission. *(Was Smuggler's Fence.)* |
| **Gigs** | **Five-Star Courier:** Most completed missions +30d. | **Yelp Reviews:** +10d per completed / −10d per failed mission. | **Surge Pricing:** Missions pay 2×; failed missions fine 10d. |

---

## 5. Currency: Denarius → Bitcoin

**1 Denarius = 0.1 Bitcoin (₿).** All prices, tolls, wagers, fines, loans, and scores are shown in
₿ at one tenth of their Denarius value. For example, the 12(d) starting cash becomes **₿1.2**.

---

## 6. Encounter Decks & Tables

| Rome | Free Parking | Members |
| :--- | :--- | :--- |
| **Patricii** | **Celebrities** | Billionaires, politicians, academics, YouTubers |
| **Nefarii** | **Criminals** | Drug dealers, pimps, gang members, VC capitalists |
| **Legiones** | **Cops** | SFPD, DEA, FBI, ICE |
| Angry Mob | **Protesters** | No change |
| Theatre Troupe | **Stand-Up** | No change |
| Soothsayer | **Schizophrenic** | No change |

**Balance changes:**
- **Cops** are **significantly more dangerous** than the Rome Legiones.
- **Celebrities** are **slightly less dangerous** than the Patricii.

---

## 7. The Map: San Francisco (6×6)

The hand-drawn grid, north at the top and the Bay on the right. Columns run west→east, rows run
north→south. Cells in *italics* were blank in the sketch, and the editor filled them with the real
neighborhood in that spot.

| | 1 (West) | 2 | 3 | 4 | 5 | 6 (East / Bay) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Row 1** | Lands End | **Presidio** 🌉 | Marina | Wharf | Embarcadero | **Rincon** 🌉 |
| **Row 2** | Outer Richmond | *Inner Richmond* | Pac Heights | *North Beach* | *Financial District* | Ball Park |
| **Row 3** | GG Park | *Haight-Ashbury* | Fillmore | *Tenderloin* | *SoMa* | Mission Bay |
| **Row 4** | Sunset | *Twin Peaks* | Noe | *Mission* | Potrero | Dogpatch *[reading uncertain]* |
| **Row 5** | **Merced** 🛣 | *West Portal* | Glen Park | *Bernal Heights* | *Portola* *[sketch shows a crossed-out "Excelsior"]* | **Hunters Point** 🛣 |
| **Row 6** | Daly City | *Ocean View* | *Ingleside* | **Outer Mission** 🛣 | Excelsior | Visitacion Valley |

### Entry Points & Escape Routes

San Francisco has exactly **5 road entry points**. Every player must start the night at one of them. The entry cell's highway edge is always open and free, and its other outside edges are closed.

| Entry point | Edge | Cell |
| :--- | :--- | :--- |
| **Golden Gate Bridge** | North | Presidio (B1) |
| **Bay Bridge** | East | Rincon Hill (F1) |
| **US-101** | East | Hunters Point (F5) |
| **I-280** | South | Outer Mission (D6) |
| **Highway 1** | West | Merced (A5) |

Every other outside edge is an **escape route** whose cost depends on the side of the city:

| Side | Escapes | Cost |
| :--- | :--- | :--- |
| **West (Pacific)** | Essentially none. About 1 in 8 tiles has a **Speedboat** | 8–10d (₿0.8–1.0) |
| **North & East (Bay)** | More and cheaper boats: **Sailboat**, **Ferry**, **Cargo Ship** (about 45% of tiles) | 1d / 2d / 3d |
| **South (Peninsula)** | **The most exits by far.** About 80% of tiles are open | Generally free (some 1d) |

Bots aim for the entry points or the southern edge when heading home.

--- | :--- | :--- |
| **Golden Gate Bridge** | North edge | Presidio (R1C2) |
| **Bay Bridge** | East edge | Rincon (R1C6) |
| **US-101** | East edge | Hunters Point (R5C6) |
| **I-280** | South edge | Outer Mission (R6C4) |
| **CA-1 (Hwy 1)** | West edge | Merced (R5C1) |

---

## 8. Unchanged

Rules, phases, the market scarcity system, missions, influence cards, combat, the Roman-numeral die,
loans, dawn fines, and Winter Reckoning keep their Rome-edition mechanics unless a section above
changes them.
