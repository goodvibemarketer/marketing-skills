---
name: substack-superfan-spotter
description: Finds the Substack readers most likely to go paid from your subscriber export (activity stars, opens, clicks, comments, shares, how long they've subscribed), then drafts the upgrade email for them, plus notes for new superfans, paying superfans and paying readers who've gone quiet. Emails are taken out on load and never shown in the chat. Use when asked to "find my superfans", "who should I ask to upgrade?", "run Superfan Spotter", "analyse my Substack subscribers", or when someone uploads a Substack subscriber export.
---

# Superfan Spotter

Your Substack dashboard tells you who reads. It doesn't tell you who to ask, or what to say. This Skill does both: it ranks your free readers by how much they behave like your paying ones, splits the list into four groups worth acting on, and drafts the message for each.

## Make it yours (edit this block once)

Fill this in once after installing. Leave a line blank and Claude asks when it matters.

```yaml
publication:        # your Substack's name
writer_name:        # how you sign off, e.g. "Andy"
paid_gets:          # what paying subscribers actually get, in plain words, e.g. "the step-by-step guide and my full Skills library"
price:              # e.g. "$10 a month or $100 a year"
founding_tier:      # optional: what the founding member tier includes and costs
offer_link:         # optional: a discount or trial link you've created in Substack
min_days:           # days subscribed before an upgrade ask (default 30)
voice_notes:        # e.g. British spelling, first person, no exclamation marks
```

Only ever mention benefits, prices and offers that are in this block or that the user gives you. Never invent a discount, a deadline or a testimonial.

## What it needs

A Substack subscriber export. Either works:

- **Subscriber CSV (best).** Dashboard → Subscribers → Export. This one includes the **activity stars**, opens, clicks and, if you add the columns before exporting, comments and shares. Tell the user: "In Subscribers, click Columns and switch on everything you can (activity, opens, clicks, comments, shares, start date), then Export."
- **Full ZIP export.** Settings → Exports → Create new export. It has the subscriber list and per-post opens, but no stars. The Skill works out reading habit from which posts each person opened over the last 90 days.

Header names change from time to time, so the script finds columns by pattern, not exact name.

## Privacy rules (non-negotiable)

- Subscriber emails are personal data. The script takes them out on load and works on anonymous IDs (`S00001`).
- **Read only `summary.json` and `report.md` into the conversation.** Never print, quote or summarise `segments/*.csv` or `_private/id_map.csv`. Those files are for the user to open.
- Never contact anyone. The Skill drafts; the user sends.
- Leave out anyone unsubscribed or with email disabled (the script does this).

## Steps

### 1. Check the columns

Run the script from this Skill's folder (it sits next to this file). It needs only Python, no extra packages.

```bash
python3 scripts/spot.py EXPORT.csv --columns
```

It prints how each column was read and what's missing. Tell the user in one or two lines. If `stars` is missing from a subscriber CSV, ask them to switch the Activity column on and export again; it's the strongest signal. If comments, shares or clicks are missing, carry on and say the ranking leans on stars and opens.

### 2. Run it

```bash
python3 scripts/spot.py EXPORT.csv --out superfan-spotter --min-days 30
```

Use `min_days` from the config. Add `--today YYYY-MM-DD` only if the export is old.

It writes:
- `summary.json` and `report.md`: counts, the star split for free and paid, the four groups and the top 25 prospects by ID. No emails.
- `segments/ready_to_upgrade.csv`, `rising.csv`, `paid_superfans.csv`, `paid_at_risk.csv`: the lists to act on, with email, name and first name, best first.
- `_private/id_map.csv`: IDs back to emails.

### 3. How the score works (explain it in a sentence if asked)

Out of 100, for every subscriber:

| Weight | Signal | Why |
| --- | --- | --- |
| 45 | Activity stars (or, with the ZIP, share of posts opened in 90 days) | The reading habit. Stars cover email opens and web views over the last month. |
| 25 | Commented, shared, clicked, read on the web | Attention beyond the open. Opens are inflated by privacy proxies; a comment is a person. |
| 15 | Opens in the last 30 days, compared with the rest of the list | Recent, not historic. |
| 10 | Days subscribed | Past the first-month honeymoon. |
| 5 | Last open within two weeks | Still here. |

The four groups:

| Group | Who | What to do |
| --- | --- | --- |
| **Ready to upgrade** | Free, 4–5 stars (or score 60+ without stars), subscribed at least `min_days` | The upgrade email. Personal notes to the top ten. |
| **Rising** | Free, 4–5 stars, newer than `min_days` | Don't sell yet. A short welcome that asks what brought them. |
| **Paid superfans** | Paying, 4–5 stars | Ask for a testimonial, a referral or what to write next. |
| **Paid at risk** | Paying, 0–1 stars and no opens in 30 days | A check-in before renewal, not a discount. |

### 4. Read the results back to the user

Short and specific, from `report.md` and `summary.json`:
- How many in each group, and how the free star split compares with the paid one (if paid readers sit at a median of 4 stars and 70 free readers are at 4–5, that's the case for the email).
- What the top prospects have in common (for example, most have commented).
- One honest caveat when it applies: a small list means small groups; opens are inflated by Apple Mail and Gmail image proxies; stars only cover the last month.
- If the report flags **link scanners** (addresses that click but never open), say their clicks were ignored: company email security tools click every link.
- If most of the list was **imported**, say that "subscribed N days" counts from the import, so tenure means less.
- The publication's own account (type "Author") is left out automatically.

Don't list emails or names. Refer to people by ID only if the user asks about a specific row.

### 5. Draft the messages

One draft per group that has members, in the user's voice (`voice_notes`). For each: two subject lines and the body, with `{first_name}` as the merge field and a fallback ("Hi there") for blank names.

Rules for every draft:
- **Personal and short.** 80–150 words. It reads like a note from the writer, not a campaign.
- **Say why them.** "You've opened nearly every issue since the spring" is fine as a group truth; never name a specific behaviour the reader didn't do. Keep it true for the whole group, and don't compare them with paying readers ("you read more than most paid subscribers") unless the numbers show it for everyone in the group.
- **One ask.** Upgrade, reply, review or check in. Not two.
- **Only real benefits** from `paid_gets`, `price`, `founding_tier` and `offer_link`. No fake scarcity, no invented numbers or quotes.
- **Easy to say no.** End without pressure ("If it's not for you, no problem, the free posts aren't going anywhere").

Group by group:
- **Ready to upgrade:** thank them for reading, say what paying gets them in one or two concrete lines, give the price and link (or `offer_link`). Add a separate three-line version for the top ten as personal notes.
- **Rising:** welcome, ask one question about what they want to read. No upgrade ask.
- **Paid superfans:** thank them, ask for one sentence you can quote (with permission) or for a referral.
- **Paid at risk:** a check-in. Ask what would make it worth it again. No discount unless the user asks.

Save the drafts as `superfan-spotter/drafts.md`.

### 6. How to send (tell the user)

Substack sends posts to all free or all paid readers, not to a custom list. So the drafts go out:
- **Personally**, from the user's own inbox, for the top ten and for paid groups (usually small). This gets the best response.
- **By mail merge** (for example Gmail with a mail-merge add-on, or their CRM) for a larger "ready to upgrade" group, using the segment CSV. Send in small batches and only to people on the list.

### 7. Run it again next month

Stars change monthly. Suggest a rerun in four to six weeks, and compare: who upgraded, who moved into "ready", who slipped.

## Output checklist

- [ ] Column check reported, gaps named
- [ ] `summary.json`, `report.md`, the four segment CSVs and `drafts.md` in `superfan-spotter/`
- [ ] No email address or name appeared in the conversation
- [ ] Every draft uses only real benefits, prices and offers
- [ ] The user knows how to send and when to rerun
