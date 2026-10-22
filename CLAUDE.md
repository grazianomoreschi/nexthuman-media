# Next Human - pubblicazione automatica

Questo repository serve solo a pubblicare i reel di @nnexthuman (Instagram) a orari fissi.
I video e le descrizioni li prepara Graziano con Claude in un'altra chat; qui arrivano gia' approvati.

## Cosa c'e'

- `queue.json`: la coda. Ogni post ha `id`, `publish_at` (ISO con fuso, ora di Roma), `video` (file sul ramo `media`),
  `caption`, `first_comment`, `status` (`pending`, `published`, `error`).
- `publish.py`: legge la coda, pubblica su Instagram con l'API (login Instagram), aggiorna la coda, toglie dal ramo
  `media` i video gia' pubblicati.
- Ramo `media`: solo i video in attesa. Il repository e' pubblico: nessun segreto va mai scritto qui.

## Regole

- Il token Instagram non e' nel repository e non va cercato ne' stampato: lo aggiunge il proxy dell'ambiente cloud
  (network secret su `graph.instagram.com`). Se una chiamata risponde 401/190, il token e' scaduto: avvisa Graziano.
- Non modificare caption, video o orari della coda: sono stati approvati da Graziano.
- Non cancellare post su Instagram e non pubblicare nulla che non sia nella coda.
- Se `publish.py --due` stampa ERRORE, riporta il messaggio esatto in una riga, senza ritentare a mano.

## Comandi

- Test in sola lettura: `python3 publish.py --check`
- Pubblicazione programmata (la routine oraria esegue questo): `python3 publish.py --due`

Alla fine di ogni esecuzione rispondi con una riga: cosa e' stato pubblicato (con il link) oppure "nessun post in scadenza".
