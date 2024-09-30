from MODULES.GENERATOR.auxiliary import Coding
from MODULES.regex_patterns import Types
from MODULES.regex_functions import get_indexes

class Individual:
    __slots__ = ('basics','nwords','fenotype','genotype','types')
    def __init__(self, types:list) -> None:    
        self.basics = [Types().real, Types().int, Types().nat, Types().nat0, Types().char]
        self.nwords = [32, 13, 12, 12, 7]
        self.fenotype = []
        self.genotype = []
        self.types = types

    def create_offspring(self, genotypeseq, lenghts):
        coding = Coding()
        self.fenotype = []
        self.genotype = genotypeseq
        counter = 0
        for i in range(len(self.types)):
            typee = self.types[i]
            for j in range(len(self.basics)):
                inds = get_indexes(self.basics[j],typee)
                indseq = get_indexes(Types().seqof, typee)
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


    def create_progenitor(self, DISTANCE:int, lenghts:list[int])->list:
        coding = Coding()
        chromosome = []
        basicTypes = fr"{Types().real}|{Types().int}|{Types().nat}|{Types().nat0}|{Types().char}"
        patternSeq = Types().seqof
        for i in range(len(self.types)):
            indexes = get_indexes(patternSeq, self.types[i])
            if(indexes):
                typee = self.types[i][indexes[0][1]:]
                elements = coding.generate_sequence(typee, DISTANCE, lenghts[i])
                self.fenotype.append(elements.copy())
            else:
                typee = self.types[i]
                indexes = get_indexes(basicTypes, typee)
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