# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr takes a plain-language request for a thrifted clothing item, searches the local listings data, and picks the best matching result. If it finds an item, it asks the model for an outfit suggestion using the user's saved wardrobe, then turns that into a short fit card caption. If no listing matches, the agent stops early and tells the user what to change instead of trying to style nothing.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listing dataset for items that match a keyword description, optional size, and optional maximum price.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None).
- **Returns:** A list of listing dicts, best match first, each containing `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** Returns an empty list `[]`.

### `suggest_outfit`

- **What it does:** Suggests one or two ways to style the selected thrift item with the user's wardrobe.
- **Inputs:** `new_item` (dict listing), `wardrobe` (dict with an `items` list).
- **Returns:** A non-empty string with outfit suggestions that name usable wardrobe pieces when the wardrobe has items.
- **When it has nothing:** If the wardrobe is empty, returns general styling advice using common closet staples instead of failing.

### `create_fit_card`

- **What it does:** Turns the outfit suggestion and selected listing into a short social-style caption.
- **Inputs:** `outfit` (str), `new_item` (dict listing).
- **Returns:** A two-to-four sentence string mentioning the item, price, platform, and vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a message saying an outfit suggestion is needed first.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a helpful message in `session["error"]` and stop. Otherwise, store the first result in `session["selected_item"]`, call `suggest_outfit`, then call `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex. The parser looks for price phrases like `under $30` and size phrases like `size M`, then cleans those phrases out to leave the item description.

**What moves through the session:** The query is stored first, then parsed into `description`, `size`, and `max_price`. Search results go into `session["search_results"]`, the first result goes into `session["selected_item"]`, the model outfit goes into `session["outfit_suggestion"]`, and the final caption goes into `session["fit_card"]`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ .venv/bin/python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear**
Pair the baby tee with your **baggy dark-wash jeans** to balance the fitted top with loose bottoms. Finish with **chunky white sneakers** and your **black crossbody bag**.

**Outfit 2: Edge & Sweet**
Layer the baby tee under your **vintage black denim jacket** paired with the **baggy dark-wash jeans** and **black combat boots** for a tougher Y2K look.

  Fit card: Unapologetic Y2K energy right here. This graphic butterfly baby tee is giving all the nostalgic feels for just $18. Pair it with baggy dark-wash jeans and chunky white sneakers, or toughen it up with a vintage black denim jacket and combat boots. Grab it now exclusively on Depop before it's gone.

2 model calls this session, 582 prompt + 168 output tokens

```

**The three tools, tested one at a time**

```
$ .venv/bin/python -c 'from tools import search_listings; print([(x["title"], x["price"]) for x in search_listings("graphic tee", max_price=30)[:3]])'
[('Y2K Baby Tee — Butterfly Print', 18.0), ('Vintage Band Tee — Faded Grey', 19.0), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0)]

```

```
$ .venv/bin/python -c 'from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[1], get_example_wardrobe()))'
**Outfit 1: Y2K Streetwear**
Pair the baby tee with your **baggy dark-wash jeans** to balance the fitted top with loose bottoms. Finish with **chunky white sneakers** and your **black crossbody bag**.

**Outfit 2: Edge & Sweet**
Layer the baby tee under your **vintage black denim jacket** paired with the **baggy dark-wash jeans** and **black combat boots** for a tougher Y2K look.

```

```
$ .venv/bin/python -c 'from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card("Pair with baggy jeans and chunky white sneakers.", load_listings()[1]))'
Channeling major early 2000s energy with this butterfly print Y2K baby tee. Grab it on Depop for just $18 before someone else does. Throw it on with your favorite baggy jeans and chunky white sneakers for the easiest weekend fit.

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Codex to implement the three starter tools while following the assignment spec.
- *What came back:* The first implementation used deterministic keyword scoring for search and model prompts for the outfit and fit card tools.
- *What I changed:* I checked the listing data and made the size filter token-based so `S` would not accidentally match shoe sizes like `US 9`.

**Moment 2**

