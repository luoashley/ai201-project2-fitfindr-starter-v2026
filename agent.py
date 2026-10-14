"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from mcp_client import MCPError, call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "suggest_outfit_item_id": None,  # item id read back from session for suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    parsed = {
        "description": query.strip(),
        "size": None,
        "max_price": None,
    }

    price_match = re.search(r"(?:under|below|less than|max|up to)\s*\$?(\d+(?:\.\d+)?)", query, re.I)
    if price_match:
        parsed["max_price"] = float(price_match.group(1))

    size_match = re.search(
        r"(?:size|sz)\s+((?:us\s*)?\d+(?:\.\d+)?|xxs|xs|s|m|l|xl|xxl|one size|w\d+(?:\s*l\d+)?)",
        query,
        re.I,
    )
    if size_match:
        parsed["size"] = re.sub(r"\s+", " ", size_match.group(1).strip()).upper()
        if parsed["size"].startswith("US"):
            parsed["size"] = parsed["size"].replace("US", "US ", 1)

    description = query
    spans = []
    if price_match:
        spans.append(price_match.span())
    if size_match:
        spans.append(size_match.span())
    for start, end in sorted(spans, reverse=True):
        description = description[:start] + description[end:]
    description = re.sub(r"\b(in|for|looking for|find me|show me)\b", " ", description, flags=re.I)
    description = re.sub(r"[$,]", " ", description)
    description = re.sub(r"\s+", " ", description).strip()
    parsed["description"] = description or query.strip()
    return parsed

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    count = 1
    trace.check_iterations(count)
    session = new_session(query, wardrobe)

    try:
        session["parsed"] = _parse_query(query)
        trace.step("parse_query", inputs={"query": query}, returned=session["parsed"])

        count += 1
        trace.check_iterations(count)
        search_inputs = {
            "description": session["parsed"]["description"],
            "size": session["parsed"]["size"],
            "max_price": session["parsed"]["max_price"],
        }
        session["search_results"] = call_tool(
            "search_listings",
            search_inputs,
        )
        trace.step("search_listings (via MCP)", inputs=search_inputs, returned=session["search_results"])

        if not session["search_results"]:
            session["error"] = (
                "I couldn't find a matching listing. Try changing the item words, "
                "removing the size, or raising the price ceiling."
            )
            trace.step("branch", returned=session["error"], note="empty search, stopping")
            return session

        session["selected_item"] = session["search_results"][0]
        trace.step("select_item", returned=session["selected_item"])

        count += 1
        trace.check_iterations(count)
        session["suggest_outfit_item_id"] = session["selected_item"].get("id")
        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"],
            session["wardrobe"],
        )
        trace.step(
            "suggest_outfit",
            inputs={
                "new_item_id": session["suggest_outfit_item_id"],
                "wardrobe_items": len(session["wardrobe"].get("items", [])),
            },
            returned=session["outfit_suggestion"],
        )

        count += 1
        trace.check_iterations(count)
        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"],
            session["selected_item"],
        )
        trace.step(
            "create_fit_card",
            inputs={
                "new_item_id": session["selected_item"].get("id"),
                "outfit_chars": len(session["outfit_suggestion"] or ""),
            },
            returned=session["fit_card"],
        )
    except MCPError as exc:
        session["error"] = (
            "The listing search tool could not be reached through MCP. "
            f"{exc}"
        )
        trace.step("error", returned=session["error"], note="MCP failure")
    except ModelUnavailable as exc:
        session["error"] = (
            f"{exc} Try checking GEMINI_API_KEY in .env, then rerun with a new query "
            "so the model call is not served from cache."
        )
        trace.step("error", returned=session["error"], note="model unavailable")

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
