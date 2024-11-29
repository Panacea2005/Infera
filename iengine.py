import sys
from sequence import TruthTable, ForwardChaining, BackwardChaining, DPLL

def parse_input_file(filename):
    """Parse the input file to extract KB and query."""
    try:
        with open(filename, 'r') as file:
            content = file.readlines()

            
        # Find the indices of TELL and ASK markers
        tell_index = -1
        ask_index = -1
        for i, line in enumerate(content):
            if line.strip() == 'TELL':
                tell_index = i
            elif line.strip() == 'ASK':
                ask_index = i
                
        if tell_index == -1 or ask_index == -1:
            raise ValueError("Input file must contain both TELL and ASK sections.")
            
        # Extract KB section (everything between TELL and ASK)
        kb_lines = content[tell_index + 1:ask_index]
        kb_str = ''.join(kb_lines).strip().replace(' ', '').replace('\n', '')
        
        # Extract query (everything after ASK)
        query_lines = content[ask_index + 1:]
        query = ''.join(query_lines).strip()
  
        # Split KB into clauses
        kb_clauses = [clause.strip() for clause in kb_str.split(';') if clause.strip()]
        
        return kb_clauses, query
        
    except FileNotFoundError:
        print(f'Error: File "{filename}" not found.')
        sys.exit(1)
    except Exception as e:
        print(f'Error parsing input file: {str(e)}')
        print(f"Debug - Error occurred at line: {sys.exc_info()[2].tb_lineno}")
        sys.exit(1)





def get_solver(method, kb_clauses):
    """Factory function to create appropriate solver instance."""
    solvers = {
        'TT': TruthTable,
        'FC': ForwardChaining,
        'BC': BackwardChaining,
        'DPLL': DPLL
    }
    
    solver_class = solvers.get(method)
    if not solver_class:
        raise ValueError(f"Invalid method. Please choose among: {list(solvers.keys())}")
    
    return solver_class(kb_clauses)

def main():
    # Validate command line arguments
    if len(sys.argv) != 3:
        print("Usage: python iengine.py <filename> <method>")
        sys.exit(1)
    filename = sys.argv[1]
    method = sys.argv[2].upper()
    
    try:
        kb_clauses, query = parse_input_file(filename)
        solver = get_solver(method, kb_clauses)
        
        result, additional_info = solver.solve(query)
        
        if result:
            if method == 'TT':
                print(f'YES: {additional_info}')  # additional_info is number of models
            elif method in ['FC', 'BC']:
                print(f'YES: {", ".join(additional_info)}')  # additional_info is list of symbols
            else:  # DPLL
                print('YES')
        else:
            print('NO')
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    # try:
    #     # Parse input and create solver
    #     kb_clauses, query = parse_input_file(filename)
    #     solver = get_solver(method, kb_clauses)
        
    #     # Solve and format output
    #     result, additional_info = solver.solve(query)
        
    #     if result:
    #         info_str = str(additional_info) if isinstance(additional_info, int) else ', '.join(additional_info)
    #         if method != 'DPLL':
    #             print(f'YES: {info_str}')
    #         else:
    #             print('YES')
    #     else:
    #         print("NO")
    # except Exception as e:
    #     print(f"Error: {str(e)}")
    #     sys.exit(1)


if __name__ == "__main__":
    main()