- *What I asked for:* I asked Codex to test the parser and search commands from the terminal.
- *What came back:* The first quick parser test lost `$30` because it was inside a double-quoted shell command.
- *What I changed:* I reran the test with safe quoting and kept the README sample commands in single quotes so the price ceiling is preserved.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item id is the id passed to `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions item, price, and platform | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Price ceiling is respected by search results | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

Full evidence file: `results/run_2026-10-13_2119_before.md`, produced by `run_eval.py::main`.

Criterion 1, matching query completed all three tools:

$ .venv/bin/python run_eval.py --label before

matching query completes
- Query: `vintage graphic tee under $30`
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Fit card:
```
The ultimate Y2K butterfly baby tee just landed on my Depop for $18. Pair it with baggy dark-wash denim and a black jacket for that effortless street edge, or dress it down with wide-leg trousers. Pure 2000s energy, ready for your rotation.
```

Criterion 2, empty search stopped early:

```
stopped early: yes — I couldn't find a matching listing. Try changing the item words, removing the size, or raising the price ceiling.
selected_item: (none)
search_results: 0
```

Criterion 3, selected item id matched the id passed into `suggest_outfit`:

```
selected_item: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
selected_item_id: lst_004
suggest_outfit_item_id: lst_004
```

Criterion 4, fit card included item/price/platform:

```
Major 90s energy incoming. These chunky platform sneakers add the exact right amount of height and attitude, and they're yours for $48 on Poshmark. Style them with a cropped zip hoodie and baggy denim for peak Y2K streetwear, or keep it clean with wide-leg khakis and a layered grey crewneck.
```

Criterion 5, price ceiling respected:

```
query: graphic tee under $20
search_results: 3
out: 3 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Mesh Long-Sleeve Top — Black
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET | All five tries selected an item, produced an outfit suggestion, and returned a non-empty fit card. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET | All five tries stopped with `search_results: 0`, `selected_item: (none)`, and no fit card. |
| 3 | State carries the selected item into `suggest_outfit` | 5 of 5 | MET | All five tries had the same `selected_item_id` and `suggest_outfit_item_id`; for the track jacket scenario both were `lst_004`. |
| 4 | Fit card mentions item, price, and platform | 4 of 5 | MET | All five fit cards named the item or a clear shortened version, included `$48`, and named Poshmark. |
| 5 | Price ceiling is respected | 5 of 5 | MET | All five `graphic tee under $20` tries returned only listings priced at or below $20. |

**Diagnoses**

No criterion missed. The targets were not empty, but criterion 4 was looser than I would write it now: "the item or a clear shortened version" passed cards that said "chunky platform sneakers" instead of the exact listing title `Platform Sneakers — White Chunky Sole`. That is acceptable under the original criterion, but it is less auditable than exact title matching.

Failure modes triggered on purpose:

- Empty search: `designer ballgown size XXS under $5` stopped before `suggest_outfit` and told the user to change item words, remove size, or raise the price ceiling.
- Empty wardrobe: `.venv/bin/python app.py ask 'denim jacket under $50' --empty-wardrobe` returned general styling advice with common pieces instead of crashing.
- Model unavailable: `GEMINI_API_KEY=bad-key AI201_CACHE=0 .venv/bin/python app.py ask 'emerald velvet blazer under $60'` returned `The model rejected your API key... Try checking GEMINI_API_KEY in .env, then rerun with a new query so the model call is not served from cache.`


---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item_id, wardrobe_items
      out: **Outfit 1: Y2K Streetwear** *   **Top:** Y2K Butterfly Baby Tee *   **Bottoms:** Baggy dark-wash straight-leg…
[5] create_fit_card
      in:  dict with keys: new_item_id, outfit_chars
      out: The ultimate Y2K butterfly baby tee just landed on my Depop for $18. Pair it with baggy dark-wash denim and a …

```

**Empty search**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      out: I couldn't find a matching listing. Try changing the item words, removing the size, or raising the price ceili…
      →    empty search, stopping

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

I moved `search_listings` behind MCP. `mcp_server.py` now registers the tool with typed inputs `description` (`str`), `size` (`str | None`), and `max_price` (`float | None`). `agent.py::run_agent` calls it with `mcp_client.call_tool("search_listings", ...)` instead of importing and calling it directly. The return shape stayed the same: a list of listing dicts, or `[]` for no match.

`python mcp_client.py` lists:

```
search_listings
  Search thrift listings by a text description, optional size string, and
  optional maximum price in dollars. Returns matching listing dictionaries
  ordered best-first; returns an empty list when nothing matches.
```


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**
I tightened the `create_fit_card` prompt in `tools.py` so it asks the model to use the exact item title once, exact price once, and exact platform once.

**Which failure it was meant to fix:**
It was meant to make criterion 4 easier to score. Before the change, criterion 4 passed, but some cards used shortened phrases like "chunky platform sneakers" rather than the exact title. That was acceptable under the original criterion, but less precise than I wanted.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item id is the id passed to `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions item, price, and platform | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Price ceiling is respected by search results | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**
Full evidence file: `results/run_2026-10-13_2122_after.md`, produced by `run_eval.py::main`.

It helped partly. The original criterion 4 was already met before and after, so the pass count stayed 5/5. The stricter behavior improved: before, the platform-sneaker fit cards usually used shortened item wording; after the prompt change, 3 of 5 used the exact full title `Platform Sneakers — White Chunky Sole`, and all 5 still included the price and platform.

After example:

```
The ultimate Y2K staple just landed. Pair these Platform Sneakers — White Chunky Sole with baggy denim and a zip hoodie for that off-duty look, or dress them down with khaki trousers. Grab this fresh find on Poshmark for $48.0 before someone else does.
```

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

Nothing in the five original criteria is still missed. The remaining weakness is measurement: criterion 4 allows "clear shortened version," which makes the grader read subjectively. If I kept going, I would revise that criterion in the next unit to require the exact listing title, exact price, and platform in 5 of 5 fit cards, or add a scorer that checks those strings directly.

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
