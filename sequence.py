from typing import List, Set, Dict, Tuple, Union, Optional
from enum import Enum
import re, sys
from abc import ABC, abstractmethod

class LogicalConnective(Enum):
    """Enumeration of logical connectives with their symbols and descriptions.""" 
    NEGATION = ('~', 'negation')
    CONJUNCTION = ('&', 'conjunction')
    DISJUNCTION = ('||', 'disjunction')
    IMPLICATION = ('=>', 'implication')
    BICONDITIONAL = ('<=>', 'biconditional')
    
    def __init__(self, symbol: str, description: str):
        self.symbol = symbol
        self.description = description
    
    @classmethod
    def get_all_symbols(cls):   # -> Set[str]
        """Get all logical connective symbols."""
        return {member.symbol for member in cls}
    
    @classmethod
    def get_operator_pattern(cls):  # -> str
        """Get regex pattern for matching logical operators."""
        # Escape special characters and join with OR
        return '|'.join(re.escape(member.symbol) for member in cls)

class KnowledgeBase:
    """Class to manage the knowledge base and provide common utility functions."""
    
    def __init__(self, clauses: List[str]):
        """Initialize knowledge base with a list of clauses."""
        self.clauses = clauses
        self.symbols = self._extract_symbols()
        self.horn_clauses = self._parse_horn_clauses()
        self.is_horn_form = self._check_horn_form()
    
    def _extract_symbols(self):  # -> Set[str]
        """Extract all unique propositional symbols from the KB."""
        # Get pattern for all operators
        op_pattern = LogicalConnective.get_operator_pattern()
        # Split by operators and filter out empty strings
        symbols = set()
        for clause in self.clauses:
            # Replace operators with spaces
            cleaned = re.sub(op_pattern, ' ', clause)
            
            # Extract symbols (alphanumeric strings)
            symbols.update(token for token in cleaned.split() if token.isalnum() and not token.isnumeric())
        return symbols
    
    def _check_horn_form(self): # -> bool
        """Check if the knowledge base is in Horn form."""
        for clause in self.clauses:
            if '||' in clause or '<=>' in clause:
                return False
            if '=>' in clause:
                antecedent = clause.split('=>')[0]
                if '~' in antecedent:
                    return False
        return True
    
    def _parse_horn_clauses(self):
        """Parse all clauses from the knowledge base into premises and conclusions."""
        parsed_clauses = []
        
        for clause in self.clauses:
            # Skip non-Horn clauses for parsing
            if '||' in clause or '<=>' in clause:
                continue
                
            if '=>' in clause:
                try:
                    premises, conclusion = clause.split('=>')
                    premises = premises.split('&') if '&' in premises else [premises]
                    parsed_clauses.append(
                        ([premise.strip() for premise in premises], 
                        conclusion.strip())
                    )
                except ValueError:
                    print(f"Error parsing clause: {clause}")
                    continue
            else:
                # Handle simple facts
                clauses_split = [c.strip() for c in clause.split('&') if c.strip()]
                for c in clauses_split:
                    if '~' not in c:  # Skip negated facts
                        parsed_clauses.append(([], c.strip()))
                    
        return parsed_clauses

class InferenceEngine(ABC):
    """Abstract base class for inference engines."""
    
    def __init__(self, clauses: List[str]):
        try:
            self.kb = KnowledgeBase(clauses)
            
            # Skip Horn form validation for DPLL and TT methods
            if not isinstance(self, (DPLL, TruthTable)) and not self.kb.is_horn_form:
                print(f"Error: Knowledge base contains non-Horn clauses. Found:")
                for clause in clauses:
                    if '||' in clause or '<=>' in clause or ('=>' in clause and '~' in clause.split('=>')[0]):
                        print(f"  - {clause}")
                print("\nOnly TT (truth table) method and DPLL can be used with non-Horn clauses.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error initializing knowledge base: {str(e)}")
            sys.exit(1)
    
    @abstractmethod
    def solve(self, query: str):
        """Solve the inference problem."""
        pass



