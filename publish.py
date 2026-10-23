"""Next Human - pubblicazione automatica dei reel su Instagram.

Uso:
  python3 publish.py --check   test in sola lettura (profilo + limite di pubblicazione)
  python3 publish.py --due     pubblica i post della coda in scadenza

Il token Instagram NON e' in questo repository: lo aggiunge il proxy dell'ambiente cloud
(network secret su graph.instagram.com, header Authorization: Bearer).
I video stanno sul ramo `media` solo finche' il loro post e' in coda.
"""
import json, os, random, subprocess, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

IG_USER = "17841480036080171"  # @nnexthuman
API = "https://graph.instagram.com/v23.0"
RAW = "https://raw.githubusercontent.com/grazianomoreschi/nexthuman-media/media/"
QUEUE = "queue.json"
INCOMING = "incoming"  # video scaricati dall'artifact privato, mai nel repository
WAIT_AHEAD = timedelta(minutes=30)   # se un post scade entro 30 minuti, aspetta l'orario esatto
JITTER_S = 180  # richiesta di Graziano: pubblica in un momento a caso tra l'orario e 3 minuti dopo


def call(method, path, params=None):
    url = API + path
    data = None
    if params and method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    elif params:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:500]
        raise RuntimeError(f"HTTP {e.code} {path}: {body}")


def check():
    print("profilo:", call("GET", "/me", {"fields": "user_id,username,account_type,media_count"}))
    print("limite:", call("GET", f"/{IG_USER}/content_publishing_limit", {"fields": "quota_usage,config"}))
    print("OK: lettura riuscita, nessuna pubblicazione fatta.")


def publish_one(post):
    params = {"media_type": "REELS", "video_url": RAW + post["video"], "caption": post["caption"],
              "share_to_feed": "true"}
    if post.get("cover_ms") is not None:
        params["thumb_offset"] = str(post["cover_ms"])
    cid = call("POST", f"/{IG_USER}/media", params)["id"]
    for _ in range(60):  # fino a 10 minuti di elaborazione
        st = call("GET", f"/{cid}", {"fields": "status_code,status"})
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"elaborazione video fallita: {st}")
        time.sleep(10)
    else:
        raise RuntimeError("elaborazione video oltre 10 minuti")
    mid = call("POST", f"/{IG_USER}/media_publish", {"creation_id": cid})["id"]
    info = call("GET", f"/{mid}", {"fields": "permalink"})
    if post.get("first_comment"):
        try:
            call("POST", f"/{mid}/comments", {"message": post["first_comment"]})
        except RuntimeError as e:
            print("commento non pubblicato:", e)
    return mid, info.get("permalink", "")


def git(*args):
    subprocess.run(["git", *args], check=True)


def rebuild_media_branch(queue):
    """Il ramo media contiene solo i video dei post ancora in attesa."""
    keep = {p["video"] for p in queue if p["status"] == "pending"}
    subprocess.run(["git", "fetch", "-q", "origin", "media"], check=False)
    tmp = "/tmp/nh_media"
    subprocess.run(["rm", "-rf", tmp], check=True)
    git("worktree", "add", "-q", "--detach", tmp)
    try:
        subprocess.run(["git", "-C", tmp, "checkout", "-q", "--orphan", "media-new"], check=True)
        subprocess.run(["git", "-C", tmp, "rm", "-rqf", "--cached", "."], check=False)
        subprocess.run("find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +", shell=True, cwd=tmp, check=True)
        for v in sorted(keep):
            data = subprocess.run(["git", "show", f"origin/media:{v}"], capture_output=True).stdout
            if data:
                open(f"{tmp}/{v}", "wb").write(data)
                subprocess.run(["git", "-C", tmp, "add", v], check=True)
        subprocess.run(["git", "-C", tmp, "-c", "user.name=Next Human bot", "-c", "user.email=noreply@anthropic.com",
                        "commit", "-q", "--allow-empty", "-m", "Media in attesa di pubblicazione"], check=True)
        subprocess.run(["git", "-C", tmp, "push", "-q", "-f", "origin", "HEAD:media"], check=True)
    finally:
        git("worktree", "remove", "--force", tmp)


