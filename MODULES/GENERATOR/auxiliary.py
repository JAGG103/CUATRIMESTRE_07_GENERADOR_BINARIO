from MODULES.regex_functions import get_indexes, replace_pattern, split_with_pattern, get_indexes_blocks, indexes_avoiding_head_and_tail, get_elements_notin_indexes

from MODULES.regex_patterns2 import Operator,Quantifier,Type

from fxpmath import Fxp
import random
import math

# Clase utilizada para administrar constantes utilizadas como identificadores
class Flags:
    __slots__ = ('AND','OR','NONE','DOMAINNUM','DOMAINELEMS','DOMAININDS','SET','REL')
    def __init__(self):
        self.AND = 0
        self.OR = 1
        self.NONE = 2

        self.DOMAINNUM = 0
        self.DOMAINELEMS = 1
        self.DOMAININDS = 2

        self.SET = 0
        self.REL = 1

# Clase utilizada para parametrizar el númerico de bits destinado a cada tipo, con el objetivo de aumentar o reducir
class FixedPoint:
    # los valores que estos tipos de datos pueden tomar.
    # Para el tipo de dato REAL se deja un bit de signo, n bits para la parte entera y m bits para la parte fraccionaria.
    __slots__ = ('N_WORD_REAL','N_FRAC_REAL','N_WORD_INT','N_WORD_NAT','N_WORD_CHAR','nwords')
    def __init__(self, num:int):
        aux = math.log(num,2)
        N_WORD = math.ceil(aux)
        N_WORD_MAX = 32

        self.N_WORD_INT = N_WORD + 1
        self.N_WORD_REAL = N_WORD_MAX 
        self.N_FRAC_REAL = self.N_WORD_REAL - self.N_WORD_INT
        self.N_WORD_NAT = N_WORD
        self.N_WORD_CHAR = 7  # 0 - 127
        self.nwords = [self.N_WORD_REAL, self.N_WORD_INT, self.N_WORD_NAT, self.N_WORD_NAT, self.N_WORD_CHAR] # [real, int, nat, nat0, char]

