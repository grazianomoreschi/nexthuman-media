"""Next Human - caricamento dei video su TikTok (Content Posting API).

Uso:
  python3 tiktok.py --check   test in sola lettura (account collegato + impostazioni di pubblicazione)
  python3 tiktok.py --test    manda un video di prova di 5 secondi come BOZZA nella inbox TikTok

Le chiavi NON sono in questo repository: sono variabili dell'ambiente cloud
(TT_CLIENT_KEY, TT_CLIENT_SECRET, TT_REFRESH_TOKEN). Non vanno mai stampate.
Finche' TikTok non approva l'app, i post diretti possono essere solo privati (SELF_ONLY).
"""
import json, os, subprocess, sys, tempfile, time, urllib.parse, urllib.request

API = "https://open.tiktokapis.com/v2"


def request(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:500]
        raise RuntimeError(f"HTTP {e.code} {urllib.parse.urlparse(url).path}: {body}")


def access_token():
    missing = [v for v in ("TT_CLIENT_KEY", "TT_CLIENT_SECRET", "TT_REFRESH_TOKEN") if not os.environ.get(v)]
    if missing:
        raise RuntimeError("variabili mancanti nell'ambiente: " + ", ".join(missing))
    data = urllib.parse.urlencode({"client_key": os.environ["TT_CLIENT_KEY"],
                                   "client_secret": os.environ["TT_CLIENT_SECRET"],
                                   "refresh_token": os.environ["TT_REFRESH_TOKEN"],
                                   "grant_type": "refresh_token"}).encode()
    r = request("POST", API + "/oauth/token/", data, {"Content-Type": "application/x-www-form-urlencoded"})
    if "access_token" not in r:
        raise RuntimeError(f"rinnovo accesso fallito: {r.get('error')} {r.get('error_description')}")
    return r["access_token"]


def call(tok, path, body=None):
    headers = {"Authorization": "Bearer " + tok}
    if body is None:
        return request("GET", API + path, headers=headers)
    headers["Content-Type"] = "application/json; charset=UTF-8"
    return request("POST", API + path, json.dumps(body).encode(), headers)


def check():
    tok = access_token()
    user = call(tok, "/user/info/?fields=open_id,display_name")["data"]["user"]
    print("account:", user.get("display_name"))
    info = call(tok, "/post/publish/creator_info/query/", {})["data"]
    print("pubblicazione:", {k: info.get(k) for k in ("creator_username", "privacy_level_options",
                                                      "max_video_post_duration_sec")})
    print("OK: lettura riuscita, nessun caricamento fatto.")


def upload_file(upload_url, path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        request("PUT", upload_url, f.read(), {"Content-Type": "video/mp4",
                                              "Content-Range": f"bytes 0-{size - 1}/{size}"})


def wait_status(tok, publish_id):
    for _ in range(60):  # fino a 10 minuti
        st = call(tok, "/post/publish/status/fetch/", {"publish_id": publish_id})["data"]
        if st.get("status") in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE", "FAILED"):
            return st
        time.sleep(10)
    return st


def init_body(path):
    # un solo pezzo: va bene fino a 64 MB (i reel Next Human sono molto piu' piccoli)
    size = os.path.getsize(path)
    if size > 64 * 1024 * 1024:
        raise RuntimeError("video oltre 64 MB: serve il caricamento a pezzi")
    return {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}


def upload_draft(path):
    """Manda il video come bozza nella inbox TikTok (permesso video.upload)."""
    tok = access_token()
    d = call(tok, "/post/publish/inbox/video/init/", {"source_info": init_body(path)})["data"]
    upload_file(d["upload_url"], path)
    return wait_status(tok, d["publish_id"])


def post_direct(path, caption, privacy="SELF_ONLY"):
    """Pubblica direttamente sul profilo (permesso video.publish). Prima dell'approvazione: solo SELF_ONLY."""
    tok = access_token()
    body = {"post_info": {"title": caption[:2200], "privacy_level": privacy},
            "source_info": init_body(path)}
    d = call(tok, "/post/publish/video/init/", body)["data"]
    upload_file(d["upload_url"], path)
    return wait_status(tok, d["publish_id"])


def test():
    path = os.path.join(tempfile.mkdtemp(), "test_prova.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=30",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100", "-t", "5",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", path], check=True)
    st = upload_draft(path)
    print("stato:", st.get("status"), st.get("fail_reason", ""))
    if st.get("status") == "SEND_TO_USER_INBOX":
        print("OK: video di prova mandato come BOZZA nella inbox TikTok (notifica nell'app).")


if __name__ == "__main__":
    {"--check": check, "--test": test}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
