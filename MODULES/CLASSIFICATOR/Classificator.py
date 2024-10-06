from MODULES.regex_patterns import Universal, Existential, Operator, Blocks, Set, Functions
from MODULES.regex_functions import get_indexes

class Classificator:
    __slots__ = ('testConditions','defConditions')
    def __init__(self, testConditions:list, defConditions:list):
        check = [Blocks('quantifiers')._forall, Blocks('quantifiers')._exists]
        check += [Operator('logic').or_, Operator('logic').implies_]
        patterns = [Functions('len').len]
        patterns += [Universal('generation').pattern, Existential('generation').pattern, Universal('evaluation').pattern, Existential('evaluation').pattern]
        patterns += [Set().in_ + '|' + Set().not_]
        names =  ['func len']
        names += ['universal generation','existential generation','universal evaluation','existential evaluation']
        names += ['set','relational']

        self.testConditions, self.defConditions = self.main(testConditions, defConditions, patterns, check, names)
    
    def main(self, testConditions:list, defConditions:list, patterns:list, check:list, names:list):
        testConditionsG = []
        defConditionsG = []
        for testc,defc in iter(zip(testConditions, defConditions)):
            groups = self.groupping(testc, patterns, check, names)
            testConditionsG.append(groups)
            groups = self.groupping(defc, patterns, check, names)
            defConditionsG.append(groups)
        return testConditionsG, defConditionsG


    def groupping(self, condition:list, patterns:list, check:list, names:list) -> dict:
        groups = dict()
        elements = []
        for pattern in patterns:
            element = self.create_group(pattern, condition)
            elements.append(element)
        pattern = "|".join(check)
        for atom in condition:
            if(get_indexes(pattern, atom)!=None):
                raise ValueError(f"Error en agrupador {atom}")
        elements.append(condition.copy())
        for i in range(len(names)):
            groups[names[i]] = elements[i]
        return groups
    

    def create_group(self, pattern:str, condition: list[str]) -> list:
        atoms = []
        out = True
        while(out):
            out = False
            for i in range(len(condition)):
                indexes = get_indexes(pattern, condition[i])
                if(indexes):
                    atoms += [condition.pop(i)]
                    out = True
                    break
        return atoms