# Clase utilizada para la códificación y decodificación de las cadenas genéticas
class Coding:
    # Clase utilizada para códificación de las soluciones en la secuencia genética de los individuos
    __slots__ = ('N_WORD_REAL','N_FRAC_REAL','N_WORD_INT','N_WORD_NAT','N_WORD_CHAR')
    def __init__(self):
        fxp = FixedPoint()
        self.N_WORD_REAL = fxp.N_FRAC_REAL
        self.N_FRAC_REAL = fxp.N_FRAC_REAL
        self.N_WORD_INT = fxp.N_WORD_INT
        self.N_WORD_NAT = fxp.N_WORD_NAT
        self.N_WORD_CHAR = fxp.N_WORD_CHAR

    # Método utilizado para obtener el genotipo (cadena binaria) a partir de un elemento continuo {int,real,nat,nat0,char}
    def get_genotype(self, element:int|float|str, typee:str) -> list:
        # Si el tipo de dato pertenece a:
            # Si el valor pertenece a un tipo continuo 'int' crea una variable de la clase Fxp para obtener su representación binaria
            # Si el valor pertenece a un tipo continuo 'nat' o 'nat0' crea una variable de la clase Fxp para obtener su representación binaria
            # Si el valor pertenece a un tipo continuo 'real' crea una variable de la clase Fxp para obtener su representación binaria
            # Si el valor pertenece a un tipo continuo 'char' crea una variable de la clase Fxp con su valor ascii, para obtener su representación binaria
            # Si el tipo de dato no pertenece al conjunto {int,nat,nat0,real,char} levanta una excepción
        # Obtiene la representación binaria:str de la variable x:Fxp
        # Obtiene una lista de python donde cada elemento es un valor binario en forma de cadena de caracteres
        if(typee in {'int'}):
            x = Fxp(element, signed=True, n_word=self.N_WORD_INT)
        elif(typee in {'nat', 'nat0'}):
            x = Fxp(element, signed=False, n_word=self.N_WORD_NAT)
        elif(typee in {'real'}):
            x = Fxp(element, signed=True, n_word=self.N_WORD_REAL, n_frac=self.N_FRAC_REAL)
        elif(typee in {'char'}):
            ascii_ = ord(element)
            x = Fxp(int(ascii_), signed=False, n_word=self.N_WORD_CHAR)
        else: 
            raise ValueError("Error")
        x_bin = x.bin()
        x_lst = [e for e in x_bin]
        return x_lst
        
    # Método utilizado para recuperar el elemento continuo, a partir de su representación binaria
    def get_fenotype(self, binary:list, typee:str):
        binaryStr = "".join(binary)
        # Si el tipo de dato pertenece a:
            # Si la secuencia binaria representa un elemento de tipo 'int' se recupera su valor
            # Si la secuencia binaria representa un elemento de tipo 'nat' o 'nat0' se recupera su valor
            # Si la secuencia binaria representa un elemento de tipo 'real' se recupera su valor
            # Si la secuencia binaria representa un elemento de tipo 'char' se recupera su valor, si este valor sale del rango [32,126] regresa un None
        # Regresa el elemento continuo códificado en la cadena binaria
        if(typee in {'int'}):
            x = Fxp(0, signed=True, n_word=self.N_WORD_INT)
            x('0b'+binaryStr)
            x_rec = x.astype(int).item()
        elif(typee in {'nat', 'nat0'}):
            x = Fxp(0, signed=False, n_word=self.N_WORD_NAT)
            x('0b'+binaryStr)
            x_rec = x.astype(int).item()
        elif(typee in {'real'}):
            x = Fxp(0.0, signed=True, n_word=self.N_WORD_REAL, n_frac=self.N_FRAC_REAL)
            x('0b'+binaryStr)
            x_rec = x.astype(float).item()
        elif(typee in {'char'}):
            ascii_ = ord(" ")
            x = Fxp(ascii_, signed=False, n_word=self.N_WORD_CHAR)
            x('0b'+binaryStr)
            x_rec = x.astype(int).item()
            if(x_rec >= 32 and x_rec <= 126):
                x_rec = chr(x_rec)
            else:
                x_rec = None
        else:
            raise ValueError("Error")
        return x_rec

    # Método que permite generar un elemento continuo de un tipo en especifico {int,nat,nat0,real,char} utilizando DISTANCE una constante para variar el tamaño del dominio  
    def generate_element(self, typee:str, DISTANCE:int)->int|float:
        if(typee in {'int'}):
            e = random.randint(-DISTANCE,DISTANCE)
        elif(typee in {'nat'}):
            e = random.randint(1, DISTANCE)
        elif(typee in {'nat0'}):
            e = random.randint(0, DISTANCE)
        elif(typee in {'real'}):
            e = random.uniform(-DISTANCE, DISTANCE)
        elif(typee in {'char'}):
            e = random.randint(32, 126)
            e = chr(e)
        else:
            raise ValueError("Error")
        return e

    # Método que permite generar una secuencia de elementos de un tipo en especifico {int,nat,nat0,real,char}, utilizando la constante DISTANCE para variar el dominio y LENGH el tamaño de la secuencia
    def generate_sequence(self, typee:str, DISTANCE:int, LENGHT:int)->list:
        sequence = [self.generate_element(typee, DISTANCE) for _ in range(LENGHT)]
        return sequence 

# Clase utilizada para extraer información de los predicados con cuantificadores
class Quantifiers:
    __slots__ = ('atoms','operator','itervar','domain','domaint','start','end')
    def __init__(self, predicate:str):
        self.extract_information(predicate)
        

    def extract_information(self, atomic:str): 
        operator = Operator()
        quantifier = Quantifier()
        flags = Flags()

        inds = get_indexes(quantifier.suchthat, atomic)
        # Contenido
        content = atomic[inds[0][1]:-1]
        inds_and = indexes_avoiding_head_and_tail([quantifier.evaluation],[quantifier.endevaluation], operator.and_, content)
        inds_or = indexes_avoiding_head_and_tail([quantifier.evaluation],[quantifier.endevaluation], operator.or_, content)
        if(inds_and):
            atoms, operator = get_elements_notin_indexes(inds_and, content), flags.AND
        elif(inds_or):
            atoms, operator = get_elements_notin_indexes(inds_or, content), flags.OR
        else:
            atoms, operator = [content], flags.NONE
        # Iterable variable
        content = atomic[:inds[0][0]]
        inds = get_indexes(quantifier.itervar, content)
        itervar = content[inds[0][0]:inds[0][1]]
        itervar = rf"(?<!')\b{itervar}\b(?!')"
        # dominio
        inds_domnum = get_indexes_blocks(content, quantifier.num, quantifier.endnum)
        inds_domelem = get_indexes_blocks(content, quantifier.elems, quantifier.endie)
        inds_dominds = get_indexes_blocks(content, quantifier.inds, quantifier.endie)
        if(inds_domnum):
            domain = content[inds_domnum[0][0]+1:inds_domnum[0][1]-1]
            start, end = split_with_pattern(quantifier.to, domain)
            domaint = flags.DOMAINNUM
        elif(inds_domelem):
            domain = content[inds_domelem[0][0]+6:inds_domelem[0][1]-1]
            start, end = '0',f'len({domain})'
            domaint = flags.DOMAINELEMS
        elif(inds_dominds):
            domain = content[inds_dominds[0][0]+5:inds_dominds[0][1]-1]
            start, end = '0',f'len({domain})'
            domaint = flags.DOMAININDS
        else:
            raise ValueError("Dominios invalidos en cuantificador")
        self.atoms = atoms
        self.operator = operator
        self.domaint = domaint
        self.itervar = itervar
        self.domain = domain
        self.start = start
        self.end = end

