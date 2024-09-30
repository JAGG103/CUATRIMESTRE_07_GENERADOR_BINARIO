from MODULES.regex_patterns import Operator, Types
from MODULES.regex_functions import get_indexes,split_with_pattern,replace_pattern

from MODULES.GENERATOR.Individual import Individual
from MODULES.GENERATOR.auxiliary import Evaluate

import numpy as np
from copy import deepcopy

class GeneticAlgorithm:
    def __init__(self, parameters:dict, variables:list, types:list ,conditions:dict):
        self.N_WORDS = {'real':32,'int':13,'nat':12,'char':7}
        self.generate(parameters, variables, types, conditions)


    def generate(self, parameters:dict, variables:list, types:list, conditions:dict):
        # parameters.keys() in {'n_population','m_probability', 'generations', 'distance'}
        ivector = [0.03, 0.01, 0.005]
        ifitness = [1/20, 1/10, 1/2] # [1/8,1/4,1/2]
        bestindividual = None
        solved = False
        generation = 0

        lenghts = self.get_lenghts(types, variables, conditions['func len'])
        genotypelenght = self.get_chrosome_lenght(types, lenghts)
        population = self.create_population(parameters['n_population'], types, parameters['distance'], lenghts)
        while(generation < parameters['generations']):

            fitnessvector,indbest = self.get_fitness_vector(population,conditions,variables)

            bestindividual = deepcopy(population[indbest])
            print(f"{generation} : {bestindividual.fenotype} : {fitnessvector[indbest]}")
            
            if(fitnessvector[indbest] == 1):
                solved = True
                break
            elif(fitnessvector[indbest] >= ifitness[0] and fitnessvector[indbest]<ifitness[1] and parameters['m_probability']!=ivector[0]):
                parameters['m_probability'] = ivector[0]
                print("UP")
            elif(fitnessvector[indbest] >= ifitness[1] and fitnessvector[indbest]<ifitness[2] and parameters['m_probability'] != ivector[1]):
                parameters['m_probability'] = ivector[1]
                print("UP")
            elif(fitnessvector[indbest] >= ifitness[2] and parameters['m_probability'] != ivector[2]):
                parameters['m_probability'] = ivector[2]
                print("UP")

            probabilityvector = self.get_probability_vector(fitnessvector)

            offspringsGenotype = self.crossing(population, probabilityvector, genotypelenght)
            
            self.mutation(offspringsGenotype, parameters['m_probability'])

            if(len(population)>parameters['n_population']):
                population = population[:parameters['n_population']]
            
            self.replacement(population, offspringsGenotype, lenghts)

            population += [bestindividual]

            generation += 1
        
        print(bestindividual.fenotype, solved)




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

    def get_error_relational(self, atomicp:str, error:float):
        # Método que sustituye en el predicado atómico relacional con la posible solución (presente en el fenotipo) y calcula su error 
        op = Operator('relational')
        pattern = rf"{op.less_}|{op.greater_}|{op.equality_}"
        indexes = get_indexes(pattern, atomicp)
        operator = atomicp[indexes[0][0]:indexes[0][1]]
        left, right = split_with_pattern(pattern, atomicp)
        error += Evaluate().relational(left, right, operator)
        return error

    def get_error_set(self, atomicp:str, error:float):
        op = Operator('set')
        pattern = rf"{op.inset_}|{op.notin_}"
        indexes = get_indexes(pattern, atomicp)
        operator = atomicp[indexes[0][0]:indexes[0][1]]
        left, right = split_with_pattern(pattern, atomicp)
        error += Evaluate().set(left, right, operator)
        return error

    def get_error_universal_numeric(self):
        pass

    def get_error_existential_numeric(self):
        pass

    def get_error_universal_elems(self):
        pass

    def get_error_universal_inds(self):
        pass

    def error_function(self, groups:dict, variables:list, fenotype:list):
        names = ['relational','set']
        functions = [self.get_error_relational, self.get_error_set]
        error = 0.0
        for i in range(len(names)):
            for atomicp in groups[names[i]]:
                atomicp = Evaluate().substitute_values(atomicp, variables, fenotype)
                error += functions[i](atomicp, error)
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
                        
            


