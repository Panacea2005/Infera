from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
from iengine import parse_input_file, get_solver

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process")
async def process_file(file: UploadFile, method: str = Form(...)):
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Parse the input file and create the solver
        kb_clauses, query = parse_input_file(tmp_file_path)
        solver = get_solver(method, kb_clauses)

        # Solve the query
        result, additional_info = solver.solve(query)
        
        response_data = {}
        
        # Format the result string
        if result:
            info_str = str(additional_info) if isinstance(additional_info, int) else ', '.join(additional_info)
            response_data["result"] = f'YES: {info_str}'
        else:
            response_data["result"] = "NO"
            
        # If using TT method, include truth table data
        if method == "TT":
            truth_table = solver.get_truth_table(query)
            response_data["truthTable"] = truth_table
         
        # If using DPLL method, include DPLL result data
        if method == "DPLL":
            response_data["assignment"] = additional_info
            response_data["steps"] = additional_info.get("steps", [])

        # Clean up the temporary file
        os.unlink(tmp_file_path)

        return response_data

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