class TruthTable(InferenceEngine):
    """Truth table checking algorithm implementation with visualization."""
    
    def _evaluate_clause(self, clause: str, model: Dict[str, bool]):
        """Evaluate a single clause given a model."""
        # Replace symbols with their boolean values
        expr = clause
        for symbol, value in model.items():
            expr = re.sub(r'\b' + re.escape(symbol) + r'\b', str(value), expr)
        
        try:
            # Handle implications first
            while '=>' in expr:
                antecedent, consequent = expr.split('=>', 1)
                antecedent_value = self._evaluate_boolean_expr(antecedent)
                consequent_value = self._evaluate_boolean_expr(consequent)
                expr = str(not antecedent_value or consequent_value)
            
            return self._evaluate_boolean_expr(expr)
            
        except Exception as e:
            print(f"Error evaluating clause '{clause}': {str(e)}")
            return False
    
    def _evaluate_boolean_expr(self, expr: str):
        """Evaluate a boolean expression."""
        expr = expr.strip()
        
        # Handle special case where the expression is already a boolean
        if expr.lower() == 'true':
            return True
        if expr.lower() == 'false':
            return False
            
        expr = expr.replace('&', ' and ').replace('||', ' or ').replace('~', ' not ')
        try:
            return bool(eval(expr))
        except:
            return False

    def get_truth_table(self, query: str):
        """Generate complete truth table data."""
        # Get sorted list of symbols
        symbols = sorted(list(self.kb.symbols))
        n_symbols = len(symbols)
        total_models = 2 ** n_symbols
        
        # Initialize truth table data
        truth_table = {
            'symbols': symbols,
            'clauses': self.kb.clauses,
            'query': query,
            'rows': []
        }
        
        # Generate all possible models
        kb_sat_count = 0
        proving_count = 0
        
        for i in range(total_models):
            # Create model
            model = {}
            for j, symbol in enumerate(symbols):
                model[symbol] = bool((i >> j) & 1)
            
            # Evaluate clauses and query
            kb_results = []
            kb_satisfied = True
            for clause in self.kb.clauses:
                result = self._evaluate_clause(clause, model)
                kb_results.append(result)
                if not result:
                    kb_satisfied = False
            
            query_result = self._evaluate_clause(query, model)
            
            if kb_satisfied:
                kb_sat_count += 1
                if query_result:
                    proving_count += 1
            
            # Add row to truth table
            row = {
                'model': model,
                'kb_results': kb_results,
                'kb_satisfied': kb_satisfied,
                'query_result': query_result,
                'proves_query': kb_satisfied and query_result
            }
            truth_table['rows'].append(row)
        
        # Calculate summary
        truth_table['summary'] = {
            'total_models': total_models,
            'proving_models': proving_count,
            'is_entailed': kb_sat_count > 0 and proving_count == kb_sat_count
        }
        
        return truth_table
    

    def solve(self, query: str): #  -> Tuple[bool, int]
        """Solve a propositional logic query using the truth table method.
    
        Args:
            query (str): The logical expression to evaluate against the knowledge base
            
        Returns:
            Tuple[bool, int]: A tuple containing:
                - bool: Whether the query is entailed by the knowledge base
                - int: Number of models that prove the query
        """
       # Generate complete truth table and extract results
        truth_table = self.get_truth_table(query)
        
        # Return whether query is entailed and number of proving models
        return (truth_table['summary']['is_entailed'], 
                truth_table['summary']['proving_models'])

        
class ChainingSolver(InferenceEngine):
    """Base class for chaining algorithms with common functionality."""
    
    def __init__(self, clauses: List[str]):
        super().__init__(clauses)
        self.entailed = []
        self.steps = [] # Track reasoning steps
        
    def _get_facts(self): # -> Set[str]
        """Get initial facts from the knowledge base."""
        return {conclusion for premises, conclusion in self.kb.horn_clauses if not premises}
    
    def _add_step(self, fact: str, reasoning: str, known_facts: List[str] = None):
        """Add a reasoning step with explanation."""
        step = {
            'fact': fact,
            'reasoning': reasoning,
            'known_facts': known_facts or []
        }
        self.steps.append(step)

