"""Next Human - caricamento degli Shorts su YouTube.

Uso:
  python3 youtube.py --check   test in sola lettura (nome del canale)
  python3 youtube.py --test    carica un video di prova PRIVATO di 5 secondi

Le chiavi NON sono in questo repository: sono variabili dell'ambiente cloud
(YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN). Non vanno mai stampate.
Finche' Google non verifica il progetto, i video caricati via API restano privati.
"""
import json, os, subprocess, sys, tempfile, urllib.parse, urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos"


def request(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.headers, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:500]
        raise RuntimeError(f"HTTP {e.code} {urllib.parse.urlparse(url).path}: {body}")


def access_token():
    missing = [v for v in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(v)]
    if missing:
        raise RuntimeError("variabili mancanti nell'ambiente: " + ", ".join(missing))
    data = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"],
                                   "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ["YT_REFRESH_TOKEN"],
                                   "grant_type": "refresh_token"}).encode()
    return request("POST", TOKEN_URL, data)[1]["access_token"]


def check():
    tok = access_token()
    _, r = request("GET", API + "/channels?part=snippet,statistics&mine=true",
                   headers={"Authorization": "Bearer " + tok})
    for c in r.get("items", []):
        print("canale:", c["snippet"]["title"], c["snippet"].get("customUrl", ""),
              "| video:", c["statistics"].get("videoCount"))
    if not r.get("items"):
        print("ERRORE: nessun canale collegato a questo account")
        return
    print("OK: lettura riuscita, nessun caricamento fatto.")


def upload(path, title, description, privacy="private"):
    """Caricamento in due passi (resumable): restituisce l'ID del video."""
    tok = access_token()
    meta = {"snippet": {"title": title[:100], "description": description[:5000], "categoryId": "27"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
    size = os.path.getsize(path)
    headers, _ = request("POST", UPLOAD + "?uploadType=resumable&part=snippet,status",
                         json.dumps(meta).encode(),
                         {"Authorization": "Bearer " + tok, "Content-Type": "application/json; charset=UTF-8",
                          "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    with open(path, "rb") as f:
        _, r = request("PUT", headers["Location"], f.read(),
                       {"Authorization": "Bearer " + tok, "Content-Type": "video/mp4"})
    return r["id"]


def update_title(video_id, title, description):
    """Cambia titolo e descrizione di un video gia' caricato (permesso youtube.force-ssl)."""
    tok = access_token()
    body = {"id": video_id, "snippet": {"title": title[:100], "description": description[:5000], "categoryId": "27"}}
    request("PUT", API + "/videos?part=snippet", json.dumps(body).encode(),
            {"Authorization": "Bearer " + tok, "Content-Type": "application/json; charset=UTF-8"})


def test():
    path = os.path.join(tempfile.mkdtemp(), "test_prova.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=30",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100", "-t", "5",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", path], check=True)
    vid = upload(path, "Test Next Human (privato)", "Video di prova del caricamento automatico.")
    print(f"OK: video di prova caricato come PRIVATO: https://youtube.com/shorts/{vid}")


if __name__ == "__main__":
    {"--check": check, "--test": test}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
