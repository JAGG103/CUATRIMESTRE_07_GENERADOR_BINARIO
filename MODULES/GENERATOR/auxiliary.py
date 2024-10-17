from MODULES.regex_functions import get_indexes, replace_pattern, split_with_pattern, get_indexes_blocks, indexes_avoiding_head_and_tail, get_elements_notin_indexes

#from MODULES.regex_patterns import Operator, Delimiters, Universal, Existential, Types
from MODULES.regex_patterns2 import Operator,Delimiter, Quantifier

from fxpmath import Fxp
import random
import math

class Flags:
    __slots__ = ('AND','OR','NONE','DOMAINNUM','DOMAINELEMS','DOMAININDS')
    def __init__(self):
        self.AND = 0
        self.OR = 1
        self.NONE = 2

        self.DOMAINNUM = 0
        self.DOMAINELEMS = 1
        self.DOMAININDS = 2

class FixedPoint:
    # Clase utilizada para parametrizar el númerico de bits destinado a cada tipo, con el objetivo de aumentar o reducir
    # los valores que estos tipos de datos pueden tomar.
    # Para el tipo de dato REAL se deja un bit de signo, n bits para la parte entera y m bits para la parte fraccionaria.
    __slots__ = ('N_WORD_REAL','N_FRAC_REAL','N_WORD_INT','N_WORD_NAT','N_WORD_CHAR','nwords')
    def __init__(self):
        self.N_WORD_REAL = 32 # -4096.00 to 4096.00
        self.N_FRAC_REAL = self.N_WORD_REAL - self.N_WORD_INT
        self.N_WORD_INT = 13  # -4096 to 4096
        self.N_WORD_NAT = self.N_WORD_INT - 1  # 0 to 4096
        self.N_WORD_CHAR = 7  # 0 - 127
        self.nwords = [self.N_WORD_REAL, self.N_WORD_INT, self.N_WORD_NAT, self.N_WORD_NAT, self.N_WORD_CHAR] # [real, int, nat, nat0, char]

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


class Quantifiers:
    __slots__ = ()
    def __init__(self, predicate:str):
        self.extract_information(predicate)
        

    def extract_information(self, atomic:str, quantifier:str): 
        delimiter = Delimiter()
        operator = Operator()
        quantifier = Quantifier()


        suchthat = Delimiters('such that').suchthat
        evaluation = Delimiters('evaluation')
        to = Delimiters('to').to
        op = Operator('logic')
        AND, OR, NONE = (1,2,3)
        DNUM, DELEM, DINDS = (1,2,3)
        inds = get_indexes(suchthat, atomic)
        # Contenido
        content = atomic[inds[0][1]:-1]
        inds_and = indexes_avoiding_head_and_tail([evaluation._evaluation],[evaluation.evaluation_],op.and_,content)
        inds_or = indexes_avoiding_head_and_tail([evaluation._evaluation],[evaluation.evaluation_],op.or_,content)
        if(inds_and):
            atoms, operator = get_elements_notin_indexes(inds_and, content), AND
        elif(inds_or):
            atoms, operator = get_elements_notin_indexes(inds_or, content), OR
        else:
            atoms, operator = [content], NONE 
        # Iterable variable
        content = atomic[:inds[0][0]]
        inds = get_indexes(quantifier.iterv, content)
        iterv = content[inds[0][0]:inds[0][1]]
        iterv = rf"(?<!')\b{iterv}\b(?!')"
        # dominio
        inds_domnum = get_indexes_blocks(content, quantifier._domainnum, quantifier.domainnum_)
        inds_domelem = get_indexes_blocks(content, quantifier._domainelems, quantifier.domainelems_)
        inds_dominds = get_indexes_blocks(content, quantifier._domaininds, quantifier.domaininds_)
        if(inds_domnum):
            domain = content[inds_domnum[0][0]+1:inds_domnum[0][1]-1]
            start, end = split_with_pattern(to, domain)
            domtype = DNUM
        elif(inds_domelem):
            domain = content[inds_domelem[0][0]+6:inds_domelem[0][1]-1]
            start, end = '0',f'len({domain})'
            domtype = DELEM
        elif(inds_dominds):
            domain = content[inds_dominds[0][0]+5:inds_dominds[0][1]-1]
            start, end = '0',f'len({domain})'
            domtype = DINDS
        else:
            raise ValueError("Dominios invalidos en cuantificador")
        self.atoms = atoms
        self.operator = operator
        self.iterv = iterv
        self.domain = domain
        self.domtype = domtype
        self.start = start
        self.end = end

