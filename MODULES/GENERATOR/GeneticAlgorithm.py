from MODULES.regex_patterns2 import Operator, Type

from MODULES.regex_functions import get_indexes, split_with_pattern, replace_pattern
from MODULES.GENERATOR.Individual import Individual
from MODULES.GENERATOR.auxiliary import Evaluate, Substitute, Quantifiers, FixedPoint, Flags
from MODULES.GENERATOR.Exceptions import UnoptimalIndividual

import numpy as np
from copy import deepcopy

class GeneticAlgorithm:
    __slots__ = ('N_WORDS','solution','solutiondict','DNUM','DELEM','DINDS','AND','OR','NONE','SET','REL')
    def __init__(self, parameters:dict, variables:list, types:list ,condition:dict):
        flags = Flags()
        fxp = FixedPoint(parameters['distance'])

        self.DNUM = flags.DOMAINNUM
        self.DELEM = flags.DOMAINELEMS
        self.DINDS = flags.DOMAININDS
        self.AND = flags.AND
        self.OR =  flags.OR
        self.NONE = flags.NONE
        self.SET = flags.SET
        self.REL = flags.REL

        self.N_WORDS = {'real':fxp.N_WORD_REAL,'int':fxp.N_WORD_INT,'nat':fxp.N_WORD_NAT, 'nat0':fxp.N_WORD_NAT, 'char':fxp.N_WORD_CHAR}
        self.solution = self.generate(parameters, variables, types, condition)
        self.solutiondict = {i:j for i,j in zip(variables, self.solution)}

    def generate(self, parameters:dict, variables:list, types:list, condition:dict):
        # parameters.keys() in {'n_population','m_probability', 'generations', 'distance'}
        bestindividual = None
        solved = False
        generation = 0

        lenghts = self.get_lenghts(types, variables, condition['function len'])
        genotypelenght = self.get_chrosome_lenght(types, lenghts)
        population = self.create_population(parameters['n_population'], types, parameters['distance'], lenghts)
        while(generation < parameters['generations']):
            
            #parameters['m_probability'] = 0.2 if generation >= 0.6*parameters['generations'] else parameters['m_probability']

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
            individual = Individual(types, distance)
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
        #indsprogenitor = np.random.choice(len(population), 2, p=probability)
        
        l = len(population)
        first = np.random.choice(l, p = probability)

        prob = probability[first]
        prob = prob/(l-1)
        probability_copy = [probability[i]+prob if i!=first else 0.0 for i in range(len(probability))]
        second = np.random.choice(l, p=probability_copy)

        return (first, second)


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
        typeobj = Type()
        counter = 0
        for i in range(len(types)):
            indexes = get_indexes(typeobj.seqof, types[i])
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
        opobj = Operator()
        pattern = rf"{opobj.less}|{opobj.greater}|{opobj.equality}|{opobj.le}|{opobj.ge}|{opobj.inequality}"
        indexes = get_indexes(pattern, atomicp)
        operator = atomicp[indexes[0][0]:indexes[0][1]]
        left, right = split_with_pattern(pattern, atomicp)
        error = Evaluate().relational(left, right, operator)
        return error

    def get_error_set(self, atomicp:str):
        opobj = Operator()
        pattern = rf"{opobj.inset}|{opobj.notin}"
        indexes = get_indexes(pattern, atomicp)
        operator = atomicp[indexes[0][0]:indexes[0][1]]
        left, right = split_with_pattern(pattern, atomicp)
        error = Evaluate().set(left, right, operator)
        return error

    def get_error_universal(self, atomic:str):
        # forall[ domain ] | P() <o> P() <o> ... <o> P();
        flags = Flags()
        universal = Quantifiers(atomic)

        errors = self.auxiliary_quantifier_error(universal)
        error = sum(errors) if universal.operator in {flags.AND, flags.NONE} else max(errors)
        return error
            
    def get_error_existential(self, atomic:str):
        # exists[ domain ] | P() <o> P() <o> ... <o> P().
        operatorobj = Operator()
        existential = Quantifiers(atomic)

        errors = self.auxiliary_quantifier_error(existential)
        error = min(errors)
        # Considera si existe una negación delante operador
        if(get_indexes(operatorobj.not_, atomic)):
            error = 0.0 if error>0.0 else 100
        return error


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
        operatorobj = Operator()
        typeobj = Type()

        lenghts = []
        for i in range(len(types)):
            indexes = get_indexes(typeobj.seqof, types[i])
            if(indexes==None):
                lenghts.append(1)
            else:
                pattern = rf'\b{variables[i]}\b'
                for func in groupfunc:
                    indexes = get_indexes(pattern,func)
                    if(indexes):
                        indexes = get_indexes(operatorobj.equality, func)
                        lenght = int(func[indexes[0][1]:])
                        lenghts.append(lenght)
                        break
        return lenghts
                        
    def auxiliary_quantifier_error(self,quantifier:Quantifiers)->list:
        operatorobj = Operator()

        functions = [self.get_error_set, self.get_error_relational]
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
            element = str(i) if quantifier.domaint in {self.DNUM, self.DINDS} else f"{quantifier.domain}[{i}]"
            try:
                for atom in quantifier.atoms:
                    funcinds = self.SET if get_indexes(operatorobj.inset+'|'+operatorobj.notin, atom) else self.REL
                    atom = replace_pattern(quantifier.itervar, element, atom)
                    error = functions[funcinds](atom)
                    errors_ += [error]
                errors.append(sum(errors_) if quantifier.operator in {self.AND, self.NONE} else min(errors_))
            except IndexError:
                pass
        return errors


