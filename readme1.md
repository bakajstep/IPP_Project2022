## Implementační dokumentace k 1. úloze do IPP 2021/2022

Jméno a příjmení: Štěpán Bakaj

Login: xbakaj00


## OOP
V projektu jsem se pokusil o "objektově orientovaný návrh". Při přemýšlení, jaký návrhový vzor použít, jsem vyhodnotil, že nejlepší pro toto řešení bude tovární metoda, kde bude jedna "továrna", která bude generovat instance třídy Command. Samotná instance třídy Command pak představuje jeden příkaz kódu IPPcode22. Jelikož by zapouzdřující třída měla málo funkcionality, tak jsem jí vynechal a samotnou "továrnu" tvoří skript. Proto jsem asi nesplnil rozšíření NVP a tak jsem ho ani neuváděl.

## Popis skriptu
Na začátku skriptu vidíme kontrolu argumentu, kde program můžeme spustit dvěma způsoby. První je s argumentem "--help". Poté nám program vypíše na standartní výstup nápovědu a chybové návratové kódy. Druhý způsob je bez argumentu a na standartní vstup přesměrujeme soubor s programem v jazyku IPPcode22. Vše jiné chápeme jako chybu a program ukončíme. Pokud vše proběhne v pořádku, začínáme číst soubor. Čteme po řádku a vždy kontrolujeme, zda řádek neobsahuje komentář. Když ano, tak ho odsekneme. Poté se zbavíme bílých znaků na začátku a konci řetězce pomocí metody trim. Nyní máme připravený řetězec pro zavolání třídy Command, ale prvně musíme ještě zkontrolovat, zda není řetězec prázdný (prázdný řádek, komentář na řádku). Pokud se zavolá konstruktor, tak nám řetězec rozdělí do pole a zvýší statickou proměnnou count, ve které uchováváme pořadí instrukce. Poté zavoláme metodu checkCorrectness, která zkontroluje, zda se jedná o validní příkaz, a vygeneruje výsledný XML soubor pomocí knihovny DOM. Správnost příkazu kontrolujeme pomocí automatu – zda máme korektní instrukci a správný počet parametru. Její argumenty již kontrolujeme pomocí regulárních výrazů. Pokud něco z toho selže, ukončíme program s příslušným chybovým návratovým kódem.
