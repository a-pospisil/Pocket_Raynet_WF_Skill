# Raynet CRM – poznámky z nápovědy a API dokumentace (stav k 2026-10-01)

Zpracováno pro Evergreen Finance (instance „evergreen“). Poznámky = fakta z oficiální nápovědy/API + URL. Odhady označeny [odhad].

## 0. Zdroje a dostupnost

- `https://help.raynet.cz` – nefunguje (TLS certifikát neodpovídá hostname, curl error 60).
- `https://raynet.cz/napoveda/` – HTTP 404 (Next.js stránka bez obsahu nápovědy); odkazuje na Zendesk `support.raynetcrm.com/hc/cs`.
- `https://support.raynetcrm.com/hc/cs` (HTML frontend Zendesk) – **HTTP 403** (ochrana proti botům).
- **Obejito přes veřejné Zendesk Help Center API**: `https://support.raynetcrm.com/api/v2/help_center/cs/articles.json?per_page=100&page=1..4`
  → staženo **všech 323 českých článků** (11 kategorií, 36 sekcí, ~800 000 znaků textu). Plné texty v `(lokální stažení, neverzováno) txt/<id>.txt`, obsah `(lokální stažení, neverzováno) toc.txt`.
  URL článku = `https://support.raynetcrm.com/hc/cs/articles/<id>` (níže zkráceně `A/<id>`).
- `https://app.raynet.cz/api/doc/` – OK (Redoc, 5,9 MB HTML s vloženou OpenAPI specifikací) → `(lokální stažení, neverzováno) api-doc.html`.

Kategorie nápovědy: TOP, Mobilní aplikace, Jak začít, Nastavení a ovládání aplikace, Adresář, Obchod, Kalendář a aktivity, Integrace, Automatizace, Jak pracovat s e-maily, FAQ.

## 1. Adresář: klient (firma / fyzická osoba), kontaktní osoby, duplicity

- **Klient** = firma/organizace v Adresáři; jediné povinné pole Název (našeptávač z rejstříku). A/6370130507025
- **Klient jako fyzická osoba**: do Názvu jméno a příjmení + zatržítko **„Fyzická osoba“**; takto vedené osoby se v seznamu **řadí/filtrují podle příjmení**; s modulem GDPR se na kartě objeví záložka GDPR (právní tituly). A/6370130507025
  → Raynet NEMÁ samostatnou entitu „klient – fyzická osoba“; FO = Klient (`company`) s příznakem. „Kontaktní osoba“ (`person`) je osoba navázaná na klienta.
- Karta klienta: Stav + Vztah (systémové, **nelze editovat položky**; nový klient = Potenciální, po Výhře OP → Aktuální), Kategorie, Rating, Obor, **Zdroj kontaktu**, Původní lead, Štítky, Vlastník, adresy (jedna = kontaktní), záložky Časová osa, Kontaktní osoby, Navázané záznamy, Poznámky (sticky notes), **Vlastní pole**, Online podepisování; boční panel = součet prodaných a rozjednaných OP, dny do další/od poslední aktivity. A/201806493, A/29248287823901
- Pro vlastní třídění klientů: **Kategorie** (editovatelný číselník, s barvou), **Klasifikace 1–3** (3 roletky, lze přejmenovat), **volitelná pole**. A/29248287823901, A/360019176951
- Kontaktní osoba: Vlastník, Kategorie, Původní lead, Poznámka, Štítky; Osobní informace (pohlaví, datum narození, rodinný stav, oslovení); záložky GDPR, vlastní pole; „tón komunikace“. A/202132568
- Kontaktní osoba může mít **hlavní vazbu** na klienta + **vedlejší vazby** na další klienty (s pozicí a poznámkou). A/201623716, A/29540282319005
- **Vztahy mezi klienty** (rozšíření, admin: Nastavení » Nastavení evidence » Klient » Obecná nastavení): mateřská/dceřiná/volné propojení; sloupce „Prodáno ve skupině“, „Rozjednáno ve skupině“. A/360016817971 → použitelné pro domácnost/manžele/spoludlužníky [odhad].
- **Slučování duplicit**: klienti, kontaktní osoby, leady; jen stejného typu. Detail záznamu A » ⋯ » Sloučit s jiným klientem → vybrat B. Logika: vše z A přejde do B, **A se smaže**; kompletní historie se převádí; pole z A se převedou jen pokud jsou v B prázdná (soc. sítě, kontaktní osoby, adresy a kontakty – původní adresa jako další, propojení, poznámka, další údaje, volitelná pole). **Uživatel musí mít právo mazat.** A/360000822106
- Smazání klienta jen bez navázaných záznamů; jinak **Zneplatnit** (i hromadně ze seznamu, včetně navázaných KO); zobrazení přes filtr „Platnost“; obnovení platnosti. A/360020742511, A/4405581777169, A/29106699002141
- OP lze přepojit na jiného klienta: OP » ⋯ » Nastavení » Změna klienta. A/360020742511, A/201623656

## 2. Vlastní (volitelná) pole, povinná pole, číselníky, customizace karty

