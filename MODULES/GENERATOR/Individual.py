from MODULES.GENERATOR.auxiliary import Coding
import re

class Individual:
    def __init__(self, types:list) -> None:    
        # -4096.00 to 4096.00
        self.N_WORD_REAL = 32
        self.N_FRAC_REAL = 19
        # -4096 to 4096
        self.N_WORD_INT = 13
        # 0 to 4096
        self.N_WORD_NAT = 12
        # 0 - 127
        self.N_WORD_CHAR = 7

        self.fenotype = [] # Sin codificar
        self.genotype = [] # Codificado
        self.types = types

    def create_offspring(self, genotypeSeq, lenghts):
        coding = Coding()
        patternSeq = "(seq)\s*(of)\s*"
        counter = 0
        self.fenotype = []
        self.genotype = genotypeSeq

        for i in range(len(self.types)):
            typee = self.types[i]
            if(typee in {'real'}):
                auxlenght = self.N_WORD_REAL
                elementStr = genotypeSeq[counter: counter+auxlenght]
                element = coding.get_fenotype(elementStr, typee)
                self.fenotype.append(element)
                counter += auxlenght

            elif(typee in {'int'}):
                auxlenght = self.N_WORD_INT
                elementStr = genotypeSeq[counter: counter+auxlenght]
                element = coding.get_fenotype(elementStr, typee)
                self.fenotype.append(element)
                counter += auxlenght

            elif(typee in {'nat', 'nat0'}):
                auxlenght = self.N_WORD_NAT
                elementStr = genotypeSeq[counter: counter+auxlenght]
                element = coding.get_fenotype(elementStr, typee)
                self.fenotype.append(element)
                counter += auxlenght

            elif(typee in {'char'}):
                auxlenght = self.N_WORD_CHAR
                elementStr = genotypeSeq[counter: counter+auxlenght]
                element = coding.get_fenotype(elementStr, typee)
                self.fenotype.append(element)
                counter += auxlenght

            else:
                search = re.search(patternSeq, typee)
                if(search):
                    index = search.span()
                    typee = typee[index[1]:]
                    
                    sequence = []
                    if(typee in {'real'}):
                        auxlenght = self.N_WORD_REAL
                        for _ in range(lenghts[i]):
                            elementStr = genotypeSeq[counter: counter+auxlenght]
                            element = coding.get_fenotype(elementStr, typee)
                            sequence.append(element)
                            counter += auxlenght
                        self.fenotype.append(sequence)

                    elif(typee in {'int'}):
                        auxlenght = self.N_WORD_INT
                        for _ in range(lenghts[i]):
                            elementStr = genotypeSeq[counter: counter+auxlenght]
                            element = coding.get_fenotype(elementStr, typee)
                            sequence.append(element)
                            counter += auxlenght
                        self.fenotype.append(sequence)

                    elif(typee in {'nat', 'nat0'}):
                        auxlenght = self.N_WORD_NAT
                        for _ in range(lenghts[i]):
                            elementStr = genotypeSeq[counter: counter+auxlenght]
                            element = coding.get_fenotype(elementStr, typee)
                            sequence.append(element)
                            counter += auxlenght
                        self.fenotype.append(sequence)

                    elif(typee in {'char'}):
                        auxlenght = self.N_WORD_CHAR
                        for _ in range(lenghts[i]):
                            elementStr = genotypeSeq[counter: counter+auxlenght]
                            element = coding.get_fenotype(elementStr, typee)
                            sequence.append(element)
                            counter += auxlenght
                        self.fenotype.append(sequence)
                    else:
                        raise ValueError("Error")    
                else:
                    raise ValueError("Error")
        

    def create_progenitor(self, DISTANCE:int, lenghts:list[int])->list:
        coding = Coding()
        chromosome = []
        basicTypes = {'int', 'nat', 'nat0', 'real', 'char'}
        patternSeq = "(seq)\s*(of)\s*"
        for i in range(len(self.types)):
            search = re.search(patternSeq, self.types[i])
            if(search):
                index = search.span()
                typee = self.types[i][index[1]:]
                elements = coding.generate_sequence(typee, DISTANCE, lenghts[i])
                self.fenotype.append(elements.copy())
            else:
                typee = self.types[i]
                if(typee in basicTypes):
                    element = coding.generate_element(self.types[i], DISTANCE)
                    self.fenotype.append(element)
                    elements = [element]
                else:
                    raise ValueError("Individual Error")
                
            for element in elements:
                chromosome = coding.get_genotype(element, typee)
                self.genotype = self.genotype + chromosome


    def show_properties(self):
        print(self.fenotype)
        print(self.genotype)
        print(self.types)