# Clase que permite agrupar métodos utiles para hacer sustituciones de variables por sus valores
class Substitute:
    __slots__ = ()
    def __init__(self):
        pass

    # Método utilizado para sustituir los valores presentes en 'values' en el predicado 'predicates' ignorando la operación si esa variable esta dentro de una evaluación
    def substitute_values_notin_evaluations(self, values:dict, predicate:str):
        quantifier = Quantifier()
        for variable in values.keys():
            pattern = rf'\b{variable}\b'
            inds = indexes_avoiding_head_and_tail([quantifier.evaluation],[quantifier.endevaluation], pattern, predicate)
            if(inds):
                for i,j in inds:
                    predicate = predicate[:i] + str(values[variable]) + predicate[j:]
        return predicate

    # Método utilizado para sustituir los valores en 'values' en el predicado 'predicate'
    def substitute_dict(self, values:dict, predicate:str)->str:
        for variable in values.keys():
            pattern = rf'\b{variable}\b'
            if(get_indexes(pattern, predicate)):
                element = values[variable]
                telement = type(element)
                element = str(f'"{element}"') if telement==str else str(f"{element}")
                predicate = replace_pattern(pattern, element, predicate)
        return predicate

    # Método utilizado para sustituir los valores del fenotipo 'seqofvalues' (sin codificar) en el predicado 'predicate' apoyandose de los nombres de las variables
    def substitute_values(self, predicate:str, variables:list, seqofvalues:list) -> list:
        # la varible con su mismo indice. len(variable) = len(chromosome)
        for i in range(len(variables)):
            pattern = rf"\b{variables[i]}\b"
            if(get_indexes(pattern, predicate)):
                predicate = replace_pattern(pattern, str(seqofvalues[i]), predicate)
        return predicate

