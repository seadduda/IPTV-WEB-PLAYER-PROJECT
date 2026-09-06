# IPTV Web Player Project

Web aplikacija za učitavanje i reprodukciju IPTV kanala putem Xtream Codes prijave. Aplikacija podržava grupe kanala, pretraživanje, EPG i tamno sučelje.

## Mogućnosti

- Xtream Codes prijava putem servera, korisničkog imena i lozinke.
- Automatsko pamćenje podataka za prijavu u lokalnom pregledniku.
- Prikaz i skrivanje lozinke pomoću ikone oka.
- Automatsko učitavanje IPTV kanala i grupa koje šalje provider.
- Pretraživanje kanala.
- Reprodukcija HLS, MPEG-TS, DASH i ClearKey streamova.
- Automatsko učitavanje EPG-a iz Xtream XMLTV izvora.
- Prikaz četiri sljedeće emisije ispod playera.
- Tamna tema prilagođena desktopu i mobitelu.
- Lokalni proxy za providerove redirecte i CORS ograničenja.

## Pokretanje

Potrebni su Python i moderan web preglednik, preporučeno Firefox.

1. Otvorite mapu projekta u terminalu.
2. Pokrenite lokalni server i proxy:

   ```powershell
   python local_server.py
   ```

3. Otvorite:

   ```text
   http://localhost:8000/index.html
   ```

4. Unesite Xtream server, korisničko ime i lozinku.
5. Kliknite `UCITAJ LISTU`.
6. Odaberite grupu i zatim kanal.

## EPG

EPG se učitava automatski iz Xtream XMLTV izvora. Ako provider ne šalje ispravan EPG ili blokira pristup, programi se neće prikazati.

## Napomene

- Streamovi ovise o provideru, njegovim serverima i dostupnosti kanala.
- Neki streamovi mogu imati CORS, DRM ili kodek ograničenja.
- Firefox se preporučuje za određene MPEG-TS streamove.
- Lokalni `local_server.py` mora ostati pokrenut dok koristite aplikaciju.
- Podaci za Xtream prijavu čuvaju se u `localStorage` preglednika. Nemojte koristiti javno ili dijeljeno računalo za osjetljive podatke.

## Datoteke

- `index.html` - glavno sučelje IPTV playera.
- `local_server.py` - lokalni HTTP server i proxy za streamove.
- `clearkey-test.html` - jednostavna ClearKey testna stranica.

## Licenca

Projekt je objavljen pod MIT licencom. Detalji se nalaze u datoteci `LICENSE`.
