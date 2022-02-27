<?php
ini_set('display_errors', 'stderr');
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
    $command->pritnXML();
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

    static int $count = -1;
    private static $dom;
    private static $program;
    private $array;

    function __construct($string) {
        self::$count++;
        $this->array = preg_split('/\s+/',$string);
        $this->array[0] = strtoupper($this->array[0]);
        //print_r($this->array); TODO
    }

    private function checkVar($string){
        return preg_match("/(LF|GF|TF)@([a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*)/",$string);
    }

    private function checkConst($string){
        return preg_match("/(int@-{0,1}[0-9]*)|(nil@nil)|(bool@(true|false)|(string@[a-zA-Z_\-$&%*!?0-9]*[\\00-30-2]*))/",$string);
    }

    private function checkLabel($string){
        return preg_match("/[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*/",$string);
    }

    private function checkType($string){
        return preg_match("/(string)|(int)|(bool)|(nil)/",$string);
    }

    function checkCorrectness() {
        if (self::$count == 0) {
            if (strcmp($this->array[0],".IPPCODE22") != 0) {
                fwrite(STDERR, "Chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode22.\n");
                exit(21);
            }else{
                self::$dom = new DOMDocument('1.0','UTF-8');
                self::$dom->formatOutput = true;
                self::$program = self::$dom->createElement("program");
                $programAttribute = self::$dom->createAttribute('language');
                $programAttribute->value = 'IPPcode22';
                self::$program->appendChild($programAttribute);
                self::$dom->appendChild(self::$program);
            }
        }else {
            switch ($this->array[0]) {
                // VAR
                case "DEFVAR":
                case "POPS":
                    if(count($this->array) == 2){
                        if ($this->checkVar($this->array[1])){
                            $instruction = self::$dom->createElement("instruction");
                            $instructionAttribute = self::$dom->createAttribute('order');
                            $instructionAttribute->value = strval(self::$count);
                            $instruction->appendChild($instructionAttribute);
                            $instructionAttribute = self::$dom->createAttribute('opcode');
                            $instructionAttribute->value = $this->array[0];
                            $instruction->appendChild($instructionAttribute);
                            $arg1 = self::$dom->createElement("arg1", $this->array[1]);
                            $arg1Attribute = self::$dom->createAttribute('type');
                            $arg1Attribute->value = 'var';
                            $arg1->appendChild($arg1Attribute);
                            $instruction->appendChild($arg1);
                            self::$program->appendChild($instruction);
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }
                    }else {
                        fwrite(STDERR, "Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
                        exit(23);
                    }
                    break;
                // VAR SYMB
                case "MOVE":
                case "INT2CHAR":
                case "STRLEN":
                case "TYPE":
                    if(count($this->array) == 3){
                        if ($this->checkVar($this->array[1])){
                            $instruction = self::$dom->createElement("instruction");
                            $instructionAttribute = self::$dom->createAttribute('order');
                            $instructionAttribute->value = strval(self::$count);
                            $instruction->appendChild($instructionAttribute);
                            $instructionAttribute = self::$dom->createAttribute('opcode');
                            $instructionAttribute->value = $this->array[0];
                            $instruction->appendChild($instructionAttribute);
                            $arg1 = self::$dom->createElement("arg1", $this->array[1]);
                            $arg1Attribute = self::$dom->createAttribute('type');
                            $arg1Attribute->value = 'var';
                            $arg1->appendChild($arg1Attribute);
                            $instruction->appendChild($arg1);
                            $arg2 = self::$dom->createElement("arg2", substr($this->array[2],strpos($this->array[2], "@")+1));
                            $arg2Attribute = self::$dom->createAttribute('type');
                            if (str_contains($this->array[2],"GF") || str_contains($this->array[2],"LF") || str_contains($this->array[2],"TF")){ // nastaveni zda mame konstatntu nebo promnenou
                                $arg2Attribute->value = 'var';
                            }else{
                                $arg2Attribute->value = substr($this->array[2], 0, strpos($this->array[2], "@"));
                            }
                            $arg2->appendChild($arg2Attribute);
                            $instruction->appendChild($arg2);
                            self::$program->appendChild($instruction);
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }

                        if ($this->checkVar($this->array[2]) || $this->checkConst($this->array[2])){
                            echo "je to good";
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }
                    }else {
                        fwrite(STDERR, "Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
                        exit(23);
                    }
                    break;
                //NIC
                case "CREATEFRAME":
                case "PUSHFRAME":
                case "POPFRAME":
                case "RETURN":
                case "BREAK":
                    $instruction = self::$dom->createElement("instruction");
                    $instructionAttribute = self::$dom->createAttribute('order');
                    $instructionAttribute->value = strval(self::$count);
                    $instruction->appendChild($instructionAttribute);
                    $instructionAttribute = self::$dom->createAttribute('opcode');
                    $instructionAttribute->value = $this->array[0];
                    $instruction->appendChild($instructionAttribute);
                    self::$program->appendChild($instruction);
                    break;
                //LABEL
                case "CALL":
                case "JUMP":
                case "LABEL":
                    if(count($this->array) == 2){
                        if ($this->checkLabel($this->array[1])){
                            $instruction = self::$dom->createElement("instruction");
                            $instructionAttribute = self::$dom->createAttribute('order');
                            $instructionAttribute->value = strval(self::$count);
                            $instruction->appendChild($instructionAttribute);
                            $instructionAttribute = self::$dom->createAttribute('opcode');
                            $instructionAttribute->value = $this->array[0];
                            $instruction->appendChild($instructionAttribute);
                            $arg1 = self::$dom->createElement("arg1", $this->array[1]);
                            $arg1Attribute = self::$dom->createAttribute('type');
                            $arg1Attribute->value = 'label';
                            $arg1->appendChild($arg1Attribute);
                            $instruction->appendChild($arg1);
                            self::$program->appendChild($instruction);
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }
                    }else {
                        fwrite(STDERR, "Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
                        exit(23);
                    }
                    break;
                //SYMBOL
                case "PUSH":
                case "WRITE":
                case "EXIT":
                case "DPRINT":
                    if(count($this->array) == 2){
                        if ($this->checkVar($this->array[1]) || $this->checkConst($this->array[1])){
                            $instruction = self::$dom->createElement("instruction");
                            $instructionAttribute = self::$dom->createAttribute('order');
                            $instructionAttribute->value = strval(self::$count);
                            $instruction->appendChild($instructionAttribute);
                            $instructionAttribute = self::$dom->createAttribute('opcode');
                            $instructionAttribute->value = $this->array[0];
                            $instruction->appendChild($instructionAttribute);
                            $arg1 = self::$dom->createElement("arg1", substr($this->array[1],strpos($this->array[1], "@")+1));
                            $arg1Attribute = self::$dom->createAttribute('type');
                            if (str_contains($this->array[1],"GF") || str_contains($this->array[1],"LF") || str_contains($this->array[1],"TF")){ // nastaveni zda mame konstatntu nebo promnenou
                                $arg1Attribute->value = 'var';
                            }else{
                                $arg1Attribute->value = substr($this->array[1], 0, strpos($this->array[1], "@"));
                            }
                            $arg1->appendChild($arg1Attribute);
                            $instruction->appendChild($arg1);
                            self::$program->appendChild($instruction);
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }
                    }else {
                        fwrite(STDERR, "Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
                        exit(23);
                    }
                    break;
                //VAR SYMB SYMB
                case "ADD":
                case "SUB":
                case "MUL":
                case "IDIV":
                case "LT":
                case "GT":
                case "EQ":
                case "AND":
                case "OR":
                case "NOT":
                case "CONCAT":
                case "GETCHAR":
                case "SETCHAR":
                case "STRING2INT":
                    if(count($this->array) == 4){
                        if ($this->checkVar($this->array[1]) && ($this->checkVar($this->array[2]) || $this->checkConst($this->array[2])) && ($this->checkVar($this->array[3]) || $this->checkConst($this->array[3]))){
                            $instruction = self::$dom->createElement("instruction");
                            $instructionAttribute = self::$dom->createAttribute('order');
                            $instructionAttribute->value = strval(self::$count);
                            $instruction->appendChild($instructionAttribute);
                            $instructionAttribute = self::$dom->createAttribute('opcode');
                            $instructionAttribute->value = $this->array[0];
                            $instruction->appendChild($instructionAttribute);
                            $arg1 = self::$dom->createElement("arg1", $this->array[1]);
                            $arg1Attribute = self::$dom->createAttribute('type');
                            $arg1Attribute->value = 'var';
                            $arg1->appendChild($arg1Attribute);
                            $instruction->appendChild($arg1);
                            $arg2 = self::$dom->createElement("arg2", substr($this->array[2],strpos($this->array[2], "@")+1));
                            $arg2Attribute = self::$dom->createAttribute('type');
                            if (str_contains($this->array[2],"GF") || str_contains($this->array[2],"LF") || str_contains($this->array[2],"TF")){ // nastaveni zda mame konstatntu nebo promnenou
                                $arg2Attribute->value = 'var';
                            }else{
                                $arg2Attribute->value = substr($this->array[2], 0, strpos($this->array[2], "@"));
                            }
                            $arg2->appendChild($arg2Attribute);
                            $instruction->appendChild($arg2);

                            $arg3 = self::$dom->createElement("arg3", substr($this->array[3],strpos($this->array[3], "@")+1));
                            $arg3Attribute = self::$dom->createAttribute('type');
                            if (str_contains($this->array[3],"GF") || str_contains($this->array[3],"LF") || str_contains($this->array[3],"TF")){ // nastaveni zda mame konstatntu nebo promnenou
                                $arg3Attribute->value = 'var';
                            }else{
                                $arg3Attribute->value = substr($this->array[3], 0, strpos($this->array[3], "@"));
                            }
                            $arg3->appendChild($arg3Attribute);
                            $instruction->appendChild($arg3);
                            self::$program->appendChild($instruction);
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }
                    }else {
                        fwrite(STDERR, "Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
                        exit(23);
                    }
                    break;
                // VAR TYPE
                case "READ":
                    if(count($this->array) == 3){
                        if ($this->checkVar($this->array[1]) && $this->checkType($this->array[2])){
                            $instruction = self::$dom->createElement("instruction");
                            $instructionAttribute = self::$dom->createAttribute('order');
                            $instructionAttribute->value = strval(self::$count);
                            $instruction->appendChild($instructionAttribute);
                            $instructionAttribute = self::$dom->createAttribute('opcode');
                            $instructionAttribute->value = $this->array[0];
                            $instruction->appendChild($instructionAttribute);
                            $arg1 = self::$dom->createElement("arg1", $this->array[1]);
                            $arg1Attribute = self::$dom->createAttribute('type');
                            $arg1Attribute->value = 'var';
                            $arg1->appendChild($arg1Attribute);
                            $instruction->appendChild($arg1);
                            $arg2 = self::$dom->createElement("arg2", $this->array[2]);
                            $arg2Attribute = self::$dom->createAttribute('type');
                            $arg2Attribute->value = 'type';
                            $arg2->appendChild($arg2Attribute);
                            $instruction->appendChild($arg2);
                            self::$program->appendChild($instruction);
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }
                    }else {
                        fwrite(STDERR, "Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
                        exit(23);
                    }
                    break;
                //LABEL SYMB SYMB
                case "JUMPIFEQ":
                case "JUMPIFNEQ":
                    if(count($this->array) == 4){
                        if ($this->checkLabel($this->array[1]) && ($this->checkVar($this->array[2]) || $this->checkConst($this->array[2])) && ($this->checkVar($this->array[3]) || $this->checkConst($this->array[3]))){
                            $instruction = self::$dom->createElement("instruction");
                            $instructionAttribute = self::$dom->createAttribute('order');
                            $instructionAttribute->value = strval(self::$count);
                            $instruction->appendChild($instructionAttribute);
                            $instructionAttribute = self::$dom->createAttribute('opcode');
                            $instructionAttribute->value = $this->array[0];
                            $instruction->appendChild($instructionAttribute);
                            $arg1 = self::$dom->createElement("arg1", $this->array[1]);
                            $arg1Attribute = self::$dom->createAttribute('type');
                            $arg1Attribute->value = 'label';
                            $arg1->appendChild($arg1Attribute);
                            $instruction->appendChild($arg1);
                            $arg2 = self::$dom->createElement("arg2", substr($this->array[2],strpos($this->array[2], "@")+1));
                            $arg2Attribute = self::$dom->createAttribute('type');
                            if (str_contains($this->array[2],"GF") || str_contains($this->array[2],"LF") || str_contains($this->array[2],"TF")){ // nastaveni zda mame konstatntu nebo promnenou
                                $arg2Attribute->value = 'var';
                            }else{
                                $arg2Attribute->value = substr($this->array[2], 0, strpos($this->array[2], "@"));
                            }
                            $arg2->appendChild($arg2Attribute);
                            $instruction->appendChild($arg2);

                            $arg3 = self::$dom->createElement("arg3", substr($this->array[3],strpos($this->array[3], "@")+1));
                            $arg3Attribute = self::$dom->createAttribute('type');
                            if (str_contains($this->array[3],"GF") || str_contains($this->array[3],"LF") || str_contains($this->array[3],"TF")){ // nastaveni zda mame konstatntu nebo promnenou
                                $arg3Attribute->value = 'var';
                            }else{
                                $arg3Attribute->value = substr($this->array[3], 0, strpos($this->array[3], "@"));
                            }
                            $arg3->appendChild($arg3Attribute);
                            $instruction->appendChild($arg3);
                            self::$program->appendChild($instruction);
                        }else{
                            fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                            exit(22);
                        }
                    }else {
                        fwrite(STDERR, "Jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode22.\n");
                        exit(23);
                    }
                    break;
                default:
                    fwrite(STDERR, "Neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode22.\n");
                    exit(22);
            }
        }
    }
    public function pritnXML(){
        $xml_string = self::$dom->saveXML();
        echo $xml_string;
    }
}

