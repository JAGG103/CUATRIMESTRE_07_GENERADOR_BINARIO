from MODULES.GENERATOR.auxiliary import Quantifiers, Evaluate
from MODULES.regex_patterns import Operator
from MODULES.regex_functions import get_indexes, get_elements_notin_indexes, replace_pattern, split_with_pattern

class EvaluationAlgorithm:
    def __init__(self, evaluations:dict, init:dict):
        self.init_ = self.main(evaluations, init)
        

    def main(self,evaluations:dict, init:dict):
        
        for variable in init.keys():
            globals()[variable] = init[variable]

        functions = [self.evaluate_universal, self.evaluate_existential]
        names = ['universal evaluation','existential evaluation']

        for i in range(len(names)):
            for predicate in evaluations[names[i]]:
                functions[i](predicate, init.keys())

        for variable in init.keys():
            init[variable] = eval(variable)
        return init
    
    def evaluate_existential(self, predicate:str, globvars:list):
        FORALL,EXISTS = (1,2)
        AND, OR, NONE = (1,2,3)
        DNUM, DELEM, DINDS = (1,2,3)
        SET,REL = [0,1]
        existential = Quantifiers(predicate,EXISTS)
        inset = Operator('set').inset_
        notin = Operator('set').notin_

        for atom in existential.atoms:
            op = Operator('logic')
            atom = atom[1:-1]
            inds = get_indexes(op.implies_, atom)
            causes = atom[:inds[0][0]]
            efect = atom[inds[0][1]:]

            inds_and = get_indexes(op.and_, causes)
            inds_or = get_indexes(op.or_, causes)
            if(inds_and):
                subatoms, operator = get_elements_notin_indexes(inds_and, causes), AND
            elif(inds_or):
                subatoms, operator = get_elements_notin_indexes(inds_or, causes), OR
            else:
                subatoms, operator = [causes], NONE
        
            start = eval(existential.start)
            end = eval(existential.end.replace("\\", "\\\\"))
            errors = list()
            for i in range(start, end):
                errors_ = list()
                element = str(i) if existential.domtype in {DNUM, DINDS} else f"{existential.domain}[{i}]"
                for atom in subatoms:
                    atom = replace_pattern(existential.iterv, element, atom)
                    option = SET if get_indexes(inset+'|'+notin, atom) else REL
                    if(option == REL):
                        op = Operator('relational')
                        pattern = rf"{op.less_}|{op.greater_}|{op.equality_}"
                    elif(option == SET):
                        op = Operator('set')
                        pattern = rf"{op.inset_}|{op.notin_}"
                    inds = get_indexes(pattern, atom)
                    operator_ = atom[inds[0][0]:inds[0][1]]
                    left, right = split_with_pattern(pattern, atom)
                    error_ = Evaluate().relational(left, right, operator_) if option==REL else Evaluate().set(left, right, operator_)
                    errors_ += [error_] 
                errors.append(sum(errors_) if operator in {AND, NONE} else min(errors_))
            #error = min(errors)
            #if(error == 0.0):
            executions = errors.count(0.0)
            for _ in range(executions):
                equality = Operator('relational').equality_
                left, right = split_with_pattern(equality, efect)
                for globvar in globvars:
                    modvar = rf"{globvar}(?!\[)"
                    modele = rf"{globvar}(?=\[)"
                    inds_modvar = get_indexes(modvar, left)
                    inds_modele = get_indexes(modele, left)
                    if(inds_modvar):
                        globals[globvar] = eval(right)
                    elif(inds_modele):
                        pinds = r"(?<=\[)\d+(?=\])"
                        inds = get_indexes(pinds, left)
                        position = left[inds[0][0]:inds[0][1]]
                        globals()[globvar][int(position)] = eval(right)

    def evaluate_universal(self, predicate:str, globvars:list):
        FORALL,EXISTS = (1,2)
        AND, OR, NONE = (1,2,3)
        DNUM, DELEM, DINDS = (1,2,3)
        SET,REL = [0,1]
        universal = Quantifiers(predicate,FORALL)

        inset = Operator('set').inset_
        notin = Operator('set').notin_

        for atom in universal.atoms:
            op = Operator('logic')
            atom = atom[1:-1]
            inds = get_indexes(op.implies_, atom)
            causes = atom[:inds[0][0]]
            efect = atom[inds[0][1]:]

            inds_and = get_indexes(op.and_, causes)
            inds_or = get_indexes(op.or_, causes)
            if(inds_and):
                subatoms, operator = get_elements_notin_indexes(inds_and, causes), AND
            elif(inds_or):
                subatoms, operator = get_elements_notin_indexes(inds_or, causes), OR
            else:
                subatoms, operator = [causes], NONE
        
            start = eval(universal.start)
            end = eval(universal.end.replace("\\", "\\\\"))
            errors = list()
            for i in range(start, end):
                errors_ = list()
                element = str(i) if universal.domtype in {DNUM, DINDS} else f"{universal.domain}[{i}]"
                for atom in subatoms:
                    atom = replace_pattern(universal.iterv, element, atom)
                    option = SET if get_indexes(inset+'|'+notin, atom) else REL
                    if(option == REL):
                        op = Operator('relational')
                        pattern = rf"{op.less_}|{op.greater_}|{op.equality_}"
                    elif(option == SET):
                        op = Operator('set')
                        pattern = rf"{op.inset_}|{op.notin_}"
                    inds = get_indexes(pattern, atom)
                    operator_ = atom[inds[0][0]:inds[0][1]]
                    left, right = split_with_pattern(pattern, atom)
                    error_ = Evaluate().relational(left, right, operator_) if option==REL else Evaluate().set(left, right, operator_)
                    errors_ += [error_] 
                errors.append(sum(errors_) if operator in {AND, NONE} else min(errors_))
            
            #error = sum(errors) if universal.operator in {AND, NONE} else max(errors)
            #if(error == 0.0):
            executions = errors.count(0.0)
            for _ in range(executions):
                equality = Operator('relational').equality_
                left, right = split_with_pattern(equality, efect)
                for globvar in globvars:
                    modvar = rf"{globvar}(?!\[)"
                    modele = rf"{globvar}(?=\[)"
                    inds_modvar = get_indexes(modvar, left)
                    inds_modele = get_indexes(modele, left)
                    if(inds_modvar):
                        globals[globvar] = eval(right)
                    elif(inds_modele):
                        pinds = r"(?<=\[)\d+(?=\])"
                        inds = get_indexes(pinds, left)
                        position = left[inds[0][0]:inds[0][1]]
                        globals()[globvar][int(position)] = eval(right)


    def auxiliary_evaluation(self):
        pass