class Substitute:
    def __init__(self):
        pass

    def substitute_pattern_notinside(self, values:dict, predicate:str):
        for variable in values.keys():
            pattern = rf'\b{variable}\b'
            inds = indexes_avoiding_head_and_tail([r"(?<!')\{(?!')"],[r"(?<!')\}(?!')"], pattern, predicate)
            if(inds):
                for i,j in inds:
                    predicate = predicate[:i] + str(values[variable]) + predicate[j:]
        return predicate

    def substitute_dict(self, values:dict, predicate:str)->str:
        for variable in values.keys():
            pattern = rf'\b{variable}\b'
            if(get_indexes(pattern, predicate)):
                element = values[variable]
                telement = type(element)
                element = str(f'"{element}"') if telement==str else str(f"{element}")
                predicate = replace_pattern(pattern, element, predicate)
        return predicate

    def substitute_values(self, predicate:str, variables:list, seqofvalues:list) -> list:
        # Función que toma un predicado atomico y substituye las variables en el
        # Con sus valores generados presentes la variable "chromosoma"
        # donde cada elemento del cromosoma es un valor generador para
        # la varible con su mismo indice. len(variable) = len(chromosome)
        for i in range(len(variables)):
            pattern = rf"\b{variables[i]}\b"
            if(get_indexes(pattern, predicate)):
                predicate = replace_pattern(pattern, str(seqofvalues[i]), predicate)
        return predicate

class Evaluate:
    def __init__(self):
        pass
    
    def relational(self, left:str, right:str, operator:str):
        # Funcion que permite evaluar una expresión relacional y 
        # regresa un error. La parte izquiera y derecha de la expresión
        # no contienen variables.
        op = Operator('relational')
        try:
            left = float(eval(left))
            right = float(eval(right))
        except ZeroDivisionError:
            error = 100.0
            return error

        indsgreat, indsless, indseq = get_indexes(op.greater_,operator), get_indexes(op.less_,operator), get_indexes(op.equality_,operator)
        if(indsgreat or indsless or indseq):
            diff = left - right
            if(indsgreat and diff>0) or (indsless and diff<0) or (indseq and (diff==0 or math.isclose(diff,0.0,abs_tol=0.00001))):
                error = 0.0
            else:
                error = 1 if diff==0.0 else abs(diff)
        else:
            raise ValueError("Invalid Operator")
        
        return error

    def set(self, left:str, right:str, operator:str):
        op = Operator('set')
        errors = []
        left = eval(left.replace("\\", "\\\\"))
        right = eval(right.replace("\\", "\\\\"))
        if(left==None or (type(left)==list and None in left)):
            return 200
        for element in right:
            error = 0.0
            typeelm = type(element)
            typeleft = type(left)
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
        indsin, indsnot = get_indexes(op.inset_, operator), get_indexes(op.notin_, operator)
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
        error = 0.0
        op = Operator('relational')
        pattern = rf"{op.equality_}|{op.less_}|{op.greater_}"
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

class Assignments:
    __slots__ = ('equality')
    def __init__(self):
        self.equality = Operator('relational').equality_

    def assignments(self, variables:list, types:list, atoms:list) -> dict:
        # Método que se encarga de iterar sobre una lista de predicados atomicos y evalua si son asignaciones validas
        # Para que sea una asignación valida una variable debe de estar sola del lado izquiero de la igualdad y ninguna de las
        # restantes debe de estar del lado derecho, este valor se guarda en values y el atomo no se considera para futuras generaciones.
        # Puede suceder el caso de que dos asiganaciones esten en la lista, en este caso solo la primera sera considerada y
        # los otros predicados que contengan asignación seran considerados para futuras evaluaciones
        atoms_ = []
        values = dict()
        typeobj = Types()
        for atom in atoms:
            if(self.isvalid_assigment(variables, atom)):
                inds = get_indexes(self.equality, atom)
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
        valid, validleft, validright = (False, False, True)
        inds = get_indexes(self.equality, atom)
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



