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
paid_promise:       # the outcome of paying, in one line: before and after, e.g. "go from prompting Claude to running your marketing with it"
paid_gets:          # 2-3 concrete things paying subscribers get, e.g. "the step-by-step guide; my full Skills library, updated monthly"
free_gets:          # what free readers keep getting, e.g. "the weekly AI news and one free Skill a month"
paid_example:       # optional: link to one paid post that shows the paid tier at its best
proof:              # optional: real quotes from paying readers (with permission) or a concrete fact about the work
price:              # e.g. "$10 a month, or $100 a year (two months free)"
upgrade_link:       # your subscribe or upgrade page link
offer:              # optional: "20% off the first year until 5 Dec" or "14-day free trial", exactly as set up in Substack
offer_link:         # the private link for that offer
expensable:         # yes if your readers are professionals who might expense it as training
founding_tier:      # optional: what the founding member tier includes and costs
min_days:           # days subscribed before an upgrade ask (default 30)
voice_notes:        # e.g. British spelling, first person, no exclamation marks
```

Only ever mention benefits, prices, proof and offers that are in this block or that the user gives you. Never invent a discount, a deadline or a testimonial. If `paid_promise` or `paid_gets` is blank, ask for them before drafting: they decide whether the email works.

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
python3 scripts/spot.py EXPORT.csv --out superfan-spotter --min-days 30 [--names OLD_LIST.csv]
```

Use `min_days` from the config. Add `--today YYYY-MM-DD` only if the export is old.

It writes:
- `summary.json` and `report.md`: counts, the star split for free and paid, the four groups and the top 25 prospects by ID. No emails.
- `segments/ready_to_upgrade.csv`, `rising.csv`, `paid_superfans.csv`, `paid_at_risk.csv`: the lists to act on, with email, name and first name, best first.
- `_private/id_map.csv`: IDs back to emails.

### 2b. First names (do this for every run)

A superfan shouldn't get "Hi there". Substack's own name field is often empty, especially for imported lists, so the script fills `first_name` in each segment CSV from, in order:

1. **Substack's name field**, unless it looks like a username (`andymills`).
2. **The user's own files**, if they pass them with `--names`: an export from a previous email tool (Mailchimp, beehiiv, ConvertKit), a CRM export, or a sheet of LinkedIn newsletter subscribers with profile links (`/in/jane-smith-…` gives "Jane"). Any CSV with an email column and a name, first name or profile column works. Repeat `--names` for several files.
3. **The email address**: `jane.smith@` gives "Jane" (high), `tom@` gives "Tom" (medium), `janesmith@` gives "Jane" (check). It uses a bundled public-domain list of common first names (`references/first-names.txt`), so names from outside English-speaking countries are often missed. Role addresses (`info@`, `hello@`) are skipped.

