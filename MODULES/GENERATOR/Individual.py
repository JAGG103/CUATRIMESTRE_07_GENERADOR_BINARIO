from MODULES.GENERATOR.auxiliary import Coding, FixedPoint

from MODULES.regex_patterns2 import Type

from MODULES.regex_functions import get_indexes

class Individual:
    __slots__ = ('basics','nwords','fenotype','genotype','types')
    def __init__(self, types:list, distance:int) -> None:    
        type_ = Type()
        fxp = FixedPoint(distance)
        # Patrones re de los tipos basicos
        self.basics = [type_.real, type_.int, type_.nat, type_.nat0, type_.char]
        # Se instancia una lista de valores enteros que corresponde al número de bits para cada tipo básico
        self.nwords = fxp.nwords
        self.fenotype = []
        self.genotype = []
        self.types = types

    # Función que permite crear un individuo a partir de su secuencia genética códificada (Binario)
    def create_offspring(self, genotypeseq, lenghts):
        coding = Coding()
        type_ = Type()

        self.fenotype = []
        self.genotype = genotypeseq
        counter = 0
        for i in range(len(self.types)):
            typee = self.types[i]
            for j in range(len(self.basics)):
                inds = get_indexes(self.basics[j],typee)
                indseq = get_indexes(type_.seqof, typee)
                if(inds):
                    elements = []
                    typee = typee[inds[0][0]:inds[0][1]]
                    for _ in range(lenghts[i]):
                        seggenotype = genotypeseq[counter: counter+self.nwords[j]]
                        element = coding.get_fenotype(seggenotype, typee)
                        elements.append(element)
                        counter += self.nwords[j]
                    if(indseq):
                        self.fenotype.append(elements)
                    else:
                        self.fenotype.append(element)
                    break

    # Función que permite crear un individuo progenitor, generando sus genes de forma aleatoria utilizando sus tipos
    def create_progenitor(self, DISTANCE:int, lenghts:list[int])->list:
        coding = Coding()
        type_ = Type()
        
        chromosome = []
        for i in range(len(self.types)):
            indexes = get_indexes(type_.seqof, self.types[i])
            if(indexes):
                typee = self.types[i][indexes[0][1]:]
                elements = coding.generate_sequence(typee, DISTANCE, lenghts[i])
                self.fenotype.append(elements.copy())
            else:
                typee = self.types[i]
                indexes = get_indexes('|'.join(self.basics), typee)
                if(indexes):
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