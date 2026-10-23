# Diagnose one reel (ordered)

Adapted from vyralcontent/content-skills `viral-instagram-reels/references/diagnose-flop.md` (MIT) to the
metrics `stats.py` collects. Walk the steps in order and stop at the first lever that explains the result:
fixing a later lever while an earlier one is broken changes nothing.

Numbers per reel in `stats/reels.json`: views, reach, likes, comments, shares, saves, interactions,
skip_rate_pct (share of viewers who left in the first ~3 s), avg_watch_s, watch_pct (avg watch / duration),
total_watch_min, views_per_h, age_h, like/share/save/comment rate per reach, plus the episode attributes from
`growth/catalog.json` (duration_s, hook, topic, pillar, first_timer_at_s, tags).

Baseline = median of the last 10 Instagram reels (say how many there are when fewer).

## 0. Reach ceiling (account level)
If several recent reels have reach far below the account's usual and no hook problem explains it, suspect an
originality or quality cap (reposted look, third-party watermarks). Our reels are original renders: check that
nothing on screen looks like another app's UI. If this is the cause, no single-reel fix helps.

## 1. Hook: the 3-second cliff
- skip_rate_pct above baseline (or above ~40% while the account is new): the hook failed. Most common cause.
- Look at the episode hook and first frame: was there an intro/subtitle before the timer
  (`first_timer_at_s` > 0)? Was the first line about "you" or a vague "this is X"? Was the number on screen at
  frame 1? Was the scene moving?
- Fix for the next reels: recut the opening, not the rest.

## 2. Body: mid-reel bleed
- Skip normal but watch_pct low (below baseline): viewers left in the middle.
- Check pacing (a change every 2-3 s), the re-hook before the middle, whether the payoff arrived too late
  (timer twist after 25-30 s), and length versus the average watch seconds.

## 3. Topic legibility: views without follows or saves
- Reach and watch fine, near-zero follows/saves: the topic was not clear to a stranger. Check on-screen
  keywords, the caption first line, and whether the bio promises this topic.

## 4. Send signal
- Watch fine, share rate below baseline: no one specific person needed it. Check the payoff (useful to a
  recognisable person?) and the CTA (named-persona send prompt or a generic "comment"?).

## 5. Audio
- Our audio is original chiptune; a reel playing silent would show as a very high skip. Spot-check on a phone
  when skip jumps with no hook change.

## 6. Caption and search
- Low reach across the board with a fine hook: caption first line must carry the topic keyword; 150-300
  characters; 3-5 hashtags.

## Verdict format (one line per reel)
`ep10 Ozempic: hook failed, skip 51% vs baseline 44%; first frame was a subtitle intro; next: open on the
chart with "-15%" already drawn.`
Then one concrete next action. Never call a reel a winner or a flop on a single day if it is still growing
(views_per_h rising).
