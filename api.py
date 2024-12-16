from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
from iengine import parse_input_file, get_solver

app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def process_file():
    try:
        file = request.files['file']
        method = request.form['method']

        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
            content = file.read()
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

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
