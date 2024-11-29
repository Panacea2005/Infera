import os
import subprocess
import sys
from time import sleep

def run_test_cases():
    # Specify the directory where the script is located
    directory = os.path.dirname(os.path.abspath(__file__))
    # List of methods for the command
    methods = ['TT', 'FC', 'BC', 'DPLL']
    # methods = ['TT', 'DPLL']

    # Number of test cases
    num_test_cases = 20

    # Get Python executable path
    python_executable = sys.executable

    # Print start of testing
    print("\n" + "="*50)
    print("Starting Test Cases Execution - Horn")
    print("="*50 + "\n")

    for case in range(num_test_cases):
        # filename = f'Horn_{case + 1}.txt'
        # filename = f'Generic_{case + 1}.txt'
        if case % 2 == 0:
            filename = f'testcase{case + 1}.txt'
            file_path = os.path.join(directory, filename)
            
            # Check if file exists before running
            if not os.path.exists(file_path):
                print(f"Warning: Test file {filename} not found. Skipping...")
                continue

            print(f"\nExecuting Test Case {case + 1}")
            print("-" * 30)

            for method in methods:
                command = f'"{python_executable}" iengine.py {filename} {method}'
                print(f"\nRunning {method} method:")
                
                try:
                    # Run the command and capture output
                    process = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate(timeout=30)  # 30 second timeout
                    
                    # Print the output
                    if process.returncode == 0:
                        if stdout:
                            print(stdout.strip())
                        else:
                            print("No output generated")
                    else:
                        print(f"Error: {stderr.strip()}")

                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"Error: Command timed out")
                except Exception as e:
                    print(f"Error running command: {e}")

                # Add a small delay between runs
                sleep(0.5)

            print("\n" + "-"*50)  # Separator between test cases

    print("\n" + "="*50)
    print("Testing Complete!")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        run_test_cases()
    except KeyboardInterrupt:
        print("\nTesting interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise