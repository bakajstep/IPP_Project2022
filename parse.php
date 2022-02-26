#!/usr/bin/php
<?php

function printHelp() {
    echo "parse.php\n";
    echo "Skript typu filtr (parse.php v jazyce PHP 8.1) nacte ze standardniho vstupu zdrojovy kód v IPPcode22, zkontroluje lexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu\n\n";
    echo "Pouziti:\n";
    echo "   php8.1 parse.php [--help]\n\n";
    echo "Argumenty:\n";
    echo "   --help     Vypise napovedu.\n\n";
    echo "Chybové návratové kódy:\n";
    echo "   21         Chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode22.\n";
    echo "   22         Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n";
    echo "   23         Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n";
}

// zpracovani argumentu

if ($argc == 1){ //zpracovani kodu
    while($line = fgets(STDIN)){
        if (str_contains($line, "#") == true){  //zbaveni se komentare
            $line = substr($line, 0, strpos($line, "#"));
        }
        $line = trim($line); //zbaveni se bilych znaku na zacatku a nokonci retezce
        if (!empty($line)){ // kontrola zda nedostavame prazdny retezec
            $command = new Comand($line);
            $command->checkCorrectness();
        }
    }
}else if ($argc == 2){ // napoveda
    if (strcmp($argv[1],"--help") == 0){
        printHelp();
    }else{
        fwrite(STDERR, "Neznamy parametr!\n");
        exit(10);
    }
}else{ // spatne zadany parametry
    fwrite(STDERR, "Nevalidni zadani paratmetru!\n");
    exit(10);
}
exit(0);


class Comand{

    static int $count = 0;
    private $array;

    function __construct($string) {
        self::$count++;
        $this->array = preg_split('/\s+/',$string);
        $this->array[0] = strtolower($this->array[0]);
        print_r($this->array);
    }

    private function checkVar($string){
        return preg_match('((?:GF|LF|TF)@' . '(?:[[:alpha:]' . '_\-\$&%\*!\?' . '][[:alnum:]' . '_\-\$&%\*!\?'. ']*)'. ')',$string);
    }

    private function checkLabel($string){

    }

    function checkCorrectness() {
        if (self::$count == 1) {
            if (strcmp($this->array[0],".ippcode22") != 0) {
                fwrite(STDERR, "Chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode22.\n");
                exit(21);
            }
        }else {
            switch ($this->array[0]) {
                case "move":

                    break;
                case "creatframe":

                    break;
                case "pushframe":

                    break;
                case "popframe":

                    break;
                case "defvar":

                    break;
                case "call":

                    break;
                case "return":

                    break;
                case "push":

                    break;
                case "pops":

                    break;
                case "add":

                    break;
                case "sub":

                    break;
                case "mul":

                    break;
                case "idiv":

                    break;
                case "lt":

                    break;
                case "gt":

                    break;
                case "eq":

                    break;
                case "and":

                    break;
                case "or":

                    break;
                case "not":

                    break;
                case "int2char":

                    break;
                case "string2int":

                    break;
                case "read":

                    break;
                case "write":

                    break;
                case "concat":

                    break;
                case "strlen":

                    break;
                case "getchar":

                    break;
                case "setchar":

                    break;
                case "type":

                    break;
                case "label":

                    break;
                case "jump":

                    break;
                case "jumpifeq":

                    break;
                case "jumpifneq":

                    break;
                case "exit":

                    break;
                case "dprint":

                    break;
                case "break":

                    break;
                default:
                    fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                    exit(22);
            }
        }
    }
}
