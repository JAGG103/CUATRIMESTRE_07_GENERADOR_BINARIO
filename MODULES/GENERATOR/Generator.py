from MODULES.regex_functions import get_indexes

from MODULES.GENERATOR.Algorithm import Algorithm
from MODULES.GENERATOR.auxiliary import Substitute

from MODULES.GENERATOR.Exceptions import UnoptimalIndividual

import copy

class Generator:
    __slots__ = ('testcase_suite')
    def __init__(self, parameters:dict, inport:dict, inaux:dict, outport:dict, outaux:dict, init:dict, testconditions:list[dict], defconditions:list[dict]):
        self.main(parameters, inport, inaux, outport, outaux, init, testconditions, defconditions)

    def main(self, parameters:dict, inport:dict, inaux:dict, outport:dict, outaux:dict, init:dict, testconditions:list[dict], defconditions:list[dict]):
        testcase_suite = list()

        for testcondition,defcondition in zip(testconditions, defconditions):
            print(testcondition)
            print(defcondition)
            attempt = 0
            while(attempt < parameters['tries']):
                try:
                    variablesIn = inport['variables']
                    variablesOut = outport['variables']
                    tc_inaux, dc_outaux = copy.deepcopy(testcondition), copy.deepcopy(defcondition)
                    tc_inport, dc_outport = dict(), dict()
                    for key in testcondition.keys():
                        tc_inport[key], tc_inaux[key] = self.get_predicates_using_variables(tc_inaux[key], variablesIn)
                        dc_outport[key], dc_outaux[key] = self.get_predicates_using_variables(dc_outaux[key], variablesOut)
                    init_ = copy.deepcopy(init)
                    tcs = list()
                    values = dict()

                    # Resolviendo las variables del puerto auxiliar de entrada --------------------------------------------
                    a = Algorithm(parameters, inaux, init_, tc_inaux)
                    init_ = a.init_
                    values.update(a.values)

                    for key in tc_inport.keys():
                        tc_inport[key] = [Substitute().substitute_dict(values, predicate) for predicate in tc_inport[key]]
                    
                    # Resolviendo las variables del puerto de entrada --------------------------------------------
                    a = Algorithm(parameters, inport, init_, tc_inport)
                    init_ = a.init_
                    values.update(a.values)

                    for key in dc_outaux.keys():
                        dc_outaux[key] = [Substitute().substitute_dict(values, predicate) for predicate in dc_outaux[key]]
                    
                    # Resolviendo las variables del puerto auxiliar de salida --------------------------------------------
                    a = Algorithm(parameters, outaux, init_, dc_outaux)
                    init_ = a.init_
                    values.update(a.values)

                    for key in dc_outport.keys():
                        dc_outport[key] = [Substitute().substitute_dict(values, predicate) for predicate in dc_outport[key]]

                    # Resolviendo las variables del puerto de salida --------------------------------------------
                    a = Algorithm(parameters, outport, init_, dc_outport)
                    init_ = a.init_
                    values.update(a.values)

                    # Guardando los casos de prueba generados
                    testvalues = self.valuesdict_turn_into_valueslist(values, variablesIn)
                    expectedvalues = self.valuesdict_turn_into_valueslist(values, variablesOut)
                    tcs += [(list((testvalues, expectedvalues)))]
                    testvalues = self.valuesdict_turn_into_valuesdict(values, variablesIn)
                    expectedvalues = self.valuesdict_turn_into_valuesdict(values, variablesOut)
                    tcs += [(list((testvalues, expectedvalues)))]
                    testcase_suite += [tcs]
                    break
                except TypeError: # Unoptimal
                    attempt += 1
                    print(f"attempt: {attempt}")
            
        self.testcase_suite = testcase_suite
    
    def get_predicates_using_variables(self, predicates:list, variables:list)->tuple[list,list]:
        # Funcion que extrae predicados de 'predicates' si estos contienen alguna variable de 'variables' y regresa la lista de predicados que las contiene, eliminando esos elementos de 'predicates'
        container = list()
        targets = list()
        for i in range(len(predicates)):
            for variable in variables:
                pattern = rf'\b{variable}\b'
                inds = get_indexes(pattern, predicates[i])
                if(inds):
                    targets += [i]
                    break
        container = [e for i,e in enumerate(predicates) if i in targets]
        predicates = [e for i,e in enumerate(predicates) if i not in targets]
        return container, predicates
    
    def valuesdict_turn_into_valueslist(self, valuesdict:dict, variables:list)->list:
        valueslist = [valuesdict[variable] for variable in variables]
        return valueslist
    
    def valuesdict_turn_into_valuesdict(self, valuesdict:dict, variables:list)->dict:
        valuesdict_ = {variable:valuesdict[variable] for variable in variables}
        return valuesdict_
