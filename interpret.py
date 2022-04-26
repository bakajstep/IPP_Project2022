"""
Skript pro interpretaci jazyka IPP22

Author: Štěpán Bakaj - xbakaj00
"""

import sys
import xml.etree.ElementTree as ET
import re

"""
    Vytisk napovedy na stardartni vystup.
"""


def print_help():
    print("Program interpretuje kod v jazyku IPPcode22 zpracovany do XML formatu.")
    print("Pouziti:")
    print("python3.8 interpret.py --source=<source file> --input=<input_file> (alespon jeden z techto argumentu musi byt specifikovan)")
    print("--source=file  - vstupní soubor s XML reprezentací zdrojového kódu dle definice ze sekce")
    print("--input=file  - soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu")


"""
    Ukonceni programu s danym cybovym kodem a a zpravou na standartni chybovej vystup.

    :param code: chybovy kod
    :param message: obsah zpravy
"""


def exit_error(code, message):
    sys.stderr.write(message)
    exit(code)


def replace(match):
    return chr(int(match.group(1)))


"""
    Funkce pro najiti navesti v programu.

    :param list: List obsahujici instrukce
    :return: Slovnik obsahujici navesti a jeho poradi
"""


def find_labels(list):
    tmp_list = {}
    for i in list:
        if i.get("opcode").upper() == "LABEL":
            if i.find("arg1").get("type") != "label":
                exit_error(32, "Nevalidni hodnota v type!")
            name = i.find("arg1").text
            if name == "":
                exit_error(32, "Prazdny label!")
            if name in tmp_list:
                exit_error(52, "Duplicitni nazev navesti!")
            tmp_list[name] = int(i.get("order"))
    return tmp_list


"""
    Funkce pro ziskani hodnuty z promeny nebo z ramce.

    :param argument: Argumrnt instrukce
    :param dictionary_TF: Slovnik globalnich ramcu
    :param dictionary_GF: Slovnik docasnych ramcu
    :return: Hodnota ramce nebo promene
"""


def get_value(argument, dictionary_TF, dictionary_GF):
    if argument.get("type") == "var":
        if argument.text[:2] == "GF":
            if argument.text[3:] in dictionary_GF.keys():
                if dictionary_GF[argument.text[3:]] is not None:
                    return dictionary_GF[argument.text[3:]]
                else:
                    exit_error(56, "Neinicializovana promena!")
            else:
                exit_error(54, "Promena neexistuje!")

        if argument.text[:2] == "LF":
            if len(frame_stack) > 0:
                tmp = frame_stack.pop()
                if argument.text[3:] in tmp.keys():
                    if tmp[argument.text[3:]] is not None:
                        val = tmp[argument.text[3:]]
                        frame_stack.append(tmp)
                        return val
                    else:
                        exit_error(56, "Neinicializovana promena!")
                else:
                    exit_error(54, "Promena neexistuje!")
            else:
                exit_error(55, "Prazdnej zasobnik!")
        if argument.text[:2] == "TF":
            if is_TF_defined:
                if argument.text[3:] in dictionary_TF.keys():
                    if dictionary_TF[argument.text[3:]] is not None:
                        return dictionary_TF[argument.text[3:]]
                    else:
                        exit_error(56, "Neinicializovana promena!")
                else:
                    exit_error(54, "Promena neexistuje!")
            else:
                exit_error(55, "Promena neexistuje!")
    elif argument.get("type") == "int":
        try:
            value = int(argument.text)
        except ValueError:
            exit_error(32, "Spatne zadany int!")
        return value
    elif argument.get("type") == "bool":
        if argument.text == "true":
            return True
        else:
            return False
    elif argument.get("type") == "nil":
        return ""
    elif argument.get("type") == "string":
        if argument.text is None:
            return ""
        else:
            aux = str(argument.text)
            regex = re.compile(r"\\(\d{1,3})")
            new = regex.sub(replace, aux)
            return new
    else:
        exit_error(32, "Nevalidni hodnota v type!")


"""
    Funkce pro ulozeni hodnotu do ramce.

    :param frame: Ramec do ktereho ukladame
    :param value: Ukladana hodnota
"""


