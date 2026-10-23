"""Next Human - statistiche giornaliere (Instagram + YouTube).

Uso:
  python3 stats.py   legge le statistiche e scrive stats/reels.json, stats/daily.json e stats/history.json

Instagram: token aggiunto dal proxy (come publish.py). YouTube: variabili YT_* (come youtube.py).
TikTok: l'app non ha ancora i permessi per leggere le statistiche (servono user.info.stats e video.list).
"""
import json, os, re
from datetime import datetime, timezone, timedelta
import publish as IG

OUT = "stats"
METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions", "ig_reels_avg_watch_time",
           "ig_reels_video_view_total_time"]
CATALOG = "growth/catalog.json"  # attributi di ogni episodio (durata, hook, tema, formato, tag degli esperimenti)


def rome_now():
    now = datetime.now(timezone.utc)
    off = 2 if now < datetime(2026, 10, 25, 1, tzinfo=timezone.utc) else 1
    return now.astimezone(timezone(timedelta(hours=off)))


def to_rome(iso):
    t = datetime.fromisoformat(iso.replace("+0000", "+00:00").replace("Z", "+00:00"))
    off = 2 if t < datetime(2026, 10, 25, 1, tzinfo=timezone.utc) else 1
    return t.astimezone(timezone(timedelta(hours=off))).strftime("%Y-%m-%d %H:%M")


def ig_reels():
    rows = []
    media = IG.call("GET", f"/{IG.IG_USER}/media", {"fields": "id,caption,timestamp,media_product_type,permalink", "limit": 50})
    for m in media.get("data", []):
        row = {"platform": "Instagram", "id": m["id"], "posted": to_rome(m["timestamp"]),
               "title": (m.get("caption") or "").split("\n")[0][:80], "link": m.get("permalink", "")}
        try:
            ins = IG.call("GET", f"/{m['id']}/insights", {"metric": ",".join(METRICS)})
            vals = {d["name"]: d["values"][0]["value"] for d in ins.get("data", [])}
        except RuntimeError:
            vals = {}
        row.update(views=vals.get("views"), reach=vals.get("reach"), likes=vals.get("likes"),
                   comments=vals.get("comments"), shares=vals.get("shares"), saves=vals.get("saved"),
                   interactions=vals.get("total_interactions"),
                   avg_watch_s=round(vals["ig_reels_avg_watch_time"] / 1000, 1) if vals.get("ig_reels_avg_watch_time") else None,
                   total_watch_min=round(vals["ig_reels_video_view_total_time"] / 60000, 1) if vals.get("ig_reels_video_view_total_time") else None)
        row["caption"] = m.get("caption") or ""
        rows.append(row)
    return rows


def ig_comments(media_ids):
    """Testo dei commenti (senza nomi utente) per capire cosa colpisce il pubblico."""
    out = []
    for mid in media_ids:
        try:
            r = IG.call("GET", f"/{mid}/comments", {"fields": "text,timestamp,like_count", "limit": 50})
        except RuntimeError:
            continue
        for c in r.get("data", []):
            out.append({"media_id": mid, "at": to_rome(c["timestamp"]), "text": c.get("text", "")[:500], "likes": c.get("like_count", 0)})
    return out


def enrich(rows, now):
    """Aggiunge attributi dell'episodio e i tassi che contano per l'algoritmo."""
    cat = json.load(open(CATALOG)) if os.path.exists(CATALOG) else []
    for r in rows:
        ep = next((c for c in cat if re.search(c["caption_match"], r.get("caption") or r.get("title") or "", re.I)), None)
        r["episode"] = ep["episode"] if ep else None
        for k in ("pillar", "topic", "duration_s", "format", "tags", "hook", "first_timer_at_s"):
            r[k] = ep.get(k) if ep else None
        n = lambda x: x or 0
        reach = r.get("reach") or r.get("views") or 0
        rate = lambda x: round(100 * n(x) / reach, 2) if reach else None
        r["like_rate_pct"], r["share_rate_pct"], r["save_rate_pct"], r["comment_rate_pct"] = (
            rate(r.get("likes")), rate(r.get("shares")), rate(r.get("saves")), rate(r.get("comments")))
        if r.get("avg_watch_s") and r.get("duration_s"):
            r["watch_pct"] = round(100 * r["avg_watch_s"] / r["duration_s"], 1)
        try:
            posted = datetime.strptime(r["posted"], "%Y-%m-%d %H:%M").replace(tzinfo=now.tzinfo)
            r["post_hour"] = posted.hour
            r["age_h"] = round((now - posted).total_seconds() / 3600, 1)
            r["views_per_h"] = round(n(r.get("views")) / max(r["age_h"], 0.5), 1)
        except (KeyError, ValueError):
            pass
        r.pop("caption", None)
    return rows


