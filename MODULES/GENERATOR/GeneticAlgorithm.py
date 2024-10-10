from MODULES.regex_patterns import Operator, Types, Set
from MODULES.regex_functions import get_indexes, split_with_pattern, replace_pattern
from MODULES.GENERATOR.Individual import Individual
from MODULES.GENERATOR.auxiliary import Evaluate, Substitute, Quantifiers
from MODULES.GENERATOR.Exceptions import UnoptimalIndividual

import numpy as np
from copy import deepcopy

class GeneticAlgorithm:
    __slots__ = ('N_WORDS','solution','solutiondict')
    def __init__(self, parameters:dict, variables:list, types:list ,condition:dict):
        self.N_WORDS = {'real':32,'int':13,'nat':12, 'nat0':12, 'char':7}
        self.solution = self.generate(parameters, variables, types, condition)
        self.solutiondict = {i:j for i,j in zip(variables, self.solution)}

    def generate(self, parameters:dict, variables:list, types:list, condition:dict):
        # parameters.keys() in {'n_population','m_probability', 'generations', 'distance'}
        bestindividual = None
        solved = False
        generation = 0

        lenghts = self.get_lenghts(types, variables, condition['func len'])
        genotypelenght = self.get_chrosome_lenght(types, lenghts)
        population = self.create_population(parameters['n_population'], types, parameters['distance'], lenghts)
        while(generation < parameters['generations']):

            fitnessvector,indbest = self.get_fitness_vector(population,condition,variables)

            bestindividual = deepcopy(population[indbest])
            print(f"{generation} : {bestindividual.fenotype} : {fitnessvector[indbest]}")
            
            if(fitnessvector[indbest] == 1):
                solved = True
                break

            probabilityvector = self.get_probability_vector(fitnessvector)

            offspringsGenotype = self.crossing(population, probabilityvector, genotypelenght)
            
            self.mutation(offspringsGenotype, parameters['m_probability'])

            if(len(population)>parameters['n_population']):
                population = population[:parameters['n_population']]
            
            self.replacement(population, offspringsGenotype, lenghts)

            population += [bestindividual]

            generation += 1
        
        if(solved):
            return bestindividual.fenotype
        else:
            raise UnoptimalIndividual("No se encontraron soluciones")




    # Métodos para el GA
    def create_population(self, n_population:int, types:list, distance:int, lenghts:list):
        population = []
        for _ in range(n_population):
            individual = Individual(types)
            individual.create_progenitor(distance, lenghts)
            population.append(individual)
        return population

    def crossing(self, population:list[Individual], probability:list, genotypelenght:int):
        offspringGenotypes = []
        for _ in range(len(population)//2):
            parents = self.selection(population, probability)
            crossPoint = np.random.randint(genotypelenght)
            chromosmeCh1 = population[parents[0]].genotype[:crossPoint] + population[parents[1]].genotype[crossPoint:]
            chromosmeCh2 = population[parents[1]].genotype[:crossPoint] + population[parents[0]].genotype[crossPoint:] 
            offspringGenotypes += [chromosmeCh1]
            offspringGenotypes += [chromosmeCh2]
        return offspringGenotypes

    def mutation(self, offspringGenotypes:list, probability:float)->None:
        for i in range(len(offspringGenotypes)):
            for j in range(len(offspringGenotypes[i])):
                if(np.random.random()<probability):
                    condition = not int(offspringGenotypes[i][j])
                    if(condition):
                        offspringGenotypes[i][j] = "1"
                    else:
                        offspringGenotypes[i][j] = "0"

    def replacement(self, population:list, offspringGenotypes:list, lenghts:list)->None:
        for i in range(len(population)):
            population[i].create_offspring(offspringGenotypes[i], lenghts)

    def selection(self, population:list, probability:list)->tuple[int,int]:
        indsprogenitor = np.random.choice(len(population), 2, p=probability)
        return indsprogenitor


    def get_fitness_vector(self, population:list[Individual], group:dict, variables:list):
        normalized_fitness_vector = []
        maxfitness = float("-inf")
        indbest = -1
        for i in range(len(population)):
            individual = population[i]
            error = self.error_function(group, variables, individual.fenotype)
            fitness = 1/(error+1)
            if(fitness>maxfitness):
                maxfitness = fitness
                indbest = i
            normalized_fitness_vector.append(fitness)
        return normalized_fitness_vector, indbest
    
    def get_probability_vector(self, normalized_fitness_vector:list)->list:
        stochasticVector = np.array(normalized_fitness_vector.copy())
        stochasticVector = stochasticVector / stochasticVector.sum()
        stochasticVector = stochasticVector.tolist()
        return stochasticVector

    def get_chrosome_lenght(self, types:list, lenghts:list):
        counter = 0
        pattern = Types().seqof
        for i in range(len(types)):
            indexes = get_indexes(pattern, types[i])
            if(indexes):
                typee = types[i][indexes[0][1]:]
            else:
                typee = types[i]
            multiplier = lenghts[i]
            counter += self.N_WORDS[typee]*multiplier
        return counter


    # Calculo de los errores

    def get_error_relational(self, atomicp:str):
        # Método que sustituye en el predicado atómico relacional con la posible solución (presente en el fenotipo) y calcula su error 
        op = Operator('relational')
        pattern = rf"{op.less_}|{op.greater_}|{op.equality_}"
        indexes = get_indexes(pattern, atomicp)
        operator = atomicp[indexes[0][0]:indexes[0][1]]
        left, right = split_with_pattern(pattern, atomicp)
        error = Evaluate().relational(left, right, operator)
        return error

    def get_error_set(self, atomicp:str):
        op = Operator('set')
        pattern = rf"{op.inset_}|{op.notin_}"
        indexes = get_indexes(pattern, atomicp)
        operator = atomicp[indexes[0][0]:indexes[0][1]]
        left, right = split_with_pattern(pattern, atomicp)
        error = Evaluate().set(left, right, operator)
        return error

    def get_error_universal(self, atomic:str):
        # forall[ domain ] | P() <o> P() <o> ... <o> P().
        AND, OR, NONE = (1,2,3)
        FORALL, EXISTS = (1,2)
        universal = Quantifiers(atomic,FORALL)
        errors = self.auxiliary_quantifier_error(universal)
        return sum(errors) if universal.operator in {AND, NONE} else max(errors)
            
    def get_error_existential(self, atomic:str):
        # exists[ domain ] | P() <o> P() <o> ... <o> P().
        FORALL, EXISTS = (1,2)
        existential = Quantifiers(atomic,EXISTS)
        errors = self.auxiliary_quantifier_error(existential)
        return min(errors)


    def error_function(self, groups:dict, variables:list, fenotype:list):
        names = ['relational','set', 'universal generation','existential generation']
        functions = [self.get_error_relational, self.get_error_set, self.get_error_universal, self.get_error_existential]
        error = 0.0
        for i in range(len(names)):
            for atomicp in groups[names[i]]:
                atomicp = Substitute().substitute_values(atomicp, variables, fenotype)
                error += functions[i](atomicp)
        return error

    # Crear vector de longitudes
    def get_lenghts(self, types:list, variables:list, groupfunc:list)->list:
        equality = Operator('relational').equality_
        seqof = Types().seqof
        lenghts = []
        for i in range(len(types)):
            indexes = get_indexes(seqof, types[i])
            if(indexes==None):
                lenghts.append(1)
            else:
                pattern = rf'\b{variables[i]}\b'
                for func in groupfunc:
                    indexes = get_indexes(pattern,func)
                    if(indexes):
                        indexes = get_indexes(equality, func)
                        lenght = int(func[indexes[0][1]:])
                        lenghts.append(lenght)
                        break
                    else:
                        raise ValueError("No es una asignación")
        return lenghts
                        
    def auxiliary_quantifier_error(self,quantifier:Quantifiers)->list:
        inset = Set().in_
        notint = Set().not_
        DNUM, DELEM, DINDS = (1,2,3)
        AND, OR, NONE = (1,2,3)
        functions = [self.get_error_set, self.get_error_relational]
        SET,REL = [0,1]
        start = eval(quantifier.start.replace("\\", "\\\\"))
        end = eval(quantifier.end.replace("\\", "\\\\"))
        
        diff = end-start
        if(diff == 0):
            return [10]
        elif(diff < 0):
            return [10*abs(diff)]

        errors = list()
        for i in range(start, end):
            errors_ = list()
            element = str(i) if quantifier.domtype in {DNUM, DINDS} else f"{quantifier.domain}[{i}]"
            for atom in quantifier.atoms:
                funcinds = SET if get_indexes(inset+'|'+notint, atom) else REL
                atom = replace_pattern(quantifier.iterv, element, atom)
                error = functions[funcinds](atom)
                errors_ += [error]
            errors.append(sum(errors_) if quantifier.operator in {AND, NONE} else min(errors_))
        return errors


