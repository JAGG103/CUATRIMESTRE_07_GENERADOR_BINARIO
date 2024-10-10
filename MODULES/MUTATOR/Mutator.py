from MODULES.regex_functions import indexes_avoiding_head_and_tail
from MODULES.regex_patterns import Operator, Delimiters, Mutations

class Mutator:
    __slots__ = ('precondition','testConditions','defConditions')
    def __init__(self, precondition:list, testConditions:list[list], defConditions:list[list]):
        self.precondition = precondition
        self.testConditions = testConditions
        self.defConditions = defConditions
        self.main()
        

    def main(self):
        # Se extienden las condiciones de prueba manteniendo sus condiciones de definición originales
        #adjust = (2*len(self.precondition))-len(self.precondition)
        adjust = 0
        self.extend_testconditions_defconditions(adjust, self.testConditions, self.defConditions)
        # Se extienden las condiciones de definición manteniendo sus condiciones de prueba originales
        adjust = 0
        self.extend_testconditions_defconditions(adjust, self.defConditions, self.testConditions)


    def extend_testconditions_defconditions(self, adjust:int, targetConditions:list[list], fixedConditions:list[list])->None:
        relational = Operator('relational')
        delimiter = Delimiters('evaluation')
        mutation = Mutations()

        condition = True
        while(condition):
            condition = False
            for it in range(len(targetConditions)):
                if(condition):
                    break
                for i in range(adjust, len(targetConditions[it])):
                    extDict = {}
                    indexes_le = indexes_avoiding_head_and_tail([delimiter._evaluation],[delimiter.evaluation_], relational.le_, targetConditions[it][i])
                    indexes_ge = indexes_avoiding_head_and_tail([delimiter._evaluation],[delimiter.evaluation_], relational.ge_, targetConditions[it][i])
                    indexes_ne = indexes_avoiding_head_and_tail([delimiter._evaluation],[delimiter.evaluation_], relational.inequality_, targetConditions[it][i])
                    if(indexes_le):
                        extDict = self.extend_set_of_predicates(targetConditions[it], fixedConditions[it], i, indexes_le, mutation.less, mutation.equal)
                    elif(indexes_ge):
                        extDict = self.extend_set_of_predicates(targetConditions[it], fixedConditions[it], i, indexes_ge, mutation.greater, mutation.equal)
                    elif(indexes_ne):
                        extDict = self.extend_set_of_predicates(targetConditions[it], fixedConditions[it], i, indexes_ne, mutation.greater, mutation.less)
                    else:
                        pass

                    if(extDict!={}):
                        targetConditions.pop(it)
                        fixedConditions.pop(it)
                        targetConditions.insert(it, extDict['operationA'][0])
                        fixedConditions.insert(it, extDict['operationA'][1])
                        targetConditions.insert(it, extDict['operationB'][0])
                        fixedConditions.insert(it, extDict['operationB'][1])
                        condition = True
                        break
        
    def extend_set_of_predicates(self, obj:list, piv: list, i: int, indexes:str, extOpA:str, extOpB:str)->tuple[list, list]:
        ext_objA = obj.copy()
        elem = obj[i][:indexes[0][0]] + extOpA + obj[i][indexes[0][1]:]
        ext_objA[i] = elem
        ext_objB = obj.copy()
        elem = obj[i][:indexes[0][0]] + extOpB + obj[i][indexes[0][1]:]
        ext_objB[i] = elem
        output = {'operationA':(ext_objA, piv.copy()), 'operationB':(ext_objB, piv.copy())}
        return output