def other_platforms(post):
    """YouTube (privato finche' Google non verifica l'app) e TikTok (bozza nella inbox): un tentativo ciascuno."""
    want_yt = post.get("youtube") and not post.get("youtube_id") and not post.get("youtube_error")
    want_tt = post.get("tiktok") and not post.get("tiktok_status") and not post.get("tiktok_error")
    if not (want_yt or want_tt):
        return
    path = f"/tmp/nh_{post['id']}.mp4"
    local = os.path.join(INCOMING, post["video"])
    data = open(local, "rb").read() if os.path.exists(local) else \
        subprocess.run(["git", "show", f"origin/media:{post['video']}"], capture_output=True).stdout
    if not data:
        subprocess.run(["git", "fetch", "-q", "origin", "media"], check=False)
        data = subprocess.run(["git", "show", f"origin/media:{post['video']}"], capture_output=True).stdout
    open(path, "wb").write(data)
    if want_yt:
        import youtube
        try:
            yt = post["youtube"]
            post["youtube_id"] = youtube.upload(path, yt["title"], yt.get("description", post["caption"]))
            print(f"YOUTUBE {post['id']}: https://youtube.com/shorts/{post['youtube_id']} (privato)")
        except Exception as e:
            post["youtube_error"] = str(e)[:400]
            print(f"ERRORE YOUTUBE {post['id']}: {e}")
    if want_tt:
        import tiktok
        try:
            st = tiktok.upload_draft(path)
            post["tiktok_status"] = st.get("status")
            print(f"TIKTOK {post['id']}: {st.get('status')} (bozza nella inbox)")
        except Exception as e:
            post["tiktok_error"] = str(e)[:400]
            print(f"ERRORE TIKTOK {post['id']}: {e}")


def stage_media(posts):
    """Mette sul ramo media, poco prima dell'uscita, i video presenti in incoming/ (scaricati dall'artifact privato)."""
    subprocess.run(["git", "fetch", "-q", "origin", "media"], check=False)
    have = set(subprocess.run(["git", "ls-tree", "--name-only", "origin/media"], capture_output=True, text=True).stdout.split())
    new = [p["video"] for p in posts if p["video"] not in have and os.path.exists(os.path.join(INCOMING, p["video"]))]
    missing = [p["video"] for p in posts if p["video"] not in have and p["video"] not in new]
    for v in missing:
        print(f"ERRORE video mancante: {v} (non e' ne' sul ramo media ne' in {INCOMING}/)")
    if not new:
        return
    tmp = "/tmp/nh_stage"
    subprocess.run(["rm", "-rf", tmp], check=True)
    git("worktree", "add", "-q", "--detach", tmp, "origin/media")
    try:
        for v in new:
            subprocess.run(["cp", os.path.join(INCOMING, v), os.path.join(tmp, v)], check=True)
            subprocess.run(["git", "-C", tmp, "add", v], check=True)
        subprocess.run(["git", "-C", tmp, "-c", "user.name=Next Human bot", "-c", "user.email=noreply@anthropic.com",
                        "commit", "-q", "-m", "Video in uscita"], check=True)
        subprocess.run(["git", "-C", tmp, "push", "-q", "origin", "HEAD:media"], check=True)
    finally:
        git("worktree", "remove", "--force", tmp)
    subprocess.run(["git", "fetch", "-q", "origin", "media"], check=False)
    time.sleep(20)  # tempo perche' il link pubblico di GitHub si aggiorni
    print("video messi online:", ", ".join(new))


def due():
    queue = json.load(open(QUEUE))
    now = datetime.now(timezone.utc)
    todo = [p for p in queue if p["status"] == "pending"
            and datetime.fromisoformat(p["publish_at"]) <= now + WAIT_AHEAD]
    if not todo:
        print("nessun post in scadenza")
        return
    stage_media(todo)
    changed = False
    for p in sorted(todo, key=lambda p: p["publish_at"]):
        at = datetime.fromisoformat(p["publish_at"]) + timedelta(seconds=random.uniform(0, JITTER_S))
        wait = (at - datetime.now(timezone.utc)).total_seconds()
        if wait > 0:
            print(f"aspetto {int(wait)} s per {p['id']}")
            time.sleep(wait)
        try:
            mid, link = publish_one(p)
            p.update(status="published", media_id=mid, permalink=link,
                     published_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
            print(f"PUBBLICATO {p['id']}: {link}")
        except Exception as e:
            p["attempts"] = p.get("attempts", 0) + 1
            p["last_error"] = str(e)[:400]
            if p["attempts"] >= 2:
                p["status"] = "error"
            print(f"ERRORE {p['id']}: {e}")
        other_platforms(p)
        changed = True
    if changed:
        json.dump(queue, open(QUEUE, "w"), indent=1, ensure_ascii=False)
        git("add", QUEUE)
        git("-c", "user.name=Next Human bot", "-c", "user.email=noreply@anthropic.com",
            "commit", "-q", "-m", "Aggiorna coda di pubblicazione")
        git("push", "-q", "origin", "HEAD:main")
        rebuild_media_branch(queue)


if __name__ == "__main__":
    {"--check": check, "--due": due}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