def ig_account():
    me = IG.call("GET", "/me", {"fields": "followers_count,media_count"})
    acc = {"followers": me.get("followers_count"), "posts": me.get("media_count")}
    for met, key in (("reach", "reach_day"), ("views", "views_day"), ("profile_views", "profile_views_day"),
                     ("accounts_engaged", "engaged_day"), ("total_interactions", "interactions_day"),
                     ("shares", "shares_day"), ("saves", "saves_day"), ("website_clicks", "link_clicks_day")):
        try:
            r = IG.call("GET", f"/{IG.IG_USER}/insights", {"metric": met, "period": "day", "metric_type": "total_value"})
            acc[key] = r["data"][0]["total_value"]["value"]
        except (RuntimeError, KeyError, IndexError):
            acc[key] = None
    return acc


def yt_videos():
    if not os.environ.get("YT_REFRESH_TOKEN"):
        return [], {}
    import youtube as YT
    tok = YT.access_token(); h = {"Authorization": "Bearer " + tok}
    _, ch = YT.request("GET", YT.API + "/channels?part=statistics,contentDetails&mine=true", headers=h)
    item = ch["items"][0]
    chan = {"yt_subscribers": int(item["statistics"].get("subscriberCount", 0)), "yt_views": int(item["statistics"].get("viewCount", 0))}
    uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
    _, pl = YT.request("GET", YT.API + f"/playlistItems?part=contentDetails&maxResults=50&playlistId={uploads}", headers=h)
    ids = [x["contentDetails"]["videoId"] for x in pl.get("items", [])]
    rows = []
    if ids:
        _, vs = YT.request("GET", YT.API + "/videos?part=snippet,statistics,status&id=" + ",".join(ids), headers=h)
        for v in vs.get("items", []):
            s = v["statistics"]
            rows.append({"platform": "YouTube", "id": v["id"], "posted": to_rome(v["snippet"]["publishedAt"]),
                         "title": v["snippet"]["title"][:80], "link": "https://youtube.com/shorts/" + v["id"],
                         "status": v["status"]["privacyStatus"], "views": int(s.get("viewCount", 0)),
                         "likes": int(s.get("likeCount", 0)), "comments": int(s.get("commentCount", 0))})
    return rows, chan


def main():
    os.makedirs(OUT, exist_ok=True)
    now = rome_now(); day = now.strftime("%Y-%m-%d")
    reels = ig_reels()
    comments = ig_comments([r["id"] for r in reels])
    acc = ig_account()
    yt, chan = yt_videos()
    reels = enrich(reels, now); yt = enrich(yt, now)
    json.dump(reels + yt, open(f"{OUT}/reels.json", "w"), indent=1, ensure_ascii=False)
    json.dump(comments, open(f"{OUT}/comments.json", "w"), indent=1, ensure_ascii=False)
    with open(f"{OUT}/snapshots.jsonl", "a") as f:  # una riga per reel a ogni lettura: serve per la velocita'
        for r in reels + yt:
            f.write(json.dumps({"at": now.strftime("%Y-%m-%d %H:%M"), **{k: r.get(k) for k in (
                "platform", "id", "episode", "views", "reach", "likes", "comments", "shares", "saves", "avg_watch_s")}}) + "\n")
    hist_path = f"{OUT}/history.json"
    hist = json.load(open(hist_path)) if os.path.exists(hist_path) else []
    snap = {"date": day, **acc, **chan,
            "ig_views_total": sum(r["views"] or 0 for r in reels), "ig_reels": len(reels),
            "ig_likes_total": sum(r["likes"] or 0 for r in reels), "ig_shares_total": sum(r["shares"] or 0 for r in reels),
            "ig_saves_total": sum(r["saves"] or 0 for r in reels), "ig_comments_total": sum(r["comments"] or 0 for r in reels)}
    hist = [h for h in hist if h["date"] != day] + [snap]
    json.dump(hist, open(hist_path, "w"), indent=1, ensure_ascii=False)
    json.dump(hist, open(f"{OUT}/daily.json", "w"), indent=1, ensure_ascii=False)
    print(f"STATISTICHE {day} {now.strftime('%H:%M')}")
    print("account:", json.dumps(snap, ensure_ascii=False))
    for r in sorted(reels, key=lambda r: r["posted"], reverse=True):
        print(f"IG {r['posted']} {r['episode']} views={r['views']} reach={r['reach']} likes={r['likes']} comm={r['comments']} "
              f"shares={r['shares']} saves={r['saves']} watch={r['avg_watch_s']}s ({r.get('watch_pct')}% di {r.get('duration_s')}s) "
              f"views/h={r.get('views_per_h')} | {r['title']}")
    print(f"commenti: {len(comments)}")
    for r in yt:
        print(f"YT {r['posted']} {r['status']} views={r['views']} likes={r['likes']} comm={r['comments']} | {r['title']}")


if __name__ == "__main__":
    main()