- Volitelná pole lze přidat **ke všem typům záznamů** (Klient, KO, Lead, OP, aktivity – úkol, schůzka, telefonát…). Vytváří jen **Administrátor**: Nastavení » Nastavení evidence » <typ záznamu> » Spravovat vlastní pole » Přidat panel » Přidat nové pole. **12 typů polí.** U pole zatržítka: zobrazit v seznamových pohledech / pokročilém filtru / exportech. Nápověda k poli max. 255 znaků (tooltip „?“). Smazání pole = smazání všech dat v něm. Po prvním poli vznikne na kartě záložka „Vlastní pole“; přes Customizaci lze pole přesunout kamkoli. A/5276401814033 (= A/7246791597841)
- Limity podle plánu: **START 5 vlastních polí, PROFESSIONAL 100, ULTIMATE 500**; povinná pole: START 0, **PROFESSIONAL 25**, ULTIMATE bez limitu. A/17161403974941, A/17162057052317
- **Povinná pole**: výchozí i volitelná; Nastavení » Nastavení evidence » <typ> » Nastavení polí. Nový záznam bez nich nejde uložit; při editaci starého záznamu je uživatel vyzván doplnit. **Hromadná změna povinná pole ignoruje.** Import: povinné sloupce tučně, chyby po řádcích. A/4414383755281
- **Povinné pole od stavu OP**: u OP lze nastavit, **od kterého stavu** je pole povinné; vynuceno při přetažení na Obchodní nástěnce i při změně stavu v detailu. A/4414383755281, A/4432592312593
- **Číselníky**: Nastavení » Nastavení evidence » Číselníky (např. Obchod » Obchodní případy » Kategorie); položky přejmenovat/smazat/zneviditelnit/řadit; číselníky jsou per typ záznamu. Většinu výchozích polí nelze přejmenovat (Stav, Vztah, **Zdroj**, Vlastník); přejmenovat lze **Kategorie a Klasifikace** (u všech typů, Kategorie s barvou). A/201849383, A/360019176951
- **Customizace karty** (admin, platí pro celý účet): ⋯ » Přizpůsobit podobu okna – vlastní záložky, panely, pole (drag & drop), povinnost pole, odstranění některých systémových polí, výchozí záložka, pořadí záložek. A/25234983930909
- **Potvrzení stavu záznamu** (OP, nabídka, objednávka, projekt): „podpis“ kdo a kdy zkontroloval; verze +1 při každém uložení OP; filtrovatelné. A/5089624670353
- **IFRAME** – vložení externího webu/aplikace jako záložky/panelu do detailu záznamu (nové 09/2026). A/39040250832157

## 3. Obchodní případy (OP)

- Detail OP: záhlaví (stav, Výhra/Prohra/Zrušeno, Typ obchodu, Založen, **Odhadované uzavření**), záložky Produkty, Nabídky/objednávky, Časová osa (+ RAYNET AI shrnutí OP), Navázané záznamy, Poznámky, Vlastní pole; boční panely: Čeho se to týká, **Participanti**, Kategorie + **Popis** + Štítky, hodnoty (Konečná cena, Předpokládaný zisk, Náklady – počítané z položek, ručně jen když OP nemá položky), nejbližší/poslední aktivita, Přílohy, Potvrzení stavu. A/201780597
- **Stavy** per typ obchodu: přejmenovat, přidat, zneplatnit, smazat, barva, **Pravděpodobnost** (%); edituje kdo má právo editovat číselníky (z detailu OP – ozubené kolečko) nebo admin v Nastavení » Nastavení evidence » Obchodní případ » Typy obchodu. Uzavřené stavy Výhra/Prohra/Zrušeno jsou pevné. A/201738406, A/360001098963
- **Typy obchodu** (rozšíření): víc pipeline s vlastními stavy; výchozí typ obchodu v profilu uživatele; hromadná změna typu = změnit Stav na stav jiného typu (hromadná změna). Limit počtu typů podle plánu. A/360001098963, A/29374362416541, A/17286900501277
- **Povinný Follow-up u otevřených OP** (admin: Nastavení evidence » OP, posuvník; lze omezit na vybrané stavy, per typ obchodu): po uložení otevřeného OP okno pro navazující aktivitu; jinak žlutá lišta + seznam OP bez naplánované aktivity, připomínka každých 15 min (lze odložit). A/31763398123165
- **Obchodní nástěnka** (Kanban): sloupce = otevřené stavy, drag & drop mění stav (respektuje povinná pole), pravým tlačítkem Výhra/Prohra/Zrušeno/Zvýraznit/Rozdělit; barva rohu = Kategorie; ukládané filtry, výchozí nástěnka. A/4432592312593
- Akce OP: Duplikovat, Série OP (opakované OP + volitelně úkol-upomínka ke každému), Rozdělit, Nastavení (Změna klienta / měny / kódu), Export PDF/XLSX (vlastní šablony), Bezpečnost (zamknutí, bezpečnostní úroveň, viditelnost), Zvýraznění, Smazat (jen bez vazeb). A/201623656, A/205068899
- **Participanti OP** (rozšíření, admin: Nastavení evidence » OP): další klienti a KO na OP, s barevnou kategorií a poznámkou → spoludlužník, ručitel, realitní makléř, tipař [odhad použití]. A/205141569
- Položky: produkty, produkty z ceníku, položka bez kategorizace; náklady u produktu → zisk. A/201657676, A/205654205
- Analýzy: **Odhad prodeje** (potřebuje vyplněné „Odhad uzavření“), **Prodejní trychtýř** (suma + vážený objem = hodnota × pravděpodobnost), **Výkon prodejního trychtýře** (průměrná doba ve stavu, konverze mezi stavy, % proher), Úspěšnost obchodníků, Prodej dle obchodníků/produktů, Vývoj prodeje/zisku, Ziskovost, ABC, Mapová analýza, Počet OP, Počet realizovaných aktivit; všechny s pokročilým filtrem, uložitelné filtry, export. A/4410153993105, A/201623776, A/4410136531345
- **Důvody prohry**: nápověda je samostatně nepopisuje (fulltext „důvod“ bez výsledku) – viz API (číselník losingReason) níže.

## 4. Aktivity

