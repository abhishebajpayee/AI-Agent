import json
import pandas as pd
from typing import Dict, Any

# Global data store reference (populated in main.py)
DATA_STORE: Dict[str, Dict[str, pd.DataFrame]] = {} 

def execute_pandas_code(file_id: str, sheet_name: str, code: str) -> Dict[str, Any]:
    """
    Safely executes generated Pandas code on the specified DataFrame.
    """
    if file_id not in DATA_STORE or sheet_name not in DATA_STORE[file_id]:
        return {"success": False, "error": "File or sheet not found in memory store."}

    df = DATA_STORE[file_id][sheet_name].copy() 

    result_capture = []
    def custom_print(data):
        """Captures JSON output from the executed code."""
        result_capture.append(data)

    # --- CRITICAL SANDBOXING MECHANISM ---
    safe_globals = {
        'pd': pd,
        'df': df, # The only way to access the data
        'print': custom_print,
        'json': json,
        # Restrict built-ins to prevent file system access (e.g., open, exit)
        '__builtins__': {'int': int, 'float': float, 'str': str, 'list': list, 'dict': dict, 
                         'len': len, 'sum': sum, 'min': min, 'max': max, 'type': type}
    }

    try:
        exec(code, safe_globals)
        
        if not result_capture:
            return {"success": False, "error": "Code executed but returned no structured output. Must use print(json.dumps(...))."}

        final_result = json.loads("".join(result_capture))
        
        # NOTE: In a real system, you'd integrate Plotly/Altair here to generate the chart_spec.
        # This example just passes the raw analysis result.
        
        return {"success": True, "result": final_result}

    except Exception as e:
        return {"success": False, "error": f"Execution failed: {type(e).__name__}: {str(e)}"}
