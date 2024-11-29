# COS30019 - Assignment 2 - Group 10
Team member: 
- Nguyen Le Truong Thien - 104974280
- Tran Pham Thanh Truc - 1048137072

## Introduction
Welcome to the COS30019 Assignement 2 repository of our Group 10.
This project is part of the COS30019 course and focuses on the implementation of various propositional logic inference methods. The aim is to provide a comprehensive toolset for logical reasoning using Python for the backend and JavaScript for the frontend. This assignment covers the following inference methods:
1. **Truth Table (TT)**: This method evaluates all possible truth values for a given propositional formula.
2. **Forward Chaining (FC)**: This approach starts with known facts and applies inference rules to extract more data until a goal is reached.
3. **Backward Chaining (BC)**: This method starts with a goal and works backward to determine which facts must be true to satisfy the goal.
4. **DPLL (Davis–Putnam–Logemann–Loveland)**: A backtracking-based search algorithm for deciding the satisfiability of propositional logic formulas in conjunctive normal form.

The project is structured into two main parts:

- **Backend**: Implemented in Python using FastAPI, responsible for processing logic and handling inference methods.
- **Frontend**: Implemented using modern JavaScript frameworks to provide a user-friendly interface for interacting with the inference methods.

This repository contains all the necessary scripts and documentation to set up and run the application locally. Users can upload their input files and select the desired inference method through the web interface, and the results will be displayed accordingly. 


## How to Run the Program

### Prerequisites
- Python 3.x
- FastAPI
- Uvicorn
- Node.js
### Running the Backend
1. Clone the repository:
   ```
   git clone https://github.com/thanhhhtruc/COS30019---Assign-2.git
   cd COS30019---Assign-2
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```
   uvicorn api:app --reload
   ```

### Running the Frontend
1. Open a new terminal and navigate to the UI directory:
   ```
   cd iengine-ui
   ```

2. Install the required Node packages (only needed for the initial setup):
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

### Using the Program for the CLI Mode
Open a new terminal and use the command:
    ```
    python iengine.py <filename> <method>
    ```

### Using the Program for the UI Mode
1. Open your web browser and navigate to `http://localhost:5173`.
2. Upload your input file and select the inference method (TT, FC, BC, or DPLL).
3. The results will be displayed on the UI.

## References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Node.js Documentation](https://nodejs.org/en/docs/)
