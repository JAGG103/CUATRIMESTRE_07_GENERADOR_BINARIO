from MODULES.GENERATOR.GeneticAlgorithm import GeneticAlgorithm
from MODULES.GENERATOR.EvaluationAlgorithm import EvaluationAlgorithm
from MODULES.GENERATOR.auxiliary import Substitute, Assignments, Evaluate

from MODULES.GENERATOR.Exceptions import UnoptimalIndividual

import copy

class Algorithm:
    __slots__ = ('init_', 'values')
    def __init__(self, parameters:dict, port:dict, init:dict, condition:dict):
        if(port['variables']==[] and port['types']==[]):
            self.init_ = init
            self.values = dict()
        else:
            self.main(parameters, port, init, condition)

    def main(self, parameters, port, init, condition):
        values = dict()
        evaluations = dict()
        condition_ = copy.deepcopy(condition)
        # Sustituir init en los predicados
        for key in condition_.keys():
            condition_[key] = [Substitute().substitute_pattern_notinside(init, predicate) for predicate in condition_[key]]

        # Resolver asignaciones
        values,condition_['relational'] = Assignments().assignments(port['variables'],port['types'], condition_['relational'])

        # Sustituir valores de las asignaciones
        for key in condition_.keys():
            condition_[key] = [Substitute().substitute_dict(values, predicate) for predicate in condition_[key]]

        # Extraer las evaluaciones y dejar los demas grupos
        for name in ['universal evaluation','existential evaluation']:
            evaluations[name] = condition_[name].copy()
            del condition_[name]

        # Algoritmo genetico
        aux = [(v,t) for v,t in zip(port['variables'],port['types']) if v not in values.keys()]
        variables,types = [e[0] for e in aux],[e[1] for e in aux]
        if(variables!=[] and types != []):
            ga = GeneticAlgorithm(parameters, variables, types, condition_)
            values.update(ga.solutiondict)
        
        # Evaluando los predicados restantes evitando contradicciones con posibles asignaciones en predicados relacionales
        error = Evaluate().satisfiability_relational(condition_['relational'], values)
        if error > 0.0:
            raise UnoptimalIndividual("Contradiccion en los predicados relacionales")
        
        # Algoritmo evaluador de condiciones
        for key in evaluations.keys():
            evaluations[key] = [Substitute().substitute_dict(values, predicate) for predicate in evaluations[key]]
        ea = EvaluationAlgorithm(evaluations, init)

        # Regresar valores
        self.init_ = ea.init_
        self.values = values