- Typy: **Úkol, Schůzka, Událost, Telefonát, E-mail, Dopis**. A/202133298
- Detail aktivity: typ lze změnit (šipka u typu; při změně Událost→Úkol se odeberou nadbyteční participanti), Předmět, **Kategorie** (paleta), stav + naplánování, připomenutí (zvoneček), **„Mám hotovo“ / Zrušit**, místo (U nás / U nich / GPS); záložky **Základní** (text aktivity, lze generovat/upravit AI), Navazující aktivity, Poznámka, Vlastní pole; Diskuze; boční panely Čeho se to týká (bez vazby = „Interní“), Vlastník + participanti, Kategorie, **Priorita**, Štítky, Přílohy. A/201780497
- **Úkol: vždy jeden Zadavatel a jeden Řešitel**; Deadline; prohození zadavatel↔řešitel tlačítkem se dvěma šipkami; víc řešitelů = duplikovat úkol, nebo pro skupinu použít Událost (více participantů). Notifikace: řešitel při přidělení, zadavatel při vypršení deadlinu (volitelně i když je splněno). Připomenutí se váže k naplánování (ne k deadlinu). A/360019701237, A/29058717970461
- Telefonát: pole **„K projednání“** při založení; zatržítko „realizovaný“ (zpětný zápis) a „soukromý“. A/4404831288209, A/202133298
- **Soukromá aktivita = bez vazby na klienta, NENÍ skrytá** před ostatními (vidí ji v kalendáři). A/4404457810705
- **Pozvánka e-mailem**: Schůzka/Událost » ⋯ » „Pozvat na schůzku/událost e-mailem“ → e-mail všem účastníkům s evidovaným e-mailem. Je to **ruční akce** (pozvánka se neodesílá automaticky při založení). A/115004799183, A/4404457810705, A/4404465454353
- **Opakování** (⋯ » Vytvořit opakování): interval, začátek, konec/počet, den v týdnu; změna „jen tato / i následující“. A/201780507
- **Připomenutí** (notifikace v Raynetu / e-mail / mobil / souhrnný e-mail); výchozí připomenutí pro všechny nové aktivity v Můj profil » Kalendář, i podle typu aktivity. A/201513355
- **Kategorie aktivit**: číselník (přidat/skrýt/smazat) + barvy; režim „jen barva“ nastavuje admin. A/206377235
- **Hromadné vytváření aktivit** ze seznamu klientů/KO, max. **200** najednou; předmět s parametry (název klienta, město, jméno osoby); plánované / nenaplánované / proběhlé. A/6003751137553
- Nenaplánované aktivity (bez data) – panel „Nenaplánováno“ vedle kalendáře. A/201777357
- E-mail aktivita: přenesené e-maily (Pošta, e-mailová asistentka, API) **nelze editovat** (obsah, předmět, korespondenti, čas); Zdroj e-mailu: Pošta / asistentka / API / nepodporovaný. A/4404825810833
- Úkol/aktivity: akce Duplikovat, Export PDF, Bezpečnost (zamknout), Smazat. A/201780507
- Pojmy „Řešení“ vs. „Popis“: nápověda je nerozlišuje (UI: záložka „Základní“ = popis/zadání; „K projednání“ u telefonátu; „Zadání úkolu“). Rozdíl je v API: `description` (zadání/popis před) vs. `solution` (řešení/zápis po realizaci) – viz API.

## 5. Automatizace (workflow)

- Pojmy: Spouštěč → Podmínka → Akce; Průběh = spuštění s ≥1 úspěšnou akcí; Test = bezplatný jednorázový běh; Log průběhu; Šablony. A/13504851193629
- **Limity: PROFESSIONAL 50 průběhů/měsíc, ULTIMATE 1000/měsíc**, dokupitelné balíčky; časový spouštěč odečte průběh **za každý vyhovující záznam**; max. **20 kroků** na automatizaci; po 3 chybách za sebou „Vynucené ukončení“; historie 12 měsíců; automatizace nemají historii změn. A/13505394647837, A/13807273975581, A/13690054035357
- Zapnutí: Nastavení » Rozšíření » Automatizace; admin má defaultně; jiným uživatelům právo uděluje admin (i když mají omezená oprávnění). A/13807273975581
- **Spouštěče**: vytvoření, vznik nebo editace, editace, smazání, **změna stavu** (OP/nabídka/objednávka), online podpis, uplynutí času (denní kontrola datového pole ± N dní v daný čas), vypršení evidence osobních údajů (GDPR), **manuální tlačítko** na kartě záznamu. Omezení iniciátorů: vybraní uživatelé / bezpečnostní profily / **povolit spouštění přes API** / zakázat řetězení z jiných automatizací. A/13511941393181
- **Podmínky**: na všechna základní i volitelná pole; při editaci hodnota před/po změně; operátory >,<,=, je/není, obsahuje, změněno/změněno na, je/není vyplněno; sady AND, mezi sadami OR; dynamické hodnoty z předchozích kroků. A/13583340127005
- **Akce**: vznik nového záznamu, **editovat záznam**, export systémové sestavy / vlastní šablony, přidat právní titul (GDPR), editovat adresu klienta, **načíst pole** ze záznamu (nepočítá se do průběhů), přidat produkt k OP, **odeslat webhook** (webhooky zakládá jen admin; klíč–hodnota), odeslat notifikaci, e-mailovou notifikaci, hromadný e-mail, **odeslat e-mail** (z Pošty uživatele s povolením; max. 20 kontaktů). A/13577638086045, A/29058733659933, A/29058748294941
- Automatizovat lze všechny typy záznamů kromě Produktů a Ceníků. A/13506822844957
- Validace: podmínka na pole, které nelze vyplnit při vytvoření (např. štítek), nikdy neprojde → použít spouštěč „editace“. A/13827690245661
- Automatizované e-maily: Professional/Ultimate/Enterprise; schránka musí mít Poštu a v Nastavení pošty » Automatizace povolené odesílání; podpis z Pošty. A/29058733659933
- **Proč se automatické úkoly neuzavírají** [odhad + logika z nápovědy]: Raynet nemá vestavěné „auto-uzavření“ úkolu; úkol uzavře jen řešitel („Mám hotovo“), hromadná změna, API, nebo vlastní automatizace s akcí „Editovat záznam“ (spouštěč např. změna stavu OP → podmínka → editovat navázaný úkol). Pokud automatizace/série OP/Hermes úkoly jen zakládá a nikdo je neuzavírá, hromadí se po termínu.

