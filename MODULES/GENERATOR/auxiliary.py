from fxpmath import Fxp
import random

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
            # if(x_rec >= 32 and x_rec <= 126):
            #     x_rec = chr(x_rec)
            # elif(x_rec<32):
            #     x_rec = chr(32)
            # else:
            #     x_rec = chr(126)
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