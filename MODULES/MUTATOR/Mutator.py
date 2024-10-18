from MODULES.regex_functions import indexes_avoiding_head_and_tail

from MODULES.regex_patterns2 import Operator, Quantifier, Mutation

import copy

class Mutator:
    __slots__ = ('precondition','testconditions','defconditions')
    def __init__(self, precondition:list, testconditions:list[list], defconditions:list[list]):
        self.precondition = precondition
        self.testconditions = testconditions
        self.defconditions = defconditions
        self.main()
        

    def main(self):
        # Se extienden las condiciones de prueba manteniendo sus condiciones de definición originales
        #adjust = (2*len(self.precondition))-len(self.precondition) # Si queremos que no mute las precondiciones decomentar esta linea y comntar la siguiente
        adjust = 0
        self.extend_testconditions_defconditions(adjust, self.testconditions, self.defconditions)
        # Se extienden las condiciones de definición manteniendo sus condiciones de prueba originales
        adjust = 0
        self.extend_testconditions_defconditions(adjust, self.defconditions, self.testconditions)


    def extend_testconditions_defconditions(self, adjust:int, targetConditions:list[list], fixedConditions:list[list])->None:
        operator = Operator()
        quantifier = Quantifier()
        mutation = Mutation()

        condition = True
        while(condition):
            condition = False
            for it in range(len(targetConditions)):
                if(condition):
                    break
                for i in range(adjust, len(targetConditions[it])):
                    mutants = {}
                    indexes_le = indexes_avoiding_head_and_tail([quantifier.forall, quantifier.exists],[quantifier.endquant, quantifier.endquant], operator.le, targetConditions[it][i])
                    indexes_ge = indexes_avoiding_head_and_tail([quantifier.forall, quantifier.exists],[quantifier.endquant, quantifier.endquant], operator.ge, targetConditions[it][i])
                    indexes_ne = indexes_avoiding_head_and_tail([quantifier.forall, quantifier.exists],[quantifier.endquant, quantifier.endquant], operator.inequality, targetConditions[it][i])
                    if(indexes_le):
                        mutants = self.extend_set_of_predicates(targetConditions[it],fixedConditions[it], i, indexes_le, mutation.less, mutation.equal)
                    elif(indexes_ge):
                        mutants = self.extend_set_of_predicates(targetConditions[it],fixedConditions[it], i, indexes_ge, mutation.greater, mutation.equal)
                    elif(indexes_ne):
                        mutants = self.extend_set_of_predicates(targetConditions[it],fixedConditions[it], i, indexes_ne, mutation.greater, mutation.less)
                    else:
                        pass

                    if(mutants!={}):
                        targetConditions.pop(it)
                        fixedConditions.pop(it)
                        targetConditions.insert(it, mutants['mutant A'][0])
                        fixedConditions.insert(it, mutants['mutant A'][1])
                        targetConditions.insert(it, mutants['mutant B'][0])
                        fixedConditions.insert(it, mutants['mutant B'][1])
                        condition = True
                        break
        
    def extend_set_of_predicates(self, obj:list, piv:list, i:int, indexes:list[tuple], operatorA:str, operatorB:str)->dict[str,tuple]:
        mutantA = copy.deepcopy(obj)
        mutantB = copy.deepcopy(obj)
        pivA = copy.deepcopy(piv)
        pivB = copy.deepcopy(piv)

        elem = obj[i][:indexes[0][0]] + operatorA + obj[i][indexes[0][1]:]
        mutantA[i] = elem

        elem = obj[i][:indexes[0][0]] + operatorB + obj[i][indexes[0][1]:]
        mutantB[i] = elem

        mutants = {'mutant A':(mutantA,pivA), 'mutant B':(mutantB,pivB)}
        return mutants