## 6. Hromadné akce, štítky, filtry, přehledy, nástěnky

- **Hromadná změna** (všechny seznamové pohledy): Editovat pole (i „vyčistit pole“), Změnit vlastníka (+ bezpečnostní úroveň navázaných záznamů), Přidat/odebrat štítky, Bezpečnostní úroveň, Zamknout/odemknout; **max. 200 záznamů najednou**; export max. 10 000; hromadné zneplatnění; hromadné vytvoření OP/aktivit. Povinná pole se při hromadné změně neuplatní. A/5926222392593, A/4414383755281
  → hromadné uzavření úkolů: seznam Aktivity » Úkoly » filtr (po termínu, automatické) » Editovat » pole Stav [odhad – že „Stav“ je mezi editovatelnými poli, ověřit v instanci].
- Editace jednotlivého pole přímo v seznamu (tužka). A/7017428624017
- **Štítky**: víc na záznam, filtr je/není/variabilní, hromadně přidat/odebrat, správa (přejmenovat/smazat) v Nastavení » Štítky. A/201631566
- **Pokročilý filtr**: chytré filtry, základní a další kritéria, volitelná pole; filtr i podle kritérií jiných záznamů (např. klienti bez otevřeného OP, klienti se schůzkou letos); ukládání, **sdílení (jen Administrátor a Na plný plyn)**, výchozí filtr, připnuté (rychlé) filtry, uložení i se sloupci. A/12588185768093, A/5883883874705
- Seznamové pohledy: sloupce, ABC filtr, souhrnné hodnoty v patičce, export XLSX. A/7017428624017
- **Nástěnka** (per uživatel): panely Moje výsledky, Výsledková tabule, Přehled aktivit, Vývoj prodeje, Srovnání výsledků, Prodejní trychtýř, Otevřené OP, Online uživatelé, Vzkazovník, Aktivní diskuze, Narozeniny a svátky, Oblíbené, Poznámka, Rychlé odkazy… Jen přednastavené panely (žádný vlastní report builder). A/201631346, A/12751477332765
- Obchodní nástěnka = Kanban OP (viz kap. 3); Nástěnka leadů (Kanban leadů). A/4432592312593, A/37833679946269
- **Historie změn záznamů** (ne v plánu START): Nastavení » Historie změn záznamů – filtr uživatel / typ změny / období. A/29058763730333

## 7. E-mail, kalendář, pozvánky

- **Pošta** (Professional/Ultimate/Enterprise): 1 schránka na uživatele (Gmail OAuth, Outlook OAuth, IMAP); max. 20 složek; import až 1 rok zpět (max. 5000 nejnovějších); nepřenáší spam, koncepty, sdílené složky; podpis HTML; blokované adresy/domény; plánované odeslání; zámeček = bezpečnostní úroveň e-mailu. A/21783670752157, A/21784189804701, A/21785994742429
- **Rejnetování**: automatické (shoda e-mailové adresy; více shod = nepřiřadí) vs. manuální (doporučeno kvůli citlivému obsahu); orejnetovaný e-mail **nelze z CRM smazat**; nechtěné e-maily držet v nesynchronizované složce. A/22692490275613
- **E-mailová asistentka** (`<ucet>@asistentka.raynet.cz`): BCC u odchozích, přeposlání jako příloha u příchozích; neznámý kontakt → **vznikne Lead**; kód OP v předmětu → přiřazení k OP; přenese jen z přihlašovací/alternativní adresy uživatele. A/202133198, A/201807123
- E-maily do CRM i přes **API**. A/21785994742429
- Šablony e-mailů: nápověda nepopisuje šablony pro běžné e-maily; pro automatizované e-maily jsou šablony v Automatizace » Šablony » Automatizované e-maily; marketingové šablony přes integrace (Ecomail, SmartEmailing, MailChimp…). A/29058748294941, A/203082165 [odhad: v editoru Pošty šablony nejsou zdokumentovány – ověřit v UI].
- **Google Calendar sync** (Můj profil » Google synchronizace): obousměrná, vybrané typy aktivit; v Googlu vznikne kalendář „Raynet CRM“; přenos od pondělí aktuálního týdne do +6 měsíců, max. 1000 starších aktivit. Z Googlu do Raynetu jen události v kalendáři „Raynet CRM“; vazba přes `-email-`/`-telefon-` v názvu, hosté = kontaktní osoby, kód OP `-OP-22-015-`, typ `-ukol-`, `-schuzka-`, `-telefonat-`, `-dopis-`; bez vazby = soukromá. **Zrušení v Raynetu = smazání v Google; realizace se v Google neprojeví; smazání v Google = smazání v Raynetu.** A/203015978
- Pozvánka na schůzku: jen ruční akce „Pozvat na schůzku e-mailem“ (všem účastníkům s e-mailem). A/115004799183
- Notifikace (Můj profil » Notifikace): přidělení úkolu, deadline, připomenutí, diskuze; kanály Raynet / e-mail / mobil / souhrnný e-mail. A/201836437

## 8. Textová pole, poznámky, přílohy, dokumenty

- Nápověda **nepopisuje schopnosti HTML editoru** (tabulky, `<pre>` apod.). Zmiňuje jen „lištu nástrojů“ pro formátování v Poznámce a „všechny potřebné nástroje pro formátování“ v editoru e-mailu. A/19353088910621, A/21785994742429 → empirické zjištění Evergreen (1. 10. 2026): `<table>` a `<pre>` se v `description`/`solution` aktivit odstraní.
- **Poznámky** (sticky notes) na kartě každého záznamu: formátovaný text, barva, náhledový obrázek, přílohy, řazení drag & drop. A/19353088910621
- **Přílohy**: ke všem záznamům kromě ceníků, **max. 50 MB/soubor**; soubor, odkaz www, Knihovna dokumentů, Google Drive, Dropbox; ZIP stažení. A/201827457
- **Diskuze**: interní vlákna k záznamu s účastníky a notifikacemi (alternativa k přeposílání e-mailů). A/201813613
- **RAYNET AI** (Professional+): v **Popisu** všech záznamů (kromě ceníků/produktů) a v záložce Základní u aktivit („otázky k projednání a výsledek aktivity“): Souhrn, Vylepšit, Korekce, Vytvořit e-mail/odpověď, Rozepsat do odstavců/bodů, Přeložit; na Časové ose klienta Shrnutí 360°, v čase, obchodování. Zpracování přes Microsoft (DPA). A/17929287156381
- Vlastní šablony exportovaných dokumentů (PDF/XLSX) pro OP aj. A/29058750617885

