Implementační dokumentace k 2. úloze do IPP 2021/2022


Jméno a příjmení: Štěpán Bakaj


Login: xbakaj00


## Interpret.py


Cílem projektu bylo vytvořit skript v jazyce Python, který má za úkol interpretovat imperativní jazyk IPPCode22. Musí umožnit načíst soubor obsahující XML strukturu ze standardního vstupu nebo ze souboru a vstupní data programu pro případnou instrukci READ. Kdy musí být, aspoň jeden ze souboru předán argumentem programu. Výstup programu tiskne na standardní výstup a končí příslušným návratovým kódem.
### Implementace
Skript začíná zpracováním argumentu, kde mohou nastat čtyři stavy. První z možností je, že uživatel bude chtít vypsat nápovědu, a to docílí pomocí přepínače --help. Další tři možnosti se týkají vstupních dat. Podle počtů argumentů se kontroluje, zda byl zadán jeden nebo dva přepínače, které se ukládají do proměnných input_file a source_file. Pokud uživatel zadá nevalidní argument(y), skript se ukončí s příslušným chybovým kódem.


Na práci s XML souborem se využívá knihovna xml.etrrr.ElementTree. Po načtení XML souboru probíhá kontrola jeho hlavičky. Následně se v cyklu projedou všechny instrukce, kde se zkontroluje order a argumenty instrukce. Zároveň se ukládá order do seznamu a následně se seřadí, aby se instrukce vykonávaly ve správném pořadí. Seznam instrukcí se převede do slovníku pro budoucí pohodlnější prací, kde jako klíč slouží order a na dané pozici je uložena instrukce. Dále se vytvoří slovník návěští pomocí pomocné funkce find_labels.


Dále skript pokračuje cyklem, ve kterém se iteruje pomocí proměnné iterater, která se vždy na konci zvětší o jedna, dokud nebude větší jako velikost seznamu instrukcí. Pomocí hodnoty v proměnné iterator se získá aktuální order a následně instrukce, která se bude vykonávat. Následuje velký if else blok, kde se zpracovávají instrukce nebo se vyhodnotí, že danou instrukci program nepodporuje a ukončí se s příslušným chybovým kódem. Instrukce se zpracovávají dle daného významu podle zadání, pro zjednodušení používají funkce na uložení do rámce(store_to_frame) a získání hodnoty z argumentu(get_value).


### Pomocné funkce

### find_labels(list)

Funkce iteruje  listem instrukcí (parametr funkce), dokud nenarazí na instrukci LABEL, kde zkontroluje, zda argument obsahuje správný typ a zda se již daný návěští nevyskytuje ve slovníku. Vrací slovník, kde jako klíč slouží název návěští a je pod ním uložena hodnota order.

### get_value(argument, dictionary_TF, dictionary_GF)

Funkce v parametru dostává argument, ze kterého chce získat hodnotu a slovníky ve kterých hledá danou hodnotu. Rozlišují se dva stavy. Buď hledá ve slovnících, na zásobníku s rámci nebo dostane proměnou. Pokud funkce dostane číst z rámec, zjistí, o který se jedná a podle toho se snaží z něj číst. Pokud se jedná o dočasný nebo globální rámec, čtení funguje stejně. Nejprve se zeptá, zda vůbec rámec s daným jménem existuje a poté jestli je definovaný. Až poté přečte hodnotu a vrátí ji volajícímu. Jedná-li se o lokální rámec, který je uložený v zásobníku, proběhne kontrola, zda není zásobník prázdný, poté vyjme vrchní slovník rámců, zkontroluje, zda daný rámec existuje a zda je definovaný. Přečte hodnotu rámce a slovník uloží zpátky na zásobník. Následně vrátí hodnotu volajícímu. Pokud se jedná o proměnou zkontroluje, kterého typu nabývá (int, bool, string a nil) a vrátí danou hodnotu volajícímu.

### store_to_frame(frame, value)

Funkce dostane v parametrech argument, do kterého se ukládá. Hodnotu, která má být uložena. Na začátku probíhá kontrola, zda se vůbec v argumentu nachází rámec, do kterého by měla být hodnota uložena. Poté se rozlišuje, zda se jedná o globální a dočasný rámec nebo lokální rámec. Pokud se jedná o globální a dočasný rámec. Zkontroluje se, zda je rámec definovaný a teprve poté se do něj uloží hodnota. Pokud se jedná o lokální rámec, zkontroluje se, zda není prázdný zásobník slovníků. Přečte se hodnota z vrchu zásobníku, zkontroluje se, zda je rámec definovaný, uloží se hodnota a vrátí se zpátky do zásobníku.