def store_to_frame(frame, value):
    if frame.get("type") != "var":
        exit_error(32, "Nevalidni hodnota v type!")
    var = frame.text
    if var[:2] == "GF":
        if var[3:] in dictionary_GF.keys():
            dictionary_GF[var[3:]] = value
        else:
            exit_error(54, "Promena nexistuje!")
    elif var[:2] == "TF":
        if is_TF_defined:
            if var[3:] in dictionary_TF.keys():
                dictionary_TF[var[3:]] = value
            else:
                exit_error(54, "Promena nexistuje!")
        else:
            exit_error(55, "Neexistuje ramec!")
    elif var[:2] == "LF":
        if len(frame_stack) > 0:
            tmp = frame_stack.pop()
            if var[3:] in tmp.keys():
                tmp[var[3:]] = value
                frame_stack.append(tmp)
            else:
                exit_error(54, "Promena neexistuje!")
        else:
            exit_error(55, "Prazdnej zasobnik!")


# soubory ze kterum cteme
input_file = ""
source_file = ""

# zpracovani argumetnu
if len(sys.argv) == 2:
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print_help()
        exit(0)
    elif sys.argv[1][:9] == "--source=":
        source_file = sys.argv[1][9:]
        input_file = sys.stdin
    elif sys.argv[1][:8] == "--input=":
        input_file = sys.argv[1][8:]
        source_file = sys.stdin
    else:
        exit_error(10, "Nevalidni parametr. Pro napovedu pouzijte --help.")
elif len(sys.argv) == 3:
    if sys.argv[1][:9] == "--source=":
        source_file = sys.argv[1][9:]
        if sys.argv[2][:8] == "--input=":
            input_file = sys.argv[2][8:]
        else:
            exit_error(10, "Nevalidni parametr. Pro napovedu pouzijte --help.")
    elif sys.argv[1][:8] == "--input=":
        input_file = sys.argv[1][7:]
        if sys.argv[2][:9] == "--source=":
            source_file = sys.argv[2][8:]
        else:
            exit_error(10, "Nevalidni parametr. Pro napovedu pouzijte --help.")
    else:
        exit_error(10, "Nevalidni parametr. Pro napovedu pouzijte --help.")
else:
    exit_error(10, "Saptny pocet parametru. Pro napovedu pouzijte --help.")

# otevreni souboru
try:
    xmlTree = ET.ElementTree(file=source_file)
except OSError:
    exit_error(11, "Chyba pri otevirani souboru!")
except ET.ParseError:
    exit_error(31, "Chybny syntax u XML.")

root = xmlTree.getroot()

# kontrola korenoveho tagu
if root.tag != "program":
    exit_error(32, "Soubor neobsahuje program!")

# kontrola hlavicky
if root.items()[0] != ('language', 'IPPcode22'):
    exit_error(32, "Spatny jazyk!")

if len(root.keys()) == 2:
    if (root.keys()[1] != "name") and (root.keys()[1] != "description"):
        exit_error(32, "Neocekavana struktura XML!")

if len(root.keys()) == 3:
    if (not ("name" in root.keys())) or (not ("description" in root.keys())):
        exit_error(32, "Neocekavana struktura XML!")

if len(root.keys()) > 3:
    exit_error(32, "Neocekavana struktura XML!")

# rozsekani jednotlivych instrukci do listu
list_of_instructions = root.findall("./")

# list pro kontrolu duplicitnich orderu a vykonani vysledneho programu po serazeni
list_of_orders = []

# kontrola zda mame dobre xml instrukce
for i in list_of_instructions:
    if i.tag != "instruction":
        exit_error(32, "Znacka neni instrukce!")
    if i.keys() != ['order', 'opcode']:
        exit_error(32, "Nevalidni klic u instrukce!")
    order = i.get("order")
    if order.isnumeric() is False or int(order) <= 0 or order in list_of_orders:
        exit_error(32, "Nevalidni hodnota v orderu!")
    children = list(i)
    for j in children:
        if not re.match("^arg[123]$", j.tag):
            exit_error(32, "Spatna znacka argumentu!")
    list_of_orders.append(order)

# serazeni aby se vykonavali ve spravnem poradi
list_of_orders.sort(key=int)

# slovnik pro kontrolu navsteni
dictionary_of_labels = find_labels(list_of_instructions)

# slovnik instrukci
dictionary_of_instructions = {}

for i in list_of_instructions:
    dictionary_of_instructions[i.get("order")] = i

# podle promeny budeme vykounavat instrukce, bud ji zvysime o jedna nebo skocime na danou instrukci
iterater = 0

