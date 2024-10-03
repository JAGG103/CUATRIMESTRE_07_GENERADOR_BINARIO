from MODULES.regex_functions import get_indexes, replace_pattern
from MODULES.regex_patterns import Operator
from fxpmath import Fxp
import random
import math

class Coding:
    def __init__(self):
        # deja 1 bit para signo y 12 bits para la parte entera    
        # -4096.00 to 4096.00
        self.N_WORD_REAL = 32
        self.N_FRAC_REAL = 19
        # -4096 to 4096
        self.N_WORD_INT = 13
        # 0 to 4096
        self.N_WORD_NAT = 12
        # 0 - 127
        self.N_WORD_CHAR = 7

    def get_genotype(self, element:int|float|str, typee:str) -> list:
        # Resultado al códificar la secuencia genética
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
        
        
    def get_fenotype(self, binary:list, typee:str):
        # Resultado de decodificar
        
        binaryStr = "".join(binary)

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


    def generate_sequence(self, typee:str, DISTANCE:int, LENGHT:int)->list:
        sequence = [self.generate_element(typee, DISTANCE) for _ in range(LENGHT)]
        return sequence 


class Evaluate:
    def __init__(self):
        pass

    def substitute_dict(self, values:dict, atom:str):
        for variable in values.keys():
            pattern = rf'\b{variable}\b'
            if(get_indexes(pattern, atom)):
                atom = replace_pattern(pattern, str(values[variable]), atom)
        return atom

    def substitute_values(self, atomicp:str, variables:list, chromosome:list) -> list:
        # Función que toma un predicado atomico y substituye las variables en el
        # Con sus valores generados presentes la variable "chromosoma"
        # donde cada elemento del cromosoma es un valor generador para
        # la varible con su mismo indice. len(variable) = len(chromosome)
        for i in range(len(variables)):
            pattern = rf"\b{variables[i]}\b"
            if(get_indexes(pattern, atomicp)):
                atomicp = replace_pattern(pattern, str(chromosome[i]), atomicp)
        return atomicp


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
                error = abs(diff)
        else:
            raise ValueError("Invalid Operator")
        return error

#
    def set(self, left:str, right:str, operator:str):
        op = Operator('set')
        errors = []

        try:
            left = eval(left.replace("\\", "\\\\"))
            right = eval(right)
            if(left==None):
                raise TypeError
        except TypeError:
            return 200
        
        for element in right:
            error = 0.0
            for i,j in zip(left,element):
                typei, typej = type(i),type(j)
                if(typei==typej):
                    if(typei == str):
                        error += abs(ord(i)-ord(j))
                    elif(typei in {int,float}):
                        error += abs(i-j)
                    else:
                        raise ValueError("El tipo de elementos no es valido")
                else:
                    raise ValueError("Elementos a evaluar no son del mismo tipo")
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
        
        
        