## 9. GDPR, oprávnění, bezpečnost

- **GDPR modul** (admin: Nastavení » Rozšíření): záložka GDPR na kartě **klienta – fyzické osoby**, kontaktní osoby a leadu; evidence **právních titulů** (souhlasy, plnění smlouvy…) s platností; automatizace: spouštěč „vypršení platnosti evidence osobních údajů“, akce „přidat právní titul“. A/360020541691, A/13511941393181, A/13577638086045
- **Anonymizace** (jen s GDPR modulem): nevratné přepsání osobních údajů (např. telefon → „999 999 999“), záznam a vazby zůstanou; jednotlivě (⋯ » GDPR modul » Anonymizace údajů) i hromadně (seznam KO » Editovat » Anonymizovat záznamy (GDPR)). Článek popisuje KO; u klienta-FO [k ověření]. A/4405243900177
- **Role**: Administrátor, Na plný plyn, S omezením, Jen ke čtení. A/202170568
- **Oprávnění uživatele** (Nastavení » Uživatelské účty » Oprávnění): viditelnost aktivit v kalendáři, měnit (cizí) záznamy, odemykat, **mazat** (vše/jen vlastní/typ), exportovat, Google sync kontaktů, hromadné změny, editace číselníků, zobrazení hodnot obchodních vztahů. A/201637926
- **Viditelnost záznamů**: vše / jen své / své + vybraných uživatelů. A/201791327
- **Bezpečnostní úrovně** (Professional+): výchozí „Sdílená“; vlastní úrovně s vybranými uživateli; výchozí úroveň per uživatel a typ záznamu; hromadně až 200; hloubková změna i navázaných záznamů. A/201637936, A/29058708250141
- **Zamknutí záznamu** (vlastník/admin; lze zakázat odemykání → kontrola nadřízeným). A/4420094451985
- Strom viditelnosti, bezpečnostní profily (vyšší plány). A/11820936124573, A/11852859808157
- Bezpečnost účtu: síla hesla, auto-odhlášení, 2FA, historie přihlášení 12 měsíců. A/36356845059997, A/360028450832

## 10. API, MCP, webhooky, limity plánů

- API dostupné od **PROFESSIONAL** (START ne). API klíč generuje admin (Nastavení » API klíče), lze vytvořit **integrační licenci** za sníženou cenu; klíč se zobrazí jen jednou. Limit klíčů: PROFESSIONAL 8, ULTIMATE 24. A/360032478072, A/115004813266, A/17187025395485
- **Webhooky**: Nastavení » Pro vývojáře » Webhook; PROFESSIONAL 8, ULTIMATE 24; v automatizacích akce „Odeslat webhook“. A/17286421005213, A/13577638086045
- **Tlačítka vlastních akcí**: Nastavení » Pro vývojáře; PROFESSIONAL 25, ULTIMATE 100. A/17286702209181
- **MCP server** (ve fázi testování): `https://app.raynet.cz/api/mcp`, Bearer MCP klíč per uživatel (Nastavení » MCP klíče; Čtení / Čtení a zápis), **limit 24 000 volání/den na účet**; dokumentace https://app.raynet.cz/api/doc/mcp/. A/38502554492573
- Automatizace lze povolit ke spuštění přes API (nastavení spouštěče). A/13511941393181

### 10.1 Ceník a limity plánů (https://raynet.cz/cena/, staženo 2026-10-01)
| | Start | Professional | Ultimate |
|---|---|---|---|
| cena / uživ. / měs. (roční platba) | 399 Kč | 799 Kč | 999 Kč |
| typy OP | 1 | 5 | bez omezení |
| vlastní pole | 5 | 100 | 500 |
| povinná pole | – | 25 | bez omezení |
| automatizace (průběhy/měs.) | – | 50 | 1000 |
| API volání/den | – | 24 000 | 48 000 |
| MCP volání/den | – | 24 000 | 24 000 |
| API / MCP klíče, webhooky | – | 8 / 8 / 8 | 24 / 24 / 24 |
| tlačítka vlastních akcí | – | 25 | 100 |
| exportní šablony | 1 | 25 | 100 |
Doplňky: automatizace Stavitel 3 000 průběhů za 1 000 Kč/měs., Architekt 10 000 za 1 500 Kč/měs.; Sandbox v Professional 5 000 Kč jednorázově (6 měsíců, bez příloh). A/33191266252061
Ultimate navíc: strom viditelnosti, SSO Entra ID, sandbox, 12 h konzultací/rok, dedikovaný account manager.

