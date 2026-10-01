# Raynet: návrh optimalizace pro Evergreen

K 2026-10-01. Vychází z celé nápovědy Raynetu (323 článků), REST API v2, dokumentace MCP, průzkumu vlastních polí instance
„evergreen“ a ze zkušebních zápisů 1. 10. 2026. Odkazy na nápovědu a plné poznámky: `docs/RAYNET-MANUAL-POZNAMKY.md`
(„A/<id>“ = `https://support.raynetcrm.com/hc/cs/articles/<id>`).

**Plán: Professional** (Adam, 1. 10. 2026). Limity: 100 vlastních polí, z toho 25 povinných · automatizace 50 průběhů
za měsíc · 8 webhooků · 8 API klíčů (zdroj: https://raynet.cz/cena/, A/17161403974941, A/13505394647837).

## Shrnutí

Největší díra není v nástroji, ale v pravidlech. Raynet umí vynutit, co dnes chybí (banka, zdroj a odhad uzavření u OP,
další krok u každého případu, kategorie prohry), a MCP tato pole umí zapsat. Pět nastavení za ~4 hodiny opraví forecast
a pipeline. Úklid úkolů po termínu je jednorázový, potom je potřeba zavřít zdroj, který je zakládá.

## A. Nastavení Raynetu (seřazeno podle přínosu)

| # | Co | Kde v Raynetu | Proč | Pracnost |
|---|---|---|---|---|
| 1 | **Povinná pole podle fáze OP.** Od „Nabídnuto“ zdroj, kategorie a odhad uzavření. Od „Podaná žádost“ banka (`producent`) a výše úvěru. | Nastavení » Nastavení evidence » Obchodní případ » Nastavení polí (A/4414383755281) | Banka dnes chybí u 78 % pipeline, odhad uzavření u 82 z 91 OP, takže forecast nefunguje. Vynucuje se i při přetažení na nástěnce. | 1–2 h |
| 2 | **Povinný follow-up** u otevřených OP (fáze Identifikace až Schváleno). | Nastavení evidence » OP (A/31763398123165) | Každý otevřený případ má naplánovaný další krok. Nahradí „automatické“ upomínky, které dnes visí po termínu. | 15 min |
| 3 | **Kategorie prohry: přidat 5 nejčastějších důvodů** (rozbor všech 56 proher a 71 zrušených OP, 1. 10. 2026, níže). | Nastavení » číselník Kategorie prohry (`losingCategory`) | Dnes je 31 z 53 skutečných proher „jiná“ a i mimo ni je zařazení chybné. Po změně zůstane v „jiná“ 1 případ. | 30 min + přetřídění 1 h |
| 4 | **Pravděpodobnost u každé fáze.** | Typy obchodu » Upravit nastavení (A/201738406) | Vážený objem v Prodejním trychtýři. MCP pravděpodobnost při změně fáze přepočítá sám. | 30 min |
| 5 | **Vlastní pole OP jako číselníky:** banka, fixace, účel jako roletky; LTV a sazba jako procenta. Nepřejmenovávat pole, která plní web a appka podle názvu. | Nastavení » Vlastní pole (A/5276401814033) | Dnes např. `Doba_fixac` zná jen „3 roky“, `LTV` je číslo, `Soucasny_c` (čistý nájem) je text. | 2–3 h |
| 6 | **Příznak „Fyzická osoba“** u ~94 % klientů (skript přes REST API `person=true` + jméno a příjmení) a **GDPR modul** (právní tituly, anonymizace, export). | REST API; Nastavení » GDPR (A/6370130507025, A/360020541691) | Správné řazení a hledání podle příjmení, GDPR záložka. MCP fyzickou osobu neumí, REST ano. | 0,5 dne |
| 7 | **Participanti OP** (spoludlužník, ručitel, makléř, tipař) a **vztahy mezi klienty** (domácnost). | Nastavení evidence (A/205141569, A/360016817971) | Hovor s manželkou nebo rodičem se dá navázat na OP dlužníka. Snižuje riziko zápisu pod jiného klienta. | 15 min |
| 8 | **Sdílené filtry na nástěnce:** OP bez banky / zdroje / odhadu, OP bez další aktivity, úkoly po termínu, prohry bez kategorie, záznamy se štítkem „AI zápis“ za týden. | Seznamy » Uložit filtr, Nástěnka (A/5883883874705) | Týdenní kontrola kvality dat i AI zápisů za 5 minut. | 1 h |
| 9 | **Kategorie aktivit zredukovat** na ~5. „Soukromá aktivita“ aktivitu před kolegy neskrývá (A/4404457810705). | Nastavení » Kategorie aktivit (A/206377235) | Dnes 8 kategorií, většinou nepoužité (ve vzorku `category: null`). | 30 min |
| 10 | **API klíč „Hermes“** pro každého kolegu (Professional = max. 8 klíčů, při víc poradcích integrační licence). | Nastavení » API klíče (A/360032478072) | Webhook a historie změn ukážou `source=api` + název klíče, takže zápisy AI půjde auditovat. | 30 min |

### Bod 3 v detailu: důvody prohry

Rozbor k 2026-10-01: 56 proher (z toho 3 testy) a 71 zrušených OP. Důvody pod „jiná“ jsou odvozené z textu a aktivit `[odvozeno]`.

**5 nových kategorií** (seřazeno podle počtu, kolik dnešních proher pokryjí; v závorce zrušené OP):

| # | Nová kategorie | Proher | Jak zavést |
|---|---|---|---|
| 1 | **Klient přestal komunikovat** | 14 (+2) | **Přejmenovat 203 „nezvedá“** (zachová historii) a přeřadit 9 z „jiná“ a 3 z kategorie 200 |
| 2 | **Klient si to rozmyslel / odložil** | 7 (+8) | nová položka |
| 3 | **Klient řeší napřímo v bance / u developera** | 4–6 | nová položka; 125 přejmenovat na „Konkurence (jiný poradce)“ |
| 4 | **Duplicita / test / chybně založeno** | 6 (+24) | nová položka; lépe ale takové OP rovnou zrušit nebo smazat, ať nekazí úspěšnost |
| 5 | **Klient nedodal podklady** | 1 (+9) | nová položka |

Dále:
- 200 přejmenovat na „Záměr koupě nevyšel / nemovitost neprošla“ (dnes v ní sedí jen 1 případ ze 6),
- 126 „termín“ zrušit (0 použití),
- u „jiná“ vyžadovat text důvodu (dnes „.“, „?“, „neznámo“),
- **zrušené OP mají důvod taky vyplňovat**: dnes ho nemá ani jeden ze 71.

**Kde se prohrává** (53 proher): Identifikace 22 · Nabídnuto 13 · Podaná žádost 7 · Čeká na schválení 5 · Kompletace 3 · Schváleno 3.
Klienti, kteří přestali komunikovat, mizí nejčastěji **po odeslání nabídky** (7 ze 14). Bod 2 (povinný další krok u OP) míří
přesně sem. Ze zrušených OP navíc 6 skončilo tím, že follow-up neproběhl z naší strany.

**Automatizace šetřit:** Professional má jen **50 průběhů za měsíc** a časový spouštěč spotřebuje průběh za každý nalezený
záznam (A/13505394647837). Hodí se na pár věcí (prohra bez kategorie → notifikace). Větší logiku dát do Herma přes webhook,
nebo dokoupit Stavitel (3 000 průběhů za 1 000 Kč/měs.).

**Pozor u Google kalendáře:** synchronizace je obousměrná. **Zrušení aktivity v Raynetu ji v Googlu smaže** a smazání v Googlu
ji smaže i v Raynetu. Označení „hotovo“ se do Googlu nepropíše (A/203015978). AI proto schůzky nikdy neruší, jen dokončuje.

**Rozpor s dřívějším rozhodnutím:** manuál doporučuje vést provize (pole Provize Kč, stav výplaty). Adam 28. 9. 2026 hlídání
provizí zrušil kvůli administrativě (vault `crm-raynet`). Návrh proto neobsahuje provizní pole. Pokud by se vracelo,
stačí 1 pole „Provize (Kč)“ jako Konečná cena OP a reporty ziskovosti začnou fungovat.

## B. Pravidla pro AI zápisy (zapracováno do skillu)

- Výsledek hovoru patří do `solution` („Výsledek telefonátu / jednání“), příprava a agenda do `description`. Potvrzeno API dokumentací.
- Povolené HTML: `<p> <b> <i> <br> <ul> <ol> <li> <a>`. Tabulky a `<pre>` Raynet odstraní (ověřeno), nápověda to nepopisuje.
- Naplánovaná aktivita se dokončí, ne zduplikuje. Schůzky se nikdy neruší (kvůli Google kalendáři).
- Štítek „AI zápis“ na každé aktivitě. Do budoucna i externí ID `pocket:<recordingId>` (REST API, až 10 na záznam).
  Dalo by se podle něj spolehlivě hledat duplicity, MCP ho ale zatím nenastaví.
- Vlastník se zjišťuje za běhu (`user_info` → `person_list(email)`), každý kolega zapisuje sám za sebe.
- Řešitel úkolu se mění jen přes `participants`. Výsledek vždy ověřit zpětným čtením.

## C. Úklid dat (jednorázově)

1. **Úkoly po termínu (113 ze 144):** Raynet úkoly sám neuzavírá. Pravděpodobný zdroj je web egfin.cz, který ke každému leadu
   zakládá úkol na +1 den `[odhad]`. Staré úkoly hromadně uzavřít (seznam úkolů → filtr → Hromadná změna, max. 200 najednou,
   A/5926222392593). Pak upravit web: úkol zakládat jen u nezpracovaného leadu, nebo ho uzavřít při konverzi.
2. **Testovací OP (~13) a testovací klienty** zneplatnit. Mezi nimi je i zkušební telefonát 37590 „TEST formátu zápisu – smazat“
   u klienta „Jan Ukazkovy (TEST)“ (smazat v UI).
3. **Duplicity klientů** sloučit (⋯ » Sloučit, A/360000822106; potřeba právo mazat; z A do B se převedou jen pole, která jsou v B prázdná).
4. **91 otevřených OP:** Hermes z historie aktivit navrhne banku, zdroj a odhad uzavření, poradce je potvrdí v seznamu.
5. **31 proher „jiná“** překlasifikovat podle nového číselníku.

## Co ověřit v instanci

- jestli povinná pole platí i pro zápisy přes API a MCP,
- kde je číselník kategorií prohry a jestli se na ni ptá dialog při Prohře,
- odkud vznikají automatické úkoly (web, historie automatizací),
- jestli MCP opravdu zapíše `scheduledEnd` a `losingCategory` (stačí test na testovacím OP).