class ForwardChaining(ChainingSolver):
    """Forward chaining algorithm implementation."""
    
    def _find_next_conclusion(self, rules, known_facts):
        """
        Find the next conclusion that can be derived, prioritizing simpler rules.
        """
        candidate_rules = []
        
        # First, gather all rules whose premises are satisfied
        for premises, conclusion in rules:
            if conclusion not in known_facts and all(p in known_facts for p in premises):
                # Calculate rule complexity (number of premises)
                complexity = len(premises)
                candidate_rules.append((complexity, premises, conclusion))
        
        if not candidate_rules:
            return None, None
            
        # Sort by complexity (fewer premises first)
        candidate_rules.sort(key=lambda x: x[0])
        _, premises, conclusion = candidate_rules[0]
        return premises, conclusion
    
    def solve(self, query: str):
        """
        Implement the forward chaining algorithm to determine if a query can be proven.
        
        Args:
            query: The query to prove
            
        Returns:
            Tuple of (whether query was proven, list of facts derived in order)
        """
        # Initialize with facts
        self.entailed = []
        self.steps = []
        
        # Initialize with facts
        facts = self._get_facts()
        for fact in sorted(facts):
            self.entailed.append(fact)
            self._add_step(
                fact=fact,
                reasoning="Initial fact from knowledge base",
                known_facts=self.entailed[:-1]
            )
            
        # Get rules (excluding pure facts)
        rules = [(premises, conclusion) 
                for premises, conclusion in self.kb.horn_clauses 
                if premises]
        
        while True:
            # Find next applicable rule based on current knowledge
            premises, conclusion = self._find_next_conclusion(rules, self.entailed)
            
            if conclusion is None:  # No more rules can be applied
                break
                
            # Apply the rule
            if conclusion not in self.entailed:
                self.entailed.append(conclusion)
                self._add_step(
                    fact=conclusion,
                    reasoning=f"Derived using: {' AND '.join(premises)}",
                    known_facts=self.entailed[:-1]
                )
            
            # Remove the used rule to prevent cyclic inference
            rules.remove((premises, conclusion))
                
        return query in self.entailed, self.entailed


class BackwardChaining(ChainingSolver):
    """Backward chaining algorithm implementation."""
    
    def _can_prove(self, query: str, visited: Set[str]): # -> bool
        """Try to prove a query using backward chaining."""
        if query in visited:
            return False
       
        visited.add(query)
        
        # Check if query is a fact
        if query in self._get_facts():
            self._add_step(
                fact=query,
                reasoning="Known fact from knowledge base",
                known_facts=self.entailed
            )
            if query not in self.entailed:
                self.entailed.append(query)
            return True
        
        
        # Try to prove through implications
        for premises, conclusion in self.kb.horn_clauses:
            if conclusion == query:
                all_premises_proven = True
                required_premises = []
                
                for premise in premises:
                    if not self._can_prove(premise, visited.copy()):
                        all_premises_proven = False
                        break
                    required_premises.append(premise)
                
                if all_premises_proven:
                    self._add_step(
                        fact=query,
                        reasoning=f"Proved using: {' AND '.join(required_premises)}",
                        known_facts=self.entailed
                    )
                    if query not in self.entailed:
                        self.entailed.append(query)
                    return True
        
        return False
        
        
    def solve(self, query: str): # -> Tuple[bool, List[str]]
        # self.entailed = set()
        self.entailed = []
        self.steps = []
        # Add initial goal step
        self._add_step(
            fact=query,
            reasoning="Initial goal to prove",
            known_facts=[]
        )
        result = self._can_prove(query, set())
        
        return result, self.entailed