### 10.2 REST API v2 (https://app.raynet.cz/api/doc/, OpenAPI „RAYNET CRM API 2.0.0“, 276 cest; extrahováno do (lokální stažení, neverzováno) openapi.json)
- Base URL `https://app.raynet.cz/api/v2/`; autentizace Basic (uživatel + API klíč) + hlavička `X-Instance-Name` / `X-Instance-Id`, nebo `Authorization: Bearer` (token z `security/bearertoken`).
- **Limity**: 24 000 požadavků/den/instanci (UTC půlnoc), hlavičky `X-Ratelimit-*`, 429 při překročení; **max. 4 souběžná spojení na klienta**; 20 špatných přihlášení → blokace IP na 60 min. Stránkování max. 1000.
- Filtrování: `atribut[OPERATOR]=hodnota` (EQ, NE, LT, LE, GT, GE, LIKE, LIKE_NOCASE, IN, NOT_IN, EQ_OR_NULL, NE_OR_NULL); prázdný řetězec + EQ/NE = prázdné/neprázdné. `view=rowInfo` pro detekci změn. Optimistic lock `_version` přes API ignorován.
- **Klient FO přes API**: `PUT /company/` i `POST /company/{id}/` mají `person` (bool) + `firstName`, `lastName` (povinné při person=true), `titleBefore/After`, `salutation`, `birthday`. Filtr `GET /company/?person=true`. → **Převod 94 % „firem“ na FO jde přes REST API** (MCP to neumí: „this tool always creates a non-person (organization) company“; company_update pole `person` nemá).
- Klient: `state` (A_POTENTIAL, B_ACTUAL, C_DEFERRED, D_UNATTRACTIVE), `role` (A_SUBSCRIBER, B_PARTNER, C_SUPPLIER, D_RIVAL), `rating` A/B/C (povinné při založení), `contactSource` (společný číselník zdrojů pro OP, klienty a leady), `category`, `companyClassification1–3`, `customFields`, `tags`, `originLead`.
- **Sloučení**: `POST /company/{companyId}/merge/{sourceCompanyId}/` (zdroj se smaže), totéž `/person/.../merge/`, `/lead/.../merge/`. **Anonymizace**: `POST /company|person|lead/{id}/anonymize/`. Zneplatnění `/invalid`, obnovení `/valid`, zamknutí `/lock`.
- Kontaktní osoba `PUT /person/`: lastName povinné; `relationship` {company, type=pozice}; `keyman`; `privateAddress`; `customFields` jen v POST (update).
- **OP** `PUT /businessCase/` / `POST /businessCase/{id}/`: name, company (povinné), person, owner, `businessCasePhase`, `probability`, `totalAmount` (Konečná cena), `estimatedValue` (Předpokládané náklady), `validFrom`/`validTill`, `description` (Poznámka/Popis), `category`, **`source`** (Zdroj), klasifikace 1–3, `originalLead`, `tags`, `customFields`, `items`. V GET a filtrech navíc **`scheduledEnd`** (Odhad uzavření), **`losingCategory`** (číselník kategorií prohry, `PUT /losingCategory/`), **`losingReason`** (text), `status` (B_ACTIVE, E_WIN, F_LOST, G_STORNO), `businessCaseType`. V REST zápisovém schématu scheduledEnd/losing* nejsou uvedeny, MCP businessCase_update je ale zapisovat umí (viz 10.3).
- `GET /businessCase/{id}/phaseChanges` – historie změn stavů (doba ve fázi); `/participants/` – participanti OP; `/pdfExport`.
- `PUT /businessCasePhase/` – nový stav s `probability` (výchozí pravděpodobnost) a `businessCaseTypeId`.
- **Aktivity** (task, meeting, event, phoneCall, email, letter): `description` vs. `solution`:
  - Úkol: description = **Zadání úkolu**, solution = **Řešení úkolu**; `owner` = zadavatel, **`resolver` jen při založení (PUT)**; v POST (update) `resolver` chybí → řešitel se mění přes `participants` (role FROM = zadavatel, TO = řešitel). `status` NEW / SCHEDULED / COMPLETED / CANCELLED (jen v update), `deadline`, `completed`.
  - Schůzka: description = **Otázky k projednání**, solution = **Výsledek jednání**.
  - Telefonát: description = **K projednání**, solution = **Výsledek telefonátu**.
  - E-mail (`PUT /email/`): description = obsah e-mailu – jen evidence, ne odeslání; Dopis: description = obsah dopisu.
  - `customFields` jsou ve schématu jen u **update (POST)** aktivit, ne u založení (PUT).
  - `GET /activity/` – smíšený seznam; filtry status, deadline (u task), owner-id, businessCase, companyContextFilter, tags.
- **Volitelná pole přes API**: `GET /customField/config/` (label, dataType, groupName, **name = klíč** typu `Cislo_klie_cd702`, hint, readOnly, showIn*), `PUT /customField/config/{entityName}/` (založení; entity company, lead, person, businessCase, offer, salesOrder, product, project, task, email, event, letter, phoneCall, meeting), `POST .../{fieldName}/` úprava, `GET/PUT/POST/DELETE /customField/enum/{entity}/{field}/` položky roletky. Datové typy: STRING, FILE, TEXT, ENUMERATION, HYPERLINK, DATE, DATETIME, TIME, BIG_DECIMAL, MONETARY, PERCENT, BOOLEAN (= 12 typů z nápovědy). Hodnoty se zapisují v běžných API přes `customFields: {klíč: hodnota}`.
- Číselníky přes API: contactSource, companyCategory, businessCaseCategory, losingCategory, activityCategory, businessCaseClassification1–3, companyClassification1–3, personCategory… (PUT/POST/DELETE).
- Štítky `PUT/DELETE /{entity}/{id}/tag/`; Diskuze `PUT /{entity}/{id}/post/`; externí ID (až 10 na záznam, prefix `hermes:...`) `/{entity}/{id}/extId/` a `GET /{entity}/ext/{extId}/`.
- **Webhooky** `PUT /webhook/`: url, secretToken (hlavička `X-RAYNETCRM-Token`), events `record.created|updated|deleted`, entityFilter; payload = entityName + entityId + extIds + `source.name` (`user` browser/mobile, **`api` + název API klíče**, `system`); fronta s opakováním, 2 události/s, při nedostupnosti >7 dní se webhook smaže; technický kontakt.
- GDPR: `PUT /gdpr/` právní titul (gdprTemplate, company/person/lead, validFrom/Till, contractValidity), `GET /gdprTemplate/`.
- Pozvánky na schůzky: v API ani MCP žádný parametr pro odeslání pozvánky (fulltext „invit/pozván“ bez výsledku).
- Spec neobsahuje nic o HTML (sanitizaci) v textových polích.

