from MODULES.GENERATOR.auxiliary import Quantifiers, Evaluate
from MODULES.regex_patterns import Operator
from MODULES.regex_functions import get_indexes, get_elements_notin_indexes, replace_pattern, split_with_pattern

class EvaluationAlgorithm:
    def __init__(self, evaluations:dict, init:dict):
        self.init_ = self.main(evaluations, init)
        

    def main(self,evaluations:dict, init:dict)->dict:
        for variable in init.keys():
            globals()[variable] = init[variable]

        functions = [self.evaluate_universal, self.evaluate_existential]
        names = ['universal evaluation','existential evaluation']
        for i in range(len(names)):
            for predicate in evaluations[names[i]]:
                functions[i](predicate, init)

        for variable in init.keys():
            init[variable] = eval(variable)
        return init
    

    def evaluate_existential(self, predicate:str, init_:dict):
        # Este operador realizara los efectos siempre que la causa se cumpla, el numero de veces que la implicación se cumpla
        FORALL,EXISTS = (1,2)
        existential = Quantifiers(predicate,EXISTS)
        self.auxiliary_existential(existential, init_)
            
    def evaluate_universal(self, predicate:str, init_:dict):
        # Este operador realizara el efecto una vez si se cumple el efecto.
        FORALL,EXISTS = (1,2)
        universal = Quantifiers(predicate,FORALL)
        self.auxiliary_universal(universal, init_,)


    def auxiliary_existential(self, quantifier:Quantifiers, init_:dict):
        # Función auxiliar que utiliza un objeto de la clase 'Quantifiers' para obtener información de este predicado, obtener las causas y efectos, para posteriormente evaluar
        AND, OR, NONE = (1,2,3)
        DNUM, DELEM, DINDS = (1,2,3)
        SET,REL = [0,1]
        inset = Operator('set').inset_
        notin = Operator('set').notin_

        for atom in quantifier.atoms:
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
            start = eval(quantifier.start)
            end = eval(quantifier.end.replace("\\", "\\\\"))
            errors = list()
            for i in range(start, end):
                errors_ = list()
                element = str(i) if quantifier.domtype in {DNUM, DINDS} else f"{quantifier.domain}[{i}]"
                for atom in subatoms:
                    atom = replace_pattern(quantifier.iterv, element, atom)
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
            error = min(errors)
            self.auxiliary_evaluations(efect, init_.keys(), error)


    def auxiliary_universal(self, quantifier:Quantifiers, init_:dict):
        # Función auxiliar que utiliza un objeto de la clase 'Quantifiers' para obtener información de este predicado, obtener las causas y efectos, para posteriormente evaluar
        AND, OR, NONE = (1,2,3)
        DNUM, DELEM, DINDS = (1,2,3)
        SET,REL = [0,1]
        inset = Operator('set').inset_
        notin = Operator('set').notin_

        start = eval(quantifier.start)
        end = eval(quantifier.end.replace("\\", "\\\\"))
        errors = list()
        # Iteración sobre los elementos del dominio
        for i in range(start, end):
            element = str(i) if quantifier.domtype in {DNUM, DINDS} else f"{quantifier.domain}[{i}]"
            # Iteración sobre los Conjuntivos (evaluaciones)
            for atom in quantifier.atoms:
                errors_ = list()
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
                
                for atom in subatoms:
                    option = SET if get_indexes(inset+'|'+notin, atom) else REL
                    atom = replace_pattern(quantifier.iterv, element, atom)
                    opr, ops = Operator('relational'), Operator('set')
                    pattern = rf"{opr.less_}|{opr.greater_}|{opr.equality_}|{ops.inset_}|{ops.notin_}"
                    inds = get_indexes(pattern, atom)
                    operator_ = atom[inds[0][0]:inds[0][1]]
                    left, right = split_with_pattern(pattern, atom)
                    error_ = Evaluate().relational_eval(left, right, operator_, init_) if option==REL else Evaluate().set_eval(left, right, operator_, init_)
                    errors_ += [error_]
                error = sum(errors_) if operator in {AND, NONE} else min(errors_)
                self.auxiliary_evaluations(efect, init_.keys(), error)


    def auxiliary_evaluations(self, efect:str, globvars:list, error:float):
        # Función que permite modificar los valores de las variables globales dentro de las evaluaciones
        if(error == 0.0):
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