class DPLL(InferenceEngine):
    """DPLL (Davis-Putnam-Logemann-Loveland) algorithm implementation."""
    
    #_____________________________ Horn 3 and Gen 1 not correct _____________________________ 
    def _parse_cnf_clauses(self, clause_str: str): #  -> List[List[Tuple[str, str]]]
        """Convert input clause string to CNF format."""
        input_clauses = [c.strip() for c in clause_str.split(';') if c.strip()]
        result_clauses = []

        for clause in input_clauses:
            if not clause:
                continue

            clause = clause.strip('() ')

            # print(f"Parsing clause: {clause}")  # Debug statement

            if '<=>' in clause:
                p, q = clause.split('<=>', 1)
                p, q = p.strip(), q.strip()
                clause1 = f'~{p}||{q}'
                clause2 = f'{p}||~{q}'
                # print(f"Handling biconditional: {clause} as {clause1} and {clause2}")  # Debug statement
                result_clauses.extend(self._parse_cnf_clauses(clause1))
                result_clauses.extend(self._parse_cnf_clauses(clause2))
                continue

            if '=>' in clause:
                p, q = clause.split('=>', 1)
                p, q = p.strip(), q.strip()
                clause = f'~{p}||{q}'
                # print(f"Handling implication: {clause}")  # Debug statement

            literals = []
            for lit in clause.split('||'):
                lit = lit.strip()
                if lit.startswith('~'):
                    literals.append(('-', lit[1:].strip()))
                else:
                    literals.append(('+', lit.strip()))

            if literals:
                # print(f"Adding literals: {literals}")  # Debug statement
                result_clauses.append(literals)

        return result_clauses
    
    
    # _____________________________ All Horn test cases are correct, but the genenric is not correct _____________________________ 
    # def _parse_cnf_clauses(self, clause_str: str): #  -> List[List[Tuple[str, str]]]
    #     """Convert input clause string to CNF format."""
    #     # First split the input into individual clauses (split on &)
    #     input_clauses = [c.strip() for c in clause_str.split('&')]
    #     result_clauses = []
        
    #     for clause in input_clauses:
    #         # Handle empty clauses
    #         if not clause:
    #             continue
                
    #         # Remove outer parentheses if they exist
    #         clause = clause.strip('() ')
            
    #         # Handle biconditional (P <=> Q)
    #         if '<=>' in clause:
    #             p, q = clause.split('<=>')
    #             p, q = p.strip(), q.strip()
    #             # Convert P <=> Q to (~P || Q) & (P || ~Q)
    #             clause1 = f'~{p}||{q}'
    #             clause2 = f'{p}||~{q}'
    #             result_clauses.extend(self._parse_cnf_clauses(clause1))
    #             result_clauses.extend(self._parse_cnf_clauses(clause2))
    #             continue
            
    #         # Handle implication (P => Q)
    #         if '=>' in clause:
    #             p, q = clause.split('=>')
    #             p, q = p.strip(), q.strip()
    #             # Convert P => Q to ~P || Q
    #             clause = f'~{p}||{q}'
            
    #         # Handle disjunctions
    #         literals = []
    #         for lit in clause.split('||'):
    #             lit = lit.strip()
    #             if lit.startswith('~'):
    #                 literals.append(('-', lit[1:].strip()))
    #             else:
    #                 literals.append(('+', lit.strip()))
                    
    #         if literals:
    #             result_clauses.append(literals)
                
    #     return result_clauses
    
    
    

    def _evaluate_clause(self, clause: List[Tuple[str, str]], assignment: Dict[str, bool]): #  -> Optional[bool]
        """Evaluate a clause given an assignment."""
        clause_value = False
        for sign, var in clause:
            if var in assignment:
                if (sign == '+' and assignment[var]) or (sign == '-' and not assignment[var]):
                    return True
            else:
                return None  # Undetermined
        return False

    def _eval_formula(self, clauses: List[List[Tuple[str, str]]], assignment: Dict[str, bool]): #  -> Optional[bool]
        """Evaluate entire formula under an assignment."""
        results = []
        for clause in clauses:
            val = self._evaluate_clause(clause, assignment)
            if val is False:
                return False
            if val is not None:
                results.append(val)
        if len(results) == len(clauses):
            return all(results)
        return None

    def _dpll_solve(self, clauses: List[List[Tuple[str, str]]], assignment: Dict[str, bool], symbols: Set[str], steps: List[str]): #  -> bool
        """Core DPLL recursive algorithm."""
        eval_result = self._eval_formula(clauses, assignment)
        steps.append(f"Evaluating formula: {eval_result}")
        if eval_result is True:
            return True
        if eval_result is False:
            return False

        if not symbols:
            return False

        var = next(iter(symbols))
        remaining_symbols = symbols - {var}

        assignment_true = assignment.copy()
        assignment_true[var] = True
        steps.append(f"Trying {var} = True")
        if self._dpll_solve(clauses, assignment_true, remaining_symbols, steps):
            assignment.update(assignment_true)
            return True

        assignment_false = assignment.copy()
        assignment_false[var] = False
        steps.append(f"Trying {var} = False")
        if self._dpll_solve(clauses, assignment_false, remaining_symbols, steps):
            assignment.update(assignment_false)
            return True

        return False

    def solve(self, query: str): #  -> Tuple[bool, Dict[str, Union[bool, List[str]]]]
        """
        Solve using DPLL algorithm.
        Args:
            query: The query to prove
        Returns:
            Tuple of (whether query is entailed, assignments with steps)
        """
        kb_clauses = []
        for clause in self.kb.clauses:
            kb_clauses.extend(self._parse_cnf_clauses(clause))

        query_clauses = self._parse_cnf_clauses(query)
        negated_query = []
        for clause in query_clauses:
            negated = [('+' if sign == '-' else '-', lit) for sign, lit in clause]
            negated_query.append(negated)

        all_clauses = kb_clauses + negated_query

        symbols = set()
        for clause in all_clauses:
            for _, var in clause:
                symbols.add(var)

        assignment = {}
        steps = []
        is_sat = self._dpll_solve(all_clauses, assignment, symbols, steps)
        assignment['steps'] = steps

        return (not is_sat, assignment)

