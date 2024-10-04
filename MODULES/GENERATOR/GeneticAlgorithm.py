from MODULES.regex_patterns import Operator, Types, Universal, Existential, Delimiters, Set
from MODULES.regex_functions import get_indexes, split_with_pattern, replace_pattern, get_indexes_blocks
from MODULES.GENERATOR.Individual import Individual
from MODULES.GENERATOR.auxiliary import Evaluate
from MODULES.GENERATOR.Exceptions import UnoptimalIndividual

import numpy as np
from copy import deepcopy

class GeneticAlgorithm:
    __slots__ = ('N_WORDS','solution','solutiondict')
    def __init__(self, parameters:dict, variables:list, types:list ,condition:dict):
        self.N_WORDS = {'real':32,'int':13,'nat':12,'char':7}
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
        pmiddle = Delimiters('middleQuan').middle
        pforall = Universal('generation')
        op = Operator('logic')
        sett = Set()
        AND,OR,NAO = 0,1,2
        DNU,DEL,DIN = 0,1,2
        operador = None
        domaintype = None
        atoms = list()

        # Contenido
        inds = get_indexes(pmiddle, atomic)
        content = atomic[inds[0][1]:-1]
        inds_and = get_indexes(op.and_, content)
        inds_or = get_indexes(op.or_, content)
        if(inds_and):
            operador = AND
            atoms = split_with_pattern(op.and_, content)
        elif(inds_or):
            operador = OR
            atoms = split_with_pattern(op.or_, content)
        else:
            operador = NAO
            atoms += [content]
        
        # iterable variable
        content = atomic[:inds[0][0]]
        inds = get_indexes(pforall.iterv, content)
        iterv = content[inds[0][0]:inds[0][1]]
        iterv = rf'\b{iterv}\b'
        # dominio
        inds_domnum = get_indexes_blocks(content, pforall._domainnum, pforall.domainnum_)
        inds_domele = get_indexes_blocks(content, pforall._domainelems, pforall.domainelems_)
        inds_domind = get_indexes_blocks(content, pforall._domaininds, pforall.domaininds_)
        if(inds_domnum):
            domain = content[inds_domnum[0][0]+1:inds_domnum[0][1]-1]
            start, end = split_with_pattern('(\.\.\.)', domain)
            domaintype = DNU
        elif(inds_domele):
            domain = content[inds_domele[0][0]+len('elems('):inds_domele[0][1]-len(')')]
            start, end = '0',f'len({domain})'
            domaintype = DEL
        elif(inds_domind):
            domain = content[inds_domind[0][0]+len('inds('):inds_domind[0][1]-len(')')]
            start, end = '0',f'len({domain})'
            domaintype = DIN
        else:
            raise ValueError("Dominios invalidos en cuantificador universal")

        # Sustitución
        accumerr = 0.0
        accumerrls = []
        functions = [self.get_error_set, self.get_error_relational]
        SET,REL = 0,1
        aux = None
        start = start.replace("\\", "\\\\")
        end = end.replace("\\", "\\\\")
        for i in range(eval(start), eval(end)):
            errormin = float("inf")
            for atom in atoms:
                inds = get_indexes(sett.in_ + r'|' + sett.not_, atom)
                if(inds):
                    aux = SET
                else:
                    aux = REL
                if(domaintype in {DNU, DIN}):
                    element = str(i)
                else:
                    element = f"{domain}[{i}]"
                atom = replace_pattern(iterv, element, atom)
                if(operador == AND):
                    error = functions[aux](atom)
                    accumerr += error
                elif(operador == OR):
                    error = functions[aux](atom)
                    if(error<errormin):
                        errormin = error
                else:
                    error = functions[aux](atom)
                    accumerr += error
            if(operador==OR):
                accumerrls += [errormin]
        if(operador==OR):
            return max(accumerrls)
        else:
            return accumerr

            
    def get_error_existential(self, atomic:str):
        # exists[ domain ] | P() <o> P() <o> ... <o> P().
        pmiddle = Delimiters('middleQuan').middle
        pexists = Existential('generation')
        op = Operator('logic')
        sett = Set()
        AND,OR,NAO = 0,1,2
        DNU,DEL,DIN = 0,1,2
        operador = None
        domaintype = None
        atoms = list()

        # Contenido
        inds = get_indexes(pmiddle, atomic)
        content = atomic[inds[0][1]:-1]
        inds_and = get_indexes(op.and_, content)
        inds_or = get_indexes(op.or_, content)
        if(inds_and):
            operador = AND
            atoms = split_with_pattern(op.and_, content)
        elif(inds_or):
            operador = OR
            atoms = split_with_pattern(op.or_, content)
        else:
            operador = NAO
            atoms += [content]
        
        # iterable variable
        content = atomic[:inds[0][0]]
        inds = get_indexes(pexists.iterv, content)
        iterv = content[inds[0][0]:inds[0][1]]
        iterv = rf'\b{iterv}\b'
        # dominio
        inds_domnum = get_indexes_blocks(content, pexists._domainnum, pexists.domainnum_)
        inds_domele = get_indexes_blocks(content, pexists._domainelems, pexists.domainelems_)
        inds_domind = get_indexes_blocks(content, pexists._domaininds, pexists.domaininds_)
        if(inds_domnum):
            domain = content[inds_domnum[0][0]+1:inds_domnum[0][1]-1]
            start, end = split_with_pattern('(\.\.\.)', domain)
            domaintype = DNU
        elif(inds_domele):
            domain = content[inds_domele[0][0]+len('elems('):inds_domele[0][1]-len(')')]
            start, end = '0',f'len({domain})'
            domaintype = DEL
        elif(inds_domind):
            domain = content[inds_domind[0][0]+len('inds('):inds_domind[0][1]-len(')')]
            start, end = '0',f'len({domain})'
            domaintype = DIN
        else:
            raise ValueError("Dominios invalidos en cuantificador existencial")

        # Sustitución
        accumerr = 0.0
        accumerrls = []
        functions = [self.get_error_set, self.get_error_relational]
        SET,REL = 0,1
        aux = None
        start = start.replace("\\", "\\\\")
        end = end.replace("\\", "\\\\")
        for i in range(eval(start), eval(end)):
            errormin = float("inf")
            accumerr = 0.0
            for atom in atoms:
                inds = get_indexes(sett.in_ + r'|' + sett.not_, atom)
                if(inds):
                    aux = SET
                else:
                    aux = REL
                if(domaintype in {DNU, DIN}):
                    element = str(i)
                else:
                    element = f"{domain}[{i}]"
                atom = replace_pattern(iterv, element, atom)
                if(operador == AND):
                    error = functions[aux](atom)
                    accumerr += error
                elif(operador == OR):
                    error = functions[aux](atom)
                    if(error<errormin):
                        errormin = error
                else:
                    error = functions[aux](atom)
                    accumerr += error
            if(operador==OR):
                accumerrls += [errormin]
            else:
                accumerrls += [accumerr]
        return min(accumerrls)


    def error_function(self, groups:dict, variables:list, fenotype:list):
        names = ['relational','set', 'universal generation','existential generation']
        functions = [self.get_error_relational, self.get_error_set, self.get_error_universal, self.get_error_existential]
        error = 0.0
        for i in range(len(names)):
            for atomicp in groups[names[i]]:
                atomicp = Evaluate().substitute_values(atomicp, variables, fenotype)
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
                        
            


