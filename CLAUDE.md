# Next Human - progetto e pubblicazione automatica

Next Human (@nnexthuman) e' la pagina Instagram di Graziano (Roma): reel in pixel art in inglese su corpo, longevita',
AI e futuro. Graziano scrive in italiano: rispondi in italiano, frasi brevi, un passo alla volta, niente gergo tecnico.

## Stato al 23 ottobre 2026 (passaggio dalla chat Claude a Claude Code)

- Produzione video: skill `next-human-reels` (account skill). Il motore si ripristina dall'artifact privato
  https://claude.ai/artifact/DYZZU4dt455uYpDVFSNhUp (file `nh_engine_v4.txt`, con le scene cage, clock, walk, space, earth), come spiega la skill.
- Reel gia' fatti e programmati a mano per il 23 ottobre: Stroke 02:00, No Sleep 06:00, Ozempic 10:00,
  80 Years Old 16:00, Cold Plunge 22:00 (episodi ep08-ep12 nel bundle del motore).
- Piano di lavoro con checklist (Claude Docs): https://claude.ai/artifact/5cMdwqk8KsZbgiYJxJT63x
- Descrizioni dei reel del 23 ottobre (Claude Docs): https://claude.ai/artifact/EuqTkB5Kpf8Ewh7Xjyudxz
- 10 script virali (Claude Docs): https://claude.ai/artifact/PCiAA1gXd6onpy6tGqMpX9
- Scala decisa: 5 reel il 24/10, 6 il 25/10, 7 al giorno dal 26/10 (orari Roma 02, 06, 10, 13, 16, 19, 22).
- 24 ottobre, in coda (descrizione 1 scelta da Graziano): Human vs Robot 02:00, Clock Shift 06:00, 3,000 Steps 10:00,
  Taller in Space 16:00, The 2100 List 22:00 (ep13-ep17). Idee: https://claude.ai/artifact/XaGrbTxPpS3MEYxJR9DkCE ,
  descrizioni: https://claude.ai/artifact/9nJdAvbyrXMgkTsmBegKQ8 . Stile voluto: hype nel tono, niente decimali,
  ma ogni frase vera. Scene nuove salvate nel bundle v4.

### Fase 1 (accessi) - fatto
- Instagram @nnexthuman professionale (Creator). App Meta "Next Human Publisher" (Instagram Login, senza Pagina FB):
  ID app Instagram 1882627469784029, account Instagram ID 17841480036080171, tester accettato,
  autorizzazioni instagram_business_basic / content_publish / manage_comments / manage_insights / manage_messages.
- Token Instagram salvato come network secret nell'ambiente cloud **Default** (host graph.instagram.com,
  header Authorization: Bearer). Scade dopo 60 giorni (circa 22 dicembre 2026): rinnovarlo prima.
- GitHub: questo repository (pubblico), push funzionante. TikTok e YouTube: account da collegare in seguito.

### Prossimi passi
1. Verificare che l'ambiente Default abbia Network access Custom con: graph.instagram.com, api.instagram.com,
   graph.facebook.com, rupload.facebook.com, www.googleapis.com, oauth2.googleapis.com, open.tiktokapis.com
   (+ lista predefinita).
2. Test in sola lettura: `python3 publish.py --check`.
3. Se riesce: attivita' programmata oraria in questo repository e ambiente con prompt
   "Segui CLAUDE.md: esegui python3 publish.py --due e rispondi con una riga."
4. Primo post reale in coda solo dopo l'ok esplicito di Graziano.
5. Poi Fase 3-5 del piano (idee giornaliere 08:00, statistiche 23:30, funnel PDF).

## Pubblicazione

- `queue.json`: coda. Ogni post ha `id`, `publish_at` (ISO con fuso, ora di Roma), `video` (file sul ramo `media`),
  `caption`, `first_comment`, `status` (`pending`, `published`, `error`).
- `publish.py`: pubblica su Instagram i post in scadenza (aspetta l'orario, poi un ritardo a caso fino a 3 minuti
  per sembrare piu' naturale; regola di Graziano),
  aggiorna la coda, toglie dal ramo `media` i video gia' pubblicati.
- I video in attesa stanno nell'artifact **privato** https://claude.ai/artifact/UoBSQKjDW8Jfk1ri1RuXGy (un file mp4
  per post, stesso nome del campo `video`). Graziano non vuole i video pubblici su GitHub per ore.
- Esecuzione programmata (15 minuti prima di ogni slot): per ogni post `pending` con `publish_at` entro 30 minuti,
  scarica il video dall'artifact con lo strumento Artifact (`action: read`, `path` = nome del video,
  `out_dir` = la cartella `incoming/` del repository), poi `python3 publish.py --due`. `publish.py` mette il video sul
  ramo `media` solo in quel momento e lo toglie dopo la pubblicazione. `incoming/` non va mai nel repository.
- Per aggiungere un post: carica l'mp4 nell'artifact privato (stesso URL, nuovo file) e aggiungi la voce in
  `queue.json` su `main`.
- Comandi: test `python3 publish.py --check`; pubblicazione `python3 publish.py --due`.
- Campi facoltativi per le altre piattaforme: `youtube` ({`title`, `description`}) carica lo Short (privato) e
  `tiktok` (true) manda la bozza nella inbox. Un tentativo ciascuno; esiti in `youtube_id` / `tiktok_status`
  oppure `youtube_error` / `tiktok_error`. Non bloccano Instagram.

## YouTube (in prova)

- Progetto Google Cloud "Next Human Publisher", YouTube Data API v3, client OAuth web. App pubblicata
  (In produzione, non verificata) il 23 ottobre: l'autorizzazione non scade dopo 7 giorni.
- Pagine pubbliche (ramo `gh-pages`, GitHub Pages): https://grazianomoreschi.github.io/nexthuman-media/
  con privacy.html e terms.html. Servono anche per l'app TikTok.
- Chiavi come variabili dell'ambiente Default: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`. Mai stamparle.
- `youtube.py`: test `python3 youtube.py --check`; video di prova privato `python3 youtube.py --test`.
- Finche' Google non verifica il progetto, i video caricati via API restano privati: Graziano li rende pubblici
  (o li programma da YouTube Studio).
- Regola di Graziano: titolo YouTube SENZA `#shorts`.

## TikTok (in prova, Sandbox)

- Organizzazione "Next Human" su developers.tiktok.com, app "Next Human Publisher" (tipo Other): Login Kit +
  Content Posting API, permessi user.info.basic e video.upload (solo bozze nella inbox; Direct Post e
  video.publish tolti il 23 ottobre: per approvarli serve una nostra schermata di scelta privacy per ogni post).
  Sito verificato con file sul ramo `gh-pages`. Redirect URI: .../nexthuman-media/tiktok-callback.html
  (pagina di collegamento: lo scambio del codice avviene nel browser di Graziano).
- In uso la **Sandbox** "Next Human Test" (utente di prova nnexthuman). Variabili dell'ambiente Default:
  `TT_CLIENT_KEY`, `TT_CLIENT_SECRET`, `TT_REFRESH_TOKEN` (della Sandbox; il refresh token dura circa 365 giorni).
  Rete: open.tiktokapis.com e open-upload-i18n.tiktokapis.com.
- `tiktok.py`: test `python3 tiktok.py --check`; bozza di prova nella inbox `python3 tiktok.py --test`.
- Revisione Production inviata il 23 ottobre (2 video demo dalla Sandbox). Dopo l'approvazione: chiavi Production
  nelle variabili TT_*, nuovo collegamento dalla pagina tiktok-callback.html, nuovo TT_REFRESH_TOKEN.
- Flusso: lo script manda la bozza nella inbox TikTok, Graziano la pubblica dall'app (puo' aggiungere musica).

## Statistiche (revisione serale)

- `python3 stats.py`: legge Instagram (per reel: views, reach, like, commenti, condivisioni, salvataggi, secondi medi
  di visione; account: follower, reach e views del giorno) e YouTube (views, like, commenti). Scrive
  `stats/reels.json`, `stats/daily.json` e lo storico `stats/history.json`. TikTok: nessuna statistica via API
  (servirebbero i permessi user.info.stats e video.list).
- Dashboard privata "Next Human Stats": https://claude.ai/artifact/F2mXFN1xKpaLBuHvPMPJU3 (tipo Dashboard; i dati
  sono file caricati come asset e collegati ai documenti `datasets/reels`, `datasets/daily`, `datasets/notes`).
- `stats/notes.json`: la revisione di Claude (righe `{date, order, kind, text}`: order 1 = Sintesi, poi Funziona,
  Non funziona, 3 x Da cambiare). Graziano vuole una revisione ogni sera perche' i numeri non vanno bene.

## Sistema di crescita (impara da solo)

- Skill di progetto `.claude/skills/next-human-growth` (revisioni, controllo prima di ogni reel, idee).
  Usala per OGNI revisione e PRIMA di scrivere qualsiasi nuovo reel (insieme alla skill next-human-reels):
  le regole PROVEN e TESTING di `growth/playbook.md` vincono sulle abitudini della skill dei reel.
- File vivi: `growth/playbook.md` (regole con stato ed evidenze), `growth/experiments.json`,
  `growth/learnings.md`, `growth/catalog.json` (una riga per ogni episodio, da aggiungere a ogni render),
  `growth/ideas.md` (banca idee).
- Revisioni automatiche: 13:05 (meta' giornata) e 23:05 (fine giornata), attivita' "Next Human - revisione serale".
- Esperimento aperto E1: formato v2 (20-25 s, frase e numero al primo fotogramma, niente intro, CTA "send this
  to the friend who...") contro v1. I reel del 24/10 sono v1; dal 25/10 si producono in v2.

## Regole

- Nessun segreto in questo repository o in chat. Il token non va cercato ne' stampato: lo aggiunge il proxy.
  Se l'API risponde 401 o errore 190, il token e' scaduto: avvisa Graziano.
- Non modificare caption, video o orari approvati da Graziano. Non pubblicare nulla fuori dalla coda,
  non cancellare post.
- Se `publish.py --due` stampa ERRORE, riporta il messaggio esatto in una riga senza ritentare a mano.
- Alla fine di ogni esecuzione programmata rispondi con una riga: cosa e' stato pubblicato (con link) oppure
  "nessun post in scadenza".
