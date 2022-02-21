#!/usr/bin/php
<?php
function printHelp() {
    echo "parse.php\n";
    echo "Skript typu filtr (parse.php v jazyce PHP 8.1) nacte ze standardniho vstupu zdrojovy kód v IPPcode22, zkontroluje lexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu\n\n";
    echo "Pouziti:\n";
    echo "   parse.php [--help]\n\n";
    echo "Argumenty:\n";
    echo "   --help - Vypise napovedu.\n\n";
    echo "Chybové návratové kódy:\n";
    echo "   21 - chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode22.\n";
    echo "   22 - neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n";
    echo "   23 - jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n";
}

// zpracovani argumentu

if ($argc == 1){ //zpracovani kodu
    while($f = fgets(STDIN)){
        echo "$f";
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