Each row gets a `name_source` and, for medium and check guesses, `check_name = yes`. Tell the user how many names came from each source (the report's "First names" section) and ask them to review the `check_name` rows before sending.

**When most of a group has no Substack name, ask:** "Do you have an export from your old email tool, a CRM or a LinkedIn subscriber list? Names from it would fill in N of the gaps." Then rerun with `--names`.

Never look subscribers up anywhere else: no enrichment services, no web searches, no LinkedIn lookups by email. Their own data and the address itself only.

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

The drafts are where this Skill earns its keep, so read `references/upgrade-email-playbook.md` before writing. It has the evidence and sources behind every rule below.

**The rules for every message**
- **Plain text.** No images, no banners, one link (or one Substack button). Plain-text emails got more clicks than designed ones in HubSpot's tests.
- **Short.** Emails 120–180 words, personal notes under 80.
- **Open with a true observation about the group, not about you.** "You've opened most of what I've sent this month" works because every reader in the group did it. Never claim something only some of them did, and don't compare them with paying readers unless the numbers show it for everyone in the group.
- **Sell the outcome, then show it.** Lead with `paid_promise` (before and after), then two or three concrete items from `paid_gets`, then `paid_example` if there is one. Say in one line what stays free (`free_gets`), so nobody feels the free tier is being taken away.
- **Proof only if it's real.** Use `proof` if given. Otherwise a concrete fact about the work. Never a made-up quote.
- **One price, one link.** The price from `price`, the annual saving in one clause if there is one, then `upgrade_link` (or `offer_link` when there's an offer).
- **`expensable: yes`** adds one line: "If your company has a training budget, you may be able to expense it." A possibility, never a promise.
- **An easy no.** "If it's not for you, no problem. The free posts aren't going anywhere."
- **End with a question** in a P.S. ("What's the one thing you'd want me to cover next?"). Replies are a warmer signal than clicks, and every reply is a conversation.
- **Subject lines:** 36–50 characters, specific, honest. Name what they did or what they'd get. No clickbait, no fake "Re:", no names (Substack can't put names in subject lines).
- **First names:** Substack's `%%first_name%%` only uses Substack's own name field, so the names filled in from files or email addresses only reach readers by mail merge or personal email. In a mail merge, greet with `Hi {first_name},` and set the fallback to the writer's choice for the few still blank. In a Substack send, write `Hi %%first_name%%` with no comma straight after it.

**Ready to upgrade: a three-email sequence, a week apart**

| Email | Job | Ask |
| --- | --- | --- |
| 1. Thank-you | Recognise their reading, state `paid_promise`, list what they'd get, price, link | Soft: "if you want to go further" |
| 2. Show it | One concrete thing from the paid tier: a paid post they'd have read, a Skill, a result. Quote a short real excerpt or describe it in two lines | Soft: link to `paid_example` or the upgrade page |
| 3. Decide | Only if there's an `offer` with a real end date: the offer, the date, one line on what they get | Clear: "the offer ends on [date]" |

**Seasonal moments.** If Black Friday and Cyber Monday, New Year or the publication's anniversary is close, suggest timing the sequence to it: Substack names holidays and milestones as good moments for an offer. For Black Friday: thank-you early that week, the offer on the Friday, "last day" on Cyber Monday. Only if the user sets up a real offer that ends then.

With no offer, email 3 becomes a short "last note from me on this" with the same easy no. Never invent an offer or a deadline. Remove anyone who upgraded before each send.

**Top ten: personal notes.** Three or four sentences, written to be sent one by one from the writer's own inbox. Leave a `[one specific thing about them]` slot for the writer to fill by hand (a comment they left, a post they shared, their job). Don't fill it in yourself.

**Rising:** one welcome email. Recognise that they've read most of what they've received, ask what brought them and what they want next. No upgrade ask.

**Paid superfans:** a thank-you, plus one ask: a sentence you can quote with permission, or a referral.

**Paid at risk:** a check-in before renewal. Ask what would make it worth it again. No discount unless the user asks.

Save everything as `superfan-spotter/drafts.md`, with a send date for each sequence email.

### 6. How to send (tell the user)

- **Choose by names.** If more than about a fifth of the group has a first name only from a file or the email address (see the report), send the sequence by **mail merge** with the segment CSV, so every superfan is greeted by name. Otherwise send from Substack.
- **Mail merge:** from the writer's own email (for example Gmail's mail merge, where the Google Workspace plan includes it, or a mail-merge add-on), small batches, plain text. These emails sit outside Substack's unsubscribe link, so end each one with "If you'd rather not get these, just reply and say so", and honour it.
- **From Substack.** Subscribers → Segments → start from scratch, then filter: free subscribers, activity 4–5 stars, signed up before the cut-off date in `summary.json` (`segment_filter`). Save it, select everyone and click *Send email*. It goes as a direct email and doesn't appear on the publication. Rebuild or refresh the segment before emails 2 and 3, so anyone who upgraded drops out.
- **From their own inbox** for the top-ten personal notes, one at a time.
- **Mail merge** with the segment CSV only if they'd rather not use Substack's segments.
- **What to expect:** Substack's own benchmark is 3–10% of the whole free list converting over time. The superfan group should beat that, but don't promise a number. Rerun the Skill in a month and count who upgraded.

### 7. Run it again next month

Stars change monthly. Suggest a rerun in four to six weeks, and compare: who upgraded, who moved into "ready", who slipped.

## Output checklist

- [ ] Column check reported, gaps named
- [ ] `summary.json`, `report.md`, the four segment CSVs and `drafts.md` in `superfan-spotter/`
- [ ] No email address or name appeared in the conversation
- [ ] First-name sources reported; `check_name` rows flagged for review; asked for an old list if many are blank
- [ ] Every draft uses only real benefits, prices, proof and offers, in plain text with one link
- [ ] Ready to upgrade has the three-email sequence with send dates; top ten have personal notes with a slot to fill by hand
- [ ] The user knows how to send and when to rerun
