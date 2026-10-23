# Next Human - progetto e pubblicazione automatica

Next Human (@nnexthuman) e' la pagina Instagram di Graziano (Roma): reel in pixel art in inglese su corpo, longevita',
AI e futuro. Graziano scrive in italiano: rispondi in italiano, frasi brevi, un passo alla volta, niente gergo tecnico.

## Stato al 23 ottobre 2026 (passaggio dalla chat Claude a Claude Code)

- Produzione video: skill `next-human-reels` (account skill). Il motore si ripristina dall'artifact privato
  https://claude.ai/artifact/DYZZU4dt455uYpDVFSNhUp (file `nh_engine_v3.txt`), come spiega la skill.
- Reel gia' fatti e programmati a mano per il 23 ottobre: Stroke 02:00, No Sleep 06:00, Ozempic 10:00,
  80 Years Old 16:00, Cold Plunge 22:00 (episodi ep08-ep12 nel bundle del motore).
- Piano di lavoro con checklist (Claude Docs): https://claude.ai/artifact/5cMdwqk8KsZbgiYJxJT63x
- Descrizioni dei reel del 23 ottobre (Claude Docs): https://claude.ai/artifact/EuqTkB5Kpf8Ewh7Xjyudxz
- 10 script virali (Claude Docs): https://claude.ai/artifact/PCiAA1gXd6onpy6tGqMpX9
- Scala decisa: 5 reel il 24/10, 6 il 25/10, 7 al giorno dal 26/10 (orari Roma 02, 06, 10, 13, 16, 19, 22).

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
- `publish.py`: pubblica su Instagram i post in scadenza (aspetta l'orario esatto se mancano meno di 30 minuti),
  aggiorna la coda, toglie dal ramo `media` i video gia' pubblicati.
- Ramo `media`: solo i video in attesa (il repository e' pubblico). Per aggiungere un video: commit sul ramo `media`
  e push; poi la voce in `queue.json` su `main`.
- Comandi: test `python3 publish.py --check`; pubblicazione `python3 publish.py --due`.

## YouTube (in prova)

- Progetto Google Cloud "Next Human Publisher", YouTube Data API v3, client OAuth web. App pubblicata
  (In produzione, non verificata) il 23 ottobre: l'autorizzazione non scade dopo 7 giorni.
- Pagine pubbliche (ramo `gh-pages`, GitHub Pages): https://grazianomoreschi.github.io/nexthuman-media/
  con privacy.html e terms.html. Servono anche per l'app TikTok.
- Chiavi come variabili dell'ambiente Default: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`. Mai stamparle.
- `youtube.py`: test `python3 youtube.py --check`; video di prova privato `python3 youtube.py --test`.
- Finche' Google non verifica il progetto, i video caricati via API restano privati: Graziano li rende pubblici.

## Regole

- Nessun segreto in questo repository o in chat. Il token non va cercato ne' stampato: lo aggiunge il proxy.
  Se l'API risponde 401 o errore 190, il token e' scaduto: avvisa Graziano.
- Non modificare caption, video o orari approvati da Graziano. Non pubblicare nulla fuori dalla coda,
  non cancellare post.
- Se `publish.py --due` stampa ERRORE, riporta il messaggio esatto in una riga senza ritentare a mano.
- Alla fine di ogni esecuzione programmata rispondi con una riga: cosa e' stato pubblicato (con link) oppure
  "nessun post in scadenza".
