from MODULES.regex_patterns import Universal, Existential, Operator, Blocks, Set, Functions
from MODULES.regex_functions import replace_pattern, get_indexes

class Classificator:
    __slots__ = ('testConditions','defConditions','_and_')
    def __init__(self, testConditions:list, defConditions:list):
        self._and_ = ' and '
        check = [Blocks('quantifiers')._forall, Blocks('quantifiers')._exists]
        check += [Operator('logic').or_, Operator('logic').implies_]
        patterns = [Universal('numeric').generation, Existential('numeric').generation, Universal('elems').generation, Universal('inds').generation]
        patterns += [Universal('numeric').evaluation, Universal('elems').evaluation, Universal('inds').evaluation]
        patterns += [Set('in').in_+'|'+ Set('not').not_]
        patterns += [Functions('len').len]
        names = ['universal numeric generation', 'existential numeric generation', 'universal elems generation', 'universal inds generation']
        names += ['universal numeric evaluation', 'universal elems evaluation', 'universal inds evaluation']
        names += ['set']
        names += ['func len']
        names += ['relational']
        self.testConditions, self.defConditions = self.main(testConditions, defConditions, patterns, check, names)
    
    def main(self, testConditions:list, defConditions:list, patterns:list, check:list, names:list):
        testConditionsG = []
        defConditionsG = []
        for testc,defc in iter(zip(testConditions, defConditions)):
            testcstr = self._and_.join(testc)
            groups = self.groupping(testcstr, patterns, check, names)
            testConditionsG.append(groups)
            defcstr = self._and_.join(defc)
            groups = self.groupping(defcstr, patterns, check, names)
            defConditionsG.append(groups)
        return testConditionsG, defConditionsG


    def groupping(self, predicate:str,patterns:list, check:list, names:list) -> dict:
        groups = dict()
        elements = []
        for pattern in patterns:
            predicate, element = self.manage_members(pattern, predicate)
            elements.append(element)
        for pattern in check:
            if(get_indexes(pattern, predicate)!=None):
                raise ValueError(f"Error en agrupador {predicate}")
        if(len(predicate)!=0):
            element = predicate.split(self._and_)
            elements.append(element)
        else:
            elements.append([])
        if(len(elements)==len(names)):
            for i in range(len(names)):
                groups[names[i]] = elements[i]
        else:
            raise ValueError("Grupos no concuerdan con el numero de clasificaciones")
        return groups
    

    def manage_members(self, pattern:str, predicate: str) -> tuple[str, list]:
        LOWER = 0
        UPPER = 1
        atoms = []
        logic = Operator('logic')
        indexes = get_indexes(pattern, predicate)
        if(indexes==None):
            return (predicate, atoms)
        else:
            atoms = [predicate[index[LOWER]:index[UPPER]] for index in indexes]
            predicate = replace_pattern( logic.and_ + pattern + logic.and_, self._and_, predicate)
            predicate = replace_pattern( logic.and_ + pattern , '', predicate)
            predicate = replace_pattern( pattern + logic.and_ , '', predicate)
            predicate = replace_pattern( pattern , '', predicate)
            return (predicate, atoms)