# slovniky promenych a zasobniky
dictionary_TF = {}
dictionary_GF = {}
frame_stack = []
data_stack = []
call_stack = []

# ukazatel zda mame docasny ramec
is_TF_defined = False

# cyklus kdy iterujeme pres seznam instrukci
while iterater < len(list_of_instructions):
    order = list_of_orders[iterater]
    instruction = dictionary_of_instructions[order]
    if instruction.tail.strip() != "":
        exit_error(32, "Nevalidni XML!")
    opcode = instruction.get("opcode").upper()
    # ---------------------------------------------- Instrukce MOVE ---------------------------------------------------
    if opcode == "MOVE":
        if instruction.find("arg1") is not None and instruction.find("arg2") is not None:
            if instruction.find("arg2").get("type") == "nil":
                value = "nil"
            else:
                value = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(32, "Nevalidni struktura argumentu!")
    # ---------------------------------------------- Instrukce CREATFRAME ---------------------------------------------
    elif opcode == "CREATEFRAME":
        dictionary_TF = {}
        is_TF_defined = True
    # ---------------------------------------------- Instrukce PUSHFRAME ----------------------------------------------
    elif opcode == "PUSHFRAME":
        if is_TF_defined:
            frame_stack.append(dictionary_TF)
            is_TF_defined = False
        else:
            exit_error(55, "Pristup nedefinovanemu ramci!")
    # ---------------------------------------------- Instrukce POPFRAME -----------------------------------------------
    elif opcode == "POPFRAME":
        if len(frame_stack) > 0:
            dictionary_TF = frame_stack.pop()
            is_TF_defined = True
        else:
            exit_error(55, "Zasobnik je prazdny!")
    # ---------------------------------------------- Instrukce DEFVAR -------------------------------------------------
    elif opcode == "DEFVAR":
        if instruction.find("arg1") is not None:
            var = instruction.find("arg1").text
            if var[:2] == "GF":
                if var[3:] not in dictionary_GF:
                    dictionary_GF[var[3:]] = None
                else:
                    exit_error(52, "Promena jiz existuje!")
            if var[:2] == "TF":
                if is_TF_defined:
                    if var[3:] not in dictionary_TF.keys():
                        dictionary_TF[var[3:]] = None
                    else:
                        exit_error(54, "Ramec existuje")
                else:
                    exit_error(55, "Promena neexistuje!")
            if var[:2] == "LF":
                if len(frame_stack) > 0:
                    tmp = frame_stack.pop()
                    if var[3:] not in tmp.keys():
                        tmp[var[3:]] = None
                        frame_stack.append(tmp)
                    else:
                        exit_error(54, "Ramec existuje")
                else:
                    exit_error(55, "Neexistuje slovnik!")
        else:
            exit_error(32, "Nevalidni struktura argumentu!")
    # ---------------------------------------------- Instrukce CALL ---------------------------------------------------
    elif opcode == "CALL":
        label = instruction.find("arg1").text
        call_stack.append(iterater + 1)
        if label in dictionary_of_labels.keys():
            iterater = list_of_orders.index(str(dictionary_of_labels[label]))
        else:
            exit_error(52, "Nedefinovane navesti!")
    # ---------------------------------------------- Instrukce RETURN -------------------------------------------------
    elif opcode == "RETURN":
        if len(call_stack) > 0:
            iterater = call_stack.pop()
            continue
        else:
            exit_error(56, "Prazdny zasobnik skoku!")
    # ---------------------------------------------- Instrukce PUSHS --------------------------------------------------
    elif opcode == "PUSHS":
        symb1 = get_value(instruction.find("arg1"), dictionary_TF, dictionary_GF)
        data_stack.append(symb1)
    # ---------------------------------------------- Instrukce POPS ---------------------------------------------------
    elif opcode == "POPS":
        if len(data_stack) > 0:
            value = data_stack.pop()
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(56, "Zasobnik je prazdny!")
    # ---------------------------------------------- Instrukce ADD ----------------------------------------------------
    elif opcode == "ADD":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if isinstance(symb1, bool) or isinstance(symb2, bool):
            exit_error(53, "Hodnoty nejsou cela cisla!")
        if isinstance(symb1, int) and isinstance(symb2, int):
            value = int(symb1) + int(symb2)
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(53, "Hodnoty nejsou cela cisla!")
    # ---------------------------------------------- Instrukce SUB ----------------------------------------------------
    elif opcode == "SUB":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if isinstance(symb1, bool) or isinstance(symb2, bool):
            exit_error(53, "Hodnoty nejsou cela cisla!")
        if isinstance(symb1, int) and isinstance(symb2, int):
            vysl = int(symb1) - int(symb2)
            store_to_frame(instruction.find("arg1"), vysl)
        else:
            exit_error(53, "Hodnoty nejsou cela cisla!")
    # ---------------------------------------------- Instrukce MUL ----------------------------------------------------
    elif opcode == "MUL":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if isinstance(symb1, bool) or isinstance(symb2, bool):
            exit_error(53, "Hodnoty nejsou cela cisla!")
        if isinstance(symb1, int) and isinstance(symb2, int):
            vysl = int(symb1) * int(symb2)
            store_to_frame(instruction.find("arg1"), vysl)
        else:
            exit_error(53, "Hodnoty nejsou cela cisla!")
    # ---------------------------------------------- Instrukce IDIV ---------------------------------------------------
    elif opcode == "IDIV":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if isinstance(symb1, bool) or isinstance(symb2, bool):
            exit_error(53, "Hodnoty nejsou cela cisla!")
        if isinstance(symb1, int) and isinstance(symb2, int):
            # kontrola deleni nulou
            if int(symb2) == 0:
                exit_error(57, "Deleni nulou!")
            vysl = int(int(symb1) // int(symb2))
            store_to_frame(instruction.find("arg1"), vysl)
        else:
            exit_error(53, "Hodnoty nejsou cela cisla!")
    # ---------------------------------------------- Instrukce LT -----------------------------------------------------
    elif opcode == "LT":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if isinstance(symb1, int) and isinstance(symb2, int):
            vysl = int(symb1) < int(symb2)
            store_to_frame(instruction.find("arg1"), vysl)
        elif (symb1 is True or symb1 is False) and (symb2 is True or symb2 is False):
            if symb1 is False and symb2 is True:
                store_to_frame(instruction.find("arg1"), "True")
            else:
                store_to_frame(instruction.find("arg1"), "False")
        elif isinstance(symb1, str) and isinstance(symb2, str):
            vysl = symb1 < symb2
            store_to_frame(instruction.find("arg1"), vysl)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce GT -----------------------------------------------------
    elif opcode == "GT":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if isinstance(symb1, int) and isinstance(symb2, int):
            vysl = int(symb1) > int(symb2)
            store_to_frame(instruction.find("arg1"), vysl)
        elif (symb1 is True or symb1 is False) and (symb2 is True or symb2 is False):
            if symb1 is True and symb2 is False:
                store_to_frame(instruction.find("arg1"), "True")
            else:
                store_to_frame(instruction.find("arg1"), "False")
        elif isinstance(symb1, str) and isinstance(symb2, str):
            vysl = symb1 > symb2
            store_to_frame(instruction.find("arg1"), vysl)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce EQ -----------------------------------------------------
    elif opcode == "EQ":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if symb1 == "nil" or symb2 == "nil":
            vysl = symb1 == symb2
            store_to_frame(instruction.find("arg1"), vysl)
        elif isinstance(symb1, int) and isinstance(symb2, int) and not (
                isinstance(symb1, bool) or isinstance(symb2, bool)):
            vysl = int(symb1) == int(symb2)
            store_to_frame(instruction.find("arg1"), vysl)
        elif (symb1 is True or symb1 is False) and (symb2 is True or symb2 is False):
            if (symb1 is False and symb2 is False) or (symb1 is True and symb2 is True):
                store_to_frame(instruction.find("arg1"), True)
            else:
                store_to_frame(instruction.find("arg1"), False)
        elif isinstance(symb1, str) and isinstance(symb2, str):
            vysl = symb1 == symb2
            store_to_frame(instruction.find("arg1"), vysl)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce AND ----------------------------------------------------
    elif opcode == "AND":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if (symb1 is True or symb1 is False) and (symb2 is True or symb2 is False):
            value = symb1 and symb2
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce OR -----------------------------------------------------
    elif opcode == "OR":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if (symb1 is True or symb1 is False) and (symb2 is True or symb2 is False):
            value = symb1 or symb2
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce NOT ----------------------------------------------------
    elif opcode == "NOT":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou shodneho typu
        if symb1 is True or symb1 is False:
            value = not symb1
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce INT2CHAR -----------------------------------------------
    elif opcode == "INT2CHAR":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        if isinstance(symb1, int):
            if 0 <= symb1 <= 11141111:
                value = chr(symb1)
                store_to_frame(instruction.find("arg1"), value)
            else:
                exit_error(58, "Nevalidni hodnota!")
        else:
            exit_error(53, "Hodnota neni kompatibilni")
    # ---------------------------------------------- Instrukce STRI2INT -----------------------------------------------
    elif opcode == "STRI2INT":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola validnich vstupu
        if isinstance(symb1, str) and isinstance(symb2, int):
            if len(symb1) > symb2:
                value = ord(symb1[symb2])
                store_to_frame(instruction.find("arg1"), value)
            else:
                exit_error(58, "Index je mimo retezec!")
        else:
            exit_error(53, "Hodnota neni kompatibilni")
    # ---------------------------------------------- Instrukce READ ---------------------------------------------------
    elif opcode == "READ":
        type = instruction.find("arg2")
        if type.get("type") != "type":
            exit_error(32, "Nevalidni hodnota v type!")
        type = type.text
        # precteni vstupu
        try:
            line = input_file.readline().strip()
        except OSError:
            line = None

        if line is None:
            store_to_frame(instruction.find("arg1"), "nil")
        elif type == "int":
            try:
                line = int(line)
            except ValueError:
                line = "nil"
            store_to_frame(instruction.find("arg1"), line)
        elif type == "bool":
            if str(line).lower() == "true":
                store_to_frame(instruction.find("arg1"), "true")
            elif str(line).lower() == "false" or str(line).lower() != "":
                store_to_frame(instruction.find("arg1"), "false")
            else:
                store_to_frame(instruction.find("arg1"), "nil")
        elif type == "string":
            if isinstance(line, str):
                store_to_frame(instruction.find("arg1"), line)
            else:
                exit_error(58, "Nebylo nacteno cele cislo!")
        else:
            exit_error(32, "Nevalidni typ!")
    # ---------------------------------------------- Instrukce WRITE --------------------------------------------------
    elif opcode == "WRITE":
        value = get_value(instruction.find("arg1"), dictionary_TF, dictionary_GF)
        if value is True or value == "True":
            print("true", end='')
        elif value is False or value == "False":
            print("false", end='')
        elif value == "nyl":  # pro vypis u type
            print("nil", end='')
        elif value == "nil":
            print("", end='')
        else:
            print(value, end='')
    # ---------------------------------------------- Instrukce CONTAC -------------------------------------------------
    elif opcode == "CONCAT":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboly jsou retezce
        if isinstance(symb1, str) and isinstance(symb2, str):
            value = symb1 + symb2
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce STRLEN -------------------------------------------------
    elif opcode == "STRLEN":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        # kontrola zda oba dva symboli jsou retezce
        if isinstance(symb1, str):
            value = len(symb1)
            store_to_frame(instruction.find("arg1"), value)
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce GETCHAR ------------------------------------------------
    elif opcode == "GETCHAR":
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda je prvni retezec a druhy cely cislo
        if isinstance(symb1, str) and isinstance(symb2, int):
            if len(symb1) > symb2:
                value = symb1[symb2]
                store_to_frame(instruction.find("arg1"), value)
            else:
                exit_error(58, "Index mimo retezec!")
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce SETCHAR ------------------------------------------------
    elif opcode == "SETCHAR":
        variable = get_value(instruction.find("arg1"), dictionary_TF, dictionary_GF)
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        # kontrola zda je prvni retezec a druhy cely cislo
        if isinstance(variable, str) and isinstance(symb1, int) and isinstance(symb2, str):
            if len(variable) > symb1 and symb2 != "":
                value = variable[:symb1] + symb2[0] + variable[symb1 + 1:]
                store_to_frame(instruction.find("arg1"), value)
            else:
                exit_error(58, "Index mimo retezec!")
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
    # ---------------------------------------------- Instrukce TYPE ---------------------------------------------------
    elif opcode == "TYPE":
        try:
            symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        except SystemExit:
            store_to_frame(instruction.find("arg1"), "")
            iterater += 1
            continue
        if symb1 == "nil":
            store_to_frame(instruction.find("arg1"), "nyl")
        elif isinstance(symb1, str):
            store_to_frame(instruction.find("arg1"), "string")
        elif isinstance(symb1, bool):
            store_to_frame(instruction.find("arg1"), "bool")
        elif isinstance(symb1, int):
            store_to_frame(instruction.find("arg1"), "int")
    # ---------------------------------------------- Instrukce LABEL --------------------------------------------------
    elif opcode == "LABEL":
        iterater += 1
        continue
    # ---------------------------------------------- Instrukce JUMP ---------------------------------------------------
    elif opcode == "JUMP":
        label = instruction.find("arg1").text
        if label in dictionary_of_labels.keys():
            iterater = list_of_orders.index(str(dictionary_of_labels[label]))
        else:
            exit_error(52, "Nedefinovane navesti!")
    # ---------------------------------------------- Instrukce JUMPIFEQ -----------------------------------------------
    elif opcode == "JUMPIFEQ":
        label = instruction.find("arg1").text
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        vysl = False
        if symb1 == "nil" or symb2 == "nil":
            vysl = symb1 == symb2
        elif isinstance(symb1, int) and isinstance(symb2, int) and not (
                isinstance(symb1, bool) or isinstance(symb2, bool)):
            vysl = int(symb1) == int(symb2)
        elif (symb1 is True or symb1 is False) and (symb2 is True or symb2 is False):
            if (symb1 is False and symb2 is False) or (symb1 is True and symb2 is True):
                vysl = True
            else:
                vysl = False
        elif isinstance(symb1, str) and isinstance(symb2, str):
            vysl = symb1 == symb2
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
        # skok
        if vysl is True:
            if label in dictionary_of_labels.keys():
                iterater = list_of_orders.index(str(dictionary_of_labels[label]))
            else:
                exit_error(52, "Nedefinovane navesti!")
    # ---------------------------------------------- Instrukce JUMPIFNEQ ----------------------------------------------
    elif opcode == "JUMPIFNEQ":
        label = instruction.find("arg1").text
        symb1 = get_value(instruction.find("arg2"), dictionary_TF, dictionary_GF)
        symb2 = get_value(instruction.find("arg3"), dictionary_TF, dictionary_GF)
        vysl = False
        if symb1 == "nil" or symb2 == "nil":
            vysl = symb1 != symb2
        elif isinstance(symb1, int) and isinstance(symb2, int) and not (
                isinstance(symb1, bool) or isinstance(symb2, bool)):
            vysl = int(symb1) != int(symb2)
        elif (symb1 is True or symb1 is False) and (symb2 is True or symb2 is False):
            if (symb1 is False and symb2 is False) or (symb1 is True and symb2 is True):
                vysl = False
            else:
                vysl = True
        elif isinstance(symb1, str) and isinstance(symb2, str):
            vysl = symb1 != symb2
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni")
        # skok
        if vysl is True:
            if label in dictionary_of_labels.keys():
                iterater = list_of_orders.index(str(dictionary_of_labels[label]))
            else:
                exit_error(52, "Nedefinovane navesti!")
    # ---------------------------------------------- Instrukce EXIT ---------------------------------------------------
    elif opcode == "EXIT":
        symb1 = get_value(instruction.find("arg1"), dictionary_TF, dictionary_GF)
        if isinstance(symb1, int):
            if 0 <= int(symb1) <= 49:
                exit(int(symb1))
            else:
                exit_error(57, "Nevalidni rozsah!")
        else:
            exit_error(53, "Hodnoty nejsou kompatibilni!")
    # ---------------------------------------------- Instrukce DPRINT -------------------------------------------------
    elif opcode == "DPRINT":
        value = get_value(instruction.find("arg1"), dictionary_TF, dictionary_GF)
        if value is True or value == "True":
            sys.stderr.write("true")
        elif value is False or value == "False":
            sys.stderr.write("false")
        elif value == "nil":
            sys.stderr.write("")
        else:
            sys.stderr.write(value)
    # ---------------------------------------------- Instrukce BREAK --------------------------------------------------
    elif opcode == "BREAK":
        sys.stderr.write("Pozice v kodu: " + str(iterater) + "\n")
        sys.stderr.write("Slovnik GF:\n")
        sys.stderr.write(str(dictionary_GF) + "\n")
        sys.stderr.write("Slovnik TF:\n")
        sys.stderr.write(str(dictionary_TF) + "\n")
        sys.stderr.write("Slovnik LF:\n")
    else:
        exit_error(32, "Neznama instrukce!")
    iterater += 1
