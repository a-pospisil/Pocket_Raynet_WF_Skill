# API pro bonitu a metodiku bank pro AI agenty (Hermes, zápisy z Pocketu do Raynetu)

## Proč

Zápisy z hovorů do Raynetu dělá skill `pocket-to-raynet` (repo `a-pospisil/Pocket_Raynet_WF_Skill`). U úvodní schůzky a při
každé změně příjmů, závazků nebo záměru počítá **bonitu pro 8 bank** (ČS, ČSOB, KB, RB, UCB, mBank, Oberbank, MONETA)
a zapíše ji do karty obchodního případu.

Dnes skill bere pravidla z Adamova vaultu (`wiki/metodiky`). Kolegové k němu přístup nemají, vault obsahuje osobní údaje.
Skill poběží v **Hermes Agent** u každého poradce zvlášť. **Metodika a výpočet mají být na jednom místě: v appce.**
Engine `/bonita` už většinu umí (`src/lib/bonita.ts`, `bank-modules.ts`, `banks.json`, `rates.json`). Chybí API pro agenty.

## Co potřebujeme

### 1. `POST /api/v1/bonita`

**Vstup** (JSON):
- žadatelé: věk, typ a výše příjmů
  - zaměstnání: čistá mzda, průměr 3 / 6 / 12 M,
  - OSVČ: řádky DP nebo paušál, obrat, paušální daň,
  - s.r.o.: řádky DP, podíl,
  - ostatní příjmy;
- domácnost: počet vyživovaných osob;
- nájmy **po nemovitostech**: nájem celkem a čistý, podíl, způsob doložení (DP §9 s ř. 201 / 202 / 206, odpisy a úroky; smlouva + výpisy,
  počet plateb; budoucí nájem), spjatá osoba, krátkodobý pronájem;
- závazky: splátky, zůstatky, limity KK a KTK, celkový stávající dluh;
- záměr: účel, cena, požadovaný úvěr, hodnota zástavy, typ nemovitosti, investiční / vlastní bydlení, refinancování (podíl z výše úvěru), splatnost.

**Výstup po bankách** (pro všech 8 bank, na přání i další):
- uznaný příjem s rozpadem: z čeho, jakým koeficientem, ze kterého řádku DP;
- max. splátka a limit DSTI (včetně pásma nebo výjimky);
- strop DTI a strop LTV;
- sazba a stres: zdroj (`rates.json` / tržní průměr) a datum sazby;
- **max. úvěr a co ho limituje** (DSTI / ŽM / DTI / LTV);
- při zadané částce: projde / neprojde, splátka, DSTI, DTI, LTV, rezerva do stropu;
- poznámky k pravidlům banky (např. „záporný ř. 206 = 0“) a původ parametrů (`_zdroj`, `_bezMetodiky`).

**Chybějící vstup → rozpětí min–max:** pesimistická a optimistická varianta a jedna věta, který předpoklad dělá rozdíl. Nic nedomýšlet.

### 2. `GET /api/v1/metodika`

Parametry bank (`banks.json`) a sazby (`rates.json`) s datem, verzí (commit) a původem. Agent podle toho cituje zdroj a stáří
a pozná, že je sazba starší než 1 měsíc.

### 3. Přístup a audit

- API klíč **pro každého poradce / agenta** (Hermes u každého zvlášť), rate limit, chybové stavy.
- Audit: kdo, kdy, která verze parametrů. **Neukládat plné vstupy** s osobními údaji klientů (GDPR); stačí hash vstupu a id klienta v Raynetu.

### 4. Sjednotit engine s metodikou, než ho pustíme agentům

Podle vaultu (tematické stránky, sekce ⚠️ Rozpory) je engine místy štědřejší než metodiky bank:
- **budoucí nájem** 70 % (UCB 60 %) i u bank, kde metodika dává 0 (ČSOB, UCB, mBank, MONETA);
- **KB:** chybí cesta přes výpisy (3 výpisy = 70 % obratu, 1 výpis + smlouva = 70 % nájmu, i při záporném §9; Adam 28. 9. 2026);
- **ČSOB:** refinancování ≥ 50,01 % výše úvěru + koupě/refundace ≤ 49,99 % = ne investiční hypotéka, LTV 80 % / DTI 12 (Adam 1. 10. 2026);
- **mBank:** poměrná daň u nájmu se liší až o 400 Kč (z regrese 10. 9. 2026, neopraveno).

Hierarchie pravdy (vault `CLAUDE.md` §5.6): originální metodika banky a odečtená kalkulačka > souhrn BT > engine. Když je appka
jediné místo, má platit, že změna metodiky se dělá v appce a vault ji jen dokumentuje.

## Akceptační kritéria

- [ ] `POST /api/v1/bonita` vrátí pro testovací vstup níže výsledek pro 8 bank s plným rozpadem a s „co limituje“.
- [ ] Kontrolní čísla sedí: RB list `Bonita` (příjem 65 000 Kč, úvěr 5 mil. / 30 let / 5,09 %) → max. úvěr 7 191 000 Kč;
      regresní testy `bank-regression.test.ts` rozšířené o nájmy (DP, výpisy, budoucí).
- [ ] Chybějící vstup vrátí rozpětí, ne odhad.
- [ ] Rozpory z bodu 4 opravené, nebo ve výstupu označené jako „engine ≠ metodika“.
- [ ] Klíč per agent, OpenAPI dokumentace endpointů.
- [ ] Navazuje úprava skillu `pocket-to-raynet`: čte bonitu z API místo z vaultu (issue v repu skillu).

## Testovací vstup (fiktivní)

Zaměstnanec 38 let, čistá mzda 90 000 Kč (Ø 12 M), domácnost 1, KK limit 50 000.
- Byt 1: 2+1 Praha 9, OV, 1/1, nájem 18 000 / čistý 15 000, smlouva na dobu určitou, v DP 2025, ČSOB 3,1 mil. / 17 900.
- Byt 2: 1+kk Brno, OV, 1/1, nájem 14 000 / čistý 12 000, smlouva od 3/2026, 7 plateb přes účet, není v DP, KB 2,4 mil. / 13 600.
- DP 2025 §9: ř. 201 = 180 000, ř. 202 = 196 000 (odpisy 90 000, úroky 98 000), ř. 206 = −16 000.
- Záměr: 3. byt k pronájmu, cena 5 000 000, úvěr 3 500 000 (LTV 70 %), 30 let.

Očekávané pořadí: KB (výpisy), ČSOB, mBank, ČS (smlouvy) na 3,5 mil. (limit LTV); RB Profit, Oberbank, MONETA, ČS (DP) a UCB níž
(limit DSTI nebo DTI). Přesná čísla dá engine.

## Mimo rozsah

Zápis do Raynetu (dělá skill), sběr sazeb (srovnávač už běží).
