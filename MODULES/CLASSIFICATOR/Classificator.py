from MODULES.regex_patterns2 import Quantifier, Operator, Function

from MODULES.regex_functions import get_indexes

import copy

class Classificator:
    __slots__ = ('testconditions','defconditions')
    def __init__(self, testconditions:list, defconditions:list):
        quantifier = Quantifier()
        operator = Operator()
        function = Function()

        patterns = {'function len':([function.lenght, operator.equality],[quantifier.forall,quantifier.exists]),
                    'universal generation':([quantifier.forall, quantifier.endquant], [quantifier.evaluation, quantifier.endevaluation]),
                    'existential generation':([quantifier.exists, quantifier.endquant], [quantifier.evaluation, quantifier.endevaluation]),
                    'universal evaluation':([quantifier.forall, quantifier.endquant,quantifier.evaluation, quantifier.endevaluation],[]),
                    'existential evaluation':([quantifier.exists, quantifier.endquant, quantifier.evaluation, quantifier.endevaluation],[]),
                    'set':([f"{operator.inset}|{operator.notin}"],[quantifier.forall,quantifier.exists]),
                    'relational':([rf"{operator.le}|{operator.ge}|{operator.less}|{operator.greater}|{operator.equality}|{operator.inequality}"],[quantifier.forall, quantifier.exists, operator.or_, operator.implies])}
        
        self.testconditions, self.defconditions = self.main(testconditions, defconditions, patterns)
    

    def main(self, testconditions:list, defconditions:list, patterns:dict[str,tuple]):
        testconditionsG = []
        defconditionsG = []
        for testc,defc in iter(zip(testconditions, defconditions)):
            groups = self.groupping(testc, patterns)
            testconditionsG.append(groups)
            groups = self.groupping(defc, patterns)
            defconditionsG.append(groups)
        return testconditionsG, defconditionsG


    def groupping(self, predicates:list, patterns:dict[str,tuple]) -> dict:
        groups = dict()

        for name in patterns.keys():
            element = self.musthave_nothave(patterns[name][0], patterns[name][1], predicates)
            groups[name] = element

        if(len(predicates)!=0):
            raise ValueError(f"Error en agrupador, no se lograron agrupar los siguientes predicados: {predicates}")
        
        return groups
    

    def musthave_nothave(self, musthave:list[str], nothave:list[str], predicates:list[str]):
        quantifier = Quantifier()
        atoms = list()
        cond = True
        while(cond):
            cond = False
            for i in range(len(predicates)):
                predicate = predicates[i]
                mhlist = [get_indexes(pattern, predicate) for pattern in musthave]

                if(get_indexes(f"{quantifier.forall}|{quantifier.exists}", predicate)):
                    inds = get_indexes(rf"{quantifier.domain}.*{quantifier.enddomain}", predicate)
                    predicate = predicate[:inds[0][0]] + predicate[inds[0][1]:]
                    #inds = get_indexes(quantifier.suchthat, predicate)
                    #predicate = predicate[inds[0][1]:]   

                nhlist = [get_indexes(pattern, predicate) for pattern in nothave]
                if(None not in mhlist):
                    if(len(nhlist)==nhlist.count(None)):
                        atoms += [predicates.pop(i)]
                        cond = True
                        break
        return atoms
        
