from MODULES.GENERATOR.GeneticAlgorithm import GeneticAlgorithm
from MODULES.GENERATOR.EvaluationAlgorithm import EvaluationAlgorithm
# Aqui se trabajara con el algoritmo genético y algoritmo evaluador
from MODULES.GENERATOR.auxiliary import Substitute, Assignments


class Algorithm:

    def __init__(self, parameters:dict, port:dict, init:dict, condition:dict):
        self.main(parameters, port, init, condition)

    def main(self, parameters, port, init, condition):
        values = dict()
        # Resolver asignaciones
        values = Assignments().assignments(port['variables'],port['types'], condition['relational'])
        # Sustituir valores de las asignaciones
        for key in condition.keys():
            condition[key] = [Substitute().substitute_dict(values, predicate) for predicate in condition[key]]
        # Extraer las evaluaciones y dejar los demas grupos
        evaluations = condition['universal evaluation'].copy()
        del evaluations['universal evaluation']

        # Algoritmo genetico
        aux = [(v,t) for v,t in zip(port['variables'],port['types']) if v not in values.keys()]
        variables,types = [e[0] for e in aux],[[e[1] for e in aux]]
        ga = GeneticAlgorithm(parameters, variables, types, condition)
        values.update(ga.solutiondict)

        # Algoritmo evaluador de condiciones
        evaluations = [Substitute().substitute_dict(values, predicate) for predicate in evaluations]
        ea = EvaluationAlgorithm(evaluations, init)