### 10.3 MCP server (https://app.raynet.cz/api/doc/mcp/ – „MCP Tools Reference“, uloženo (lokální stažení, neverzováno) mcp-doc.txt)
- Nástroje: *_list/get/create/update pro company, person, lead (+ convert), businessCase, offer, salesOrder, project, task, meeting, event, phonecall; activity_list; analytické businessCase_* (pipeline, forecast, salesPerson…), activity_completedActivityAnalysis; rate_limit_status; user_info/configuration. **Žádné mazání, žádný e-mail/dopis, žádná konfigurace polí, žádné přílohy jako soubor (jen odkaz/složka DMS).**
- Zápis je dvoukrokový: náhled → `confirmToken` platný 60 s.
- **company_create vždy organizace** (FO nelze); company_create neumí štítky.
- **task_create/update**: `resolverPerson` (známá chyba v instanci evergreen – nefunguje, viz vault), `participants` při update **nahrazuje celý seznam**; status update přepíše `completed`; owner nelze změnit.
- **meeting_create nepřijímá `person`** – osobu jen přes participants; meetingPlace + adresa.
- **businessCase_create/update umí** `scheduledEnd`, `source`, `losingCategory`, `losingReason`, `businessCaseType/Phase`, `customFields`, `tags`, `highlighted`; při změně fáze bez `probability` se pravděpodobnost přepočte z výchozí hodnoty fáze; probability se zaokrouhluje na 5; tradingProfit = totalAmount − estimatedValue.
- customFields: klíče převzít z existujícího *_get (MCP nemá nástroj na konfiguraci polí).
- Resources: `raynet://codelists`, `raynet://codelist/{entity}` (např. contactSource, businessCaseType, activityCategory, losingCategory – ověřeno v MCP dokumentaci), `raynet://enumerations`.
- Limit 24 000 volání/den na účet (A/38502554492573). MCP klíč per uživatel (Čtení / Čtení a zápis).

## 11. GDPR – doplněk z blogu (https://raynet.cz/blog/gdpr-v-raynet-crm/)
- GDPR karta u: klient – fyzická osoba, kontaktní osoba, lead; přednastavené šablony právních titulů + vlastní; hromadná změna titulů; akce **Anonymizace**, **Export osobních údajů (.docx)**, **Export pro přenos (JSON)**.

## 12. Co nápověda NEŘEŠÍ / nenalezeno
- Schopnosti HTML editoru (tabulky, `<pre>`, nadpisy) – nedokumentováno.
- Důvody prohry v UI (dialog při Prohře, umístění číselníku) – nedokumentováno; existuje jen v API (losingCategory/losingReason).
- „Šablony aktivit“ a šablony běžných e-mailů v Poště – nedokumentováno.
- Zda povinná pole platí i pro zápisy přes API/MCP – nedokumentováno.
- Automatické uzavírání úkolů – žádná vestavěná funkce; jen ruční „Mám hotovo“, hromadná změna, API (status), automatizace „Editovat záznam“.

## 13. Návrhy pro Evergreen Finance (plná verze; zkrácená v reportu)

Pozn.: „A/<id>“ = https://support.raynetcrm.com/hc/cs/articles/<id>. [odhad] = můj úsudek, ne text nápovědy.