# Clase utilizada para obtener los errores de expresiones relacionales y las que operan sobre conjuntos (No contienen variables) solo expresion dereche, izquierda y operador
class Evaluate:
    def __init__(self):
        pass
    
    def relational(self, left:str, right:str, operator:str):
        # Funcion que permite evaluar una expresión relacional y 
        # regresa un error. La parte izquiera y derecha de la expresión
        # no contienen variables.
        operator_ = Operator()

        try:
            left = float(eval(left))
            right = float(eval(right))
        except ZeroDivisionError:
            error = 100.0
            return error

        indsge, indsle, indseq = get_indexes(operator_.ge, operator), get_indexes(operator_.le, operator), get_indexes(operator_.equality, operator)
        indsg, indsl, indsinq = get_indexes(operator_.greater, operator), get_indexes(operator_.less, operator), get_indexes(operator_.inequality, operator)

        diff = left - right
        if(indsge or indsle or indseq):
            if(indsge and diff>=0) or (indsle and diff<=0) or (indseq and math.isclose(diff,0.0,abs_tol=0.00001)):
                error = 0.0
            else:
                error = abs(diff)
        elif(indsg or indsl or indsinq):
            if(indsg and diff>0) or (indsl and diff<0) or (indsinq and diff!=0):
                error = 0.0
            else:
                error = 1 if diff==0.0 else abs(diff)
        else:
            raise ValueError("Invalid Operator")
        return error


    def set(self, left:str, right:str, operator:str):
        operatorobj = Operator()

        errors = []
        left = eval(left.replace("\\", "\\\\"))
        right = eval(right.replace("\\", "\\\\"))

        if(left==None or (type(left)==list and None in left) or (type(right)==set and None in right)):
            return 200
        
        for element in right:
            error = 0.0
            typeelm, typeleft = type(element), type(left)
            left = ''.join(left) if typeleft==list else left
            typeleft = type(left)
            if(typeelm == typeleft):
                if(typeelm in {str}):
                    for i,j in zip(left,element):
                        error += abs(ord(i)-ord(j))
                elif(typeelm in {int,float}):
                    error += abs(left-element)
                else:
                    raise ValueError("Elementos a evaluar no son del mismo tipo {secuencias de caracteres y enteros/flotantes}")
            else:
                raise ValueError(f"Los elementos utilizados en el operador inset o notin no son del mismo tipo: {typeleft} {typeelm}")
            errors.append(error)
        minimal = min(errors)
        indsin, indsnot = get_indexes(operatorobj.inset, operator), get_indexes(operatorobj.notin, operator)
        if(indsin):
            return minimal
        elif(indsnot):
            if(minimal==0):
                return 100
            else:
                return 0
        else:
            raise ValueError("Operador invalido")
        
    def relational_eval(self, left:str, right:str, operator:str, globvars:dict):
        for variable in globvars.keys():
            globals()[variable] = globvars[variable]
        error = self.relational(left, right, operator)
        return error

    def set_eval(self, left:str, right:str, operator:str, globvars:dict):
        for variable in globvars.keys():
            globals()[variable] = globvars[variable]
        error = self.set(left, right, operator)
        return error
    
    def satisfiability_relational(self, atoms:list, values:dict):
        op = Operator()

        error = 0.0
        pattern = rf"{op.equality}|{op.less}|{op.greater}|{op.inequality}|{op.le}|{op.ge}"
        for atom in atoms:
            indexes = get_indexes(pattern, atom)
            if(indexes):
                operator = atom[indexes[0][0]:indexes[0][1]]
                atom = Substitute().substitute_dict(values, atom)
                left, right = split_with_pattern(pattern, atom)
                error = Evaluate().relational(left, right, operator)
                if(error>0.0):
                    return error
        return error

# Clase utilizada para resolver asignaciones
class Assignments:
    __slots__ = ()
    def __init__(self):
        pass

    def assignments(self, variables:list, types:list, atoms:list) -> dict:
        # Método que se encarga de iterar sobre una lista de predicados atomicos y evalua si son asignaciones validas
        # Para que sea una asignación valida una variable debe de estar sola del lado izquiero de la igualdad y ninguna de las
        # restantes debe de estar del lado derecho, este valor se guarda en values y el atomo no se considera para futuras generaciones.
        # Puede suceder el caso de que dos asiganaciones esten en la lista, en este caso solo la primera sera considerada y
        # los otros predicados que contengan asignación seran considerados para futuras evaluaciones
        typeobj = Type()
        operatorobj = Operator()

        atoms_ = []
        values = dict()
        for atom in atoms:
            if(self.isvalid_assigment(variables, atom)):
                inds = get_indexes(operatorobj.equality, atom)
                variable = atom[:inds[0][0]]
                value = atom[inds[0][1]:]
                for v,t in zip(variables,types):      
                    if(v==variable):
                        if(v not in values):
                            inds = get_indexes(typeobj.int+'|'+typeobj.nat+'|'+typeobj.nat0, t)
                            indsreal = get_indexes(typeobj.real, t)
                            indseq = get_indexes(typeobj.seqof, t)
                            if(inds and indseq==None):
                                values[variable] = int(eval(value))
                            elif(indsreal and indseq==None):
                                values[variable] = float(eval(value))
                            else:
                                values[variable] = eval(value.replace('\\','\\\\'))
                        else:
                            atoms_ += [atom]
            else:
                atoms_ += [atom]
        return values,atoms_

    def isvalid_assigment(self, variables:list, atom:str) -> bool:
        operatorobj = Operator()

        valid, validleft, validright = (False, False, True)
        inds = get_indexes(operatorobj.equality, atom)
        if(inds):
            left = atom[:inds[0][0]]
            right = atom[inds[0][1]:]
            for variable in variables:
                pattern = fr"\b{variable}\b"
                inds = get_indexes(pattern, left)
                if(inds):
                    left = left.replace(' ','')
                    validleft = True if len(left)==(inds[0][1] - inds[0][0]) else validleft
                else:
                    validright = False if get_indexes(pattern, right) else validright
            valid = True if validleft and validright else False
        return valid



