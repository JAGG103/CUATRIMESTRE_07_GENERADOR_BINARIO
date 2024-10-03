from MODULES.GENERATOR.GeneticAlgorithm import GeneticAlgorithm
from MODULES.GENERATOR.Exceptions import UnoptimalIndividual
# Aqui se trabajara con el algoritmo genético y algoritmo evaluador

class Generator:

    def __init__(self, parameters:dict, inport:dict, inaux:dict, outport:dict, outaux:dict, init:dict, testconditions:list[dict], defconditions:list[dict]):
        self.testcases = []
        self.main(parameters, inport, inaux, outport, outaux, init, testconditions, defconditions)

    def main(self, parameters:dict, inport:dict, inaux:dict, outport:dict, outaux:dict, init:dict, testconditions:list[dict], defconditions:list[dict]):
        for testcondition,defcondition in zip(testconditions, defconditions):
            tries = 0
            tc = []
            dc = []
            variablesI = inport['variables'] + inaux['variables']
            typesI = inport['types'] + inaux['types']
            variablesO = outport['variables'] + outaux['variables']
            typesO = outport['types'] + outaux['types']
            print(testcondition)
            print(defcondition)

            while(tries < parameters['tries']):
                try:
                    testvalues = GeneticAlgorithm(parameters, variablesI, typesI, testcondition, {})
                    tc.append(testvalues.solution)

                    testvalues = GeneticAlgorithm(parameters, variablesO, typesO, defcondition, testvalues.values)
                    tc.append(testvalues.solution)
                    break
                except UnoptimalIndividual:
                    print(f"Intento: {tries}")
                    tries += 1
        self.testcases.append(tc)
        self.testcases.append(dc)
            

            