### (a) Nastavení Raynetu – podle přínosu
1. **Povinná pole podle fáze OP** (Nastavení » Nastavení evidence » Obchodní případ » Nastavení polí; A/4414383755281). Návrh [odhad]: od „Nabídnuto“ Zdroj (systémové `source`), Kategorie (typ úvěru), Odhad uzavření; od „Podaná žádost + EPP 2.0“ Producent (banka), výše úvěru; od „Schváleno“ sazba, fixace, LTV; při Prohře kategorie prohry (pokud lze označit povinnou). Limit Professional 25 povinných polí. Pracnost 1–2 h. Riziko: zda se vynucují i u API/MCP – ověřit; Hermes musí pole plnit tak jako tak.
2. **Číselník Kategorie prohry** (`losingCategory`) + text `losingReason` – nahradit „jiná“ 5–7 kategoriemi (bonita/DSTI, klient nereaguje, obešel nás / jiný poradce, změna záměru, nemovitost/odhad, sazba u konkurence, duplicitní/test). API `PUT /losingCategory/`, MCP businessCase_update.losingCategory. Pracnost 30 min.
3. **Pravděpodobnost u každé fáze** (Typy obchodu » Upravit nastavení; A/201738406) → vážený objem v Prodejním trychtýři (A/201623776); MCP přepočítá pravděpodobnost při změně fáze sám. 30 min.
4. **Povinný Follow-up u otevřených OP** omezený na fáze Identifikace → Schváleno (A/31763398123165) – každý otevřený OP má další krok; nahrazuje potřebu „automatických“ upomínek. 15 min.
5. **Vlastní pole OP – typy a obsah** (A/5276401814033): Producent (banka) = ENUMERATION; typ provize ENUMERATION; LTV PERCENT; sazba PERCENT; fixace ENUMERATION; splatnost BIG_DECIMAL (roky); účel ENUMERATION; pojištění BOOLEAN/ENUM; **nově Provize (MONETARY), Stav provize (ENUM), Datum výplaty (DATE), Výše úvěru (MONETARY)**; u všech zapnout seznam/filtr/export, nápověda (255 zn.). Rozhodnutí pro Adama: Konečná cena = provize (pak fungují Vývoj zisku/Ziskovost/Prodej dle obchodníků) vs. = výše úvěru [odhad: doporučuji provizi, objem do vlastního pole]. **Nepřejmenovávat pole, která plní web/appka podle názvu** (vault crm-raynet). Pracnost 2–3 h + migrace.
6. **Klienti – fyzické osoby**: příznak „Fyzická osoba“ (A/6370130507025) – převod přes REST API (`POST /company/{id}` person=true + jméno/příjmení); MCP to neumí. Zapnout **GDPR modul** (A/360020541691): právní tituly (plnění smlouvy/oprávněný zájem/souhlas) s platností, anonymizace, export osobních údajů. 0,5 dne + skript.
7. **Participanti na OP** (A/205141569) – spoludlužník, ručitel, makléř, tipař s barevnou kategorií; **Vztahy mezi klienty** (A/360016817971) – domácnost/rodina, firma klienta. 15 min.
8. **Kategorie aktivit** (A/206377235) – zredukovat; stavy schůzky (napevno/předběžně/nepotvrzeno) jsou vlastně stav, „soukromá aktivita“ duplikuje zatržítko Soukromá (které ale aktivitu neskrývá – A/4404457810705). [odhad] Pracnost 30 min.
9. **Sdílené uložené filtry + Nástěnka** (A/5883883874705, A/201631346): „Otevřené OP bez banky/zdroje/odhadu uzavření“, „OP bez naplánované aktivity“, „Úkoly po termínu“, „Prohry bez kategorie“, „Klienti FO bez GDPR titulu“. Panely Prodejní trychtýř, Otevřené OP, Přehled aktivit. Sdílet mohou jen Administrátor/Na plný plyn. 1 h.
10. **Automatizace** (A/13504851193629): Professional = jen 50 průběhů/měsíc → použít na málo a důležité (např. Prohra bez kategorie → notifikace vlastníkovi; Výhra → úkol „kontrola čerpání/výplaty provize“ za X dní). Větší objem: doplněk Stavitel (3 000 průběhů, 1 000 Kč/měs.) nebo logika v Hermesovi přes webhook `record.updated` (max. 8 webhooků). 2–4 h.
11. **Pozvánky na schůzky**: z UI „Pozvat na schůzku e-mailem“ (A/115004799183); pro Hermese [odhad] zakládat schůzky v Google kalendáři „Raynet CRM“ s hosty (Google pozve, sync do Raynetu naváže KO podle e-mailu hosta; A/203015978). Ověřit Meet odkaz a duplicitu.
12. **Pošta s manuálním rejnetováním** pro poradce (A/21783670752157, A/22692490275613) – e-maily klientů u případu; jinak e-mailová asistentka (BCC). Kód OP v předmětu → přiřazení k OP (A/202133198).
13. **Audit AI zápisů**: Historie změn záznamů (A/29058763730333), webhook `source=api` + název klíče, samostatná integrační licence / API klíč „Hermes“ (A/360032478072), externí ID `hermes:<id>`.
14. Typ obchodu „Provize“ uzavřít a zneplatnit (A/360001098963).

### (b) Pravidla pro AI zápisy (Hermes)
- Text do správného pole: zápis z hovoru/schůzky = `solution` (Výsledek telefonátu/jednání); agenda/co projednat = `description`; úkol: zadání = `description`, splnění = `solution`.
- Povolené HTML: `<p> <b> <i> <ul>/<ol>/<li> <br> <a>` (+ `style`); žádné tabulky/`<pre>` (empiricky). Struktura: 1 věta shrnutí → „Dohodnuto“ → „Další krok (kdo, do kdy)“ → „Podklady od klienta“; max. ~10 odrážek.
- „Karta případu“ = `description` OP (Popis), přepisovat celou, pevné sekce `<b>Stav:</b> … <br>`; ale **vše, co má pole, do pole** (fáze, banka, LTV, sazba, fixace, výše, zdroj, odhad uzavření, kategorie prohry).
- Před založením klienta deduplikace (`company_list` fulltext, filtr e-mailu `primaryAddress-contactInfo.email`). FO zakládat přes REST API (person=true), ne MCP.
- Úkoly: jeden souhrnný úkol na klienta/schůzku; řešitel přes participants (resolver v update nefunguje); termín reálný; po splnění `status=COMPLETED`; Hermes uzavírá své úkoly sám.
- Vazby: každá aktivita na `businessCase` + `company`; u schůzky osoba jen přes participants. Realizované hovory/schůzky zakládat se `completed` / status COMPLETED.
- `probability` nenastavovat (dopočítá se z fáze); `scheduledEnd` při každé změně fáze aktualizovat.
- Vlastní pole: klíče z `GET /customField/config/` nebo z *_get; u aktivit zapisovat až update.
- Štítek nebo vlastní pole „Zdroj zápisu: Hermes/Pocket“ + odkaz na nahrávku (HYPERLINK) [odhad].
- Limity: 24 000 API + 24 000 MCP/den, max. 4 souběžná spojení, MCP potvrzení do 60 s, 429 → backoff.
- Ověřovat zápis čtením (task_get / businessCase_get), odpověď „updated“ nestačí.

### (c) Úklid dat
1. Úkoly po termínu (113/144): najít zdroj „automatických“ úkolů (web egfin.cz zakládá úkol +1 den k leadu – vault; dále Historie spuštění automatizací, série OP); hromadně uzavřít/zrušit staré (seznam Úkoly → filtr → Hromadná změna, max. 200 – A/5926222392593; nebo API `status`). Pak změnit integraci webu (úkol jen když lead není zpracován, nebo uzavírat při konverzi leadu).
2. Testovací OP (~13) → smazat (jen bez vazeb) nebo zneplatnit (A/360020742511).
3. Duplicity klientů → Sloučit (A/360000822106; vyžaduje právo mazat; z A do B jen prázdná pole) nebo API merge.
4. FO příznak u ~94 % klientů → skript přes REST API (jméno/příjmení rozdělit z názvu; ověřit vzorek).
5. Doplnit banku/zdroj/odhad uzavření u 91 otevřených OP – Hermes navrhne z historie aktivit, poradce potvrdí v seznamu (inline editace, A/7017428624017).
6. Překlasifikovat 31 proher „jiná“ do nového číselníku.
7. Provize – zpětně doplnit u výher od 12/2025.
