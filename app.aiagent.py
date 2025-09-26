from typing import Dict, Any, List
from .database import retrieve_metadata_for_file
from .agent_tools import execute_pandas_code

# --- Simulated LLM Prompts & Tools ---

def get_agent_response(file_id: str, question: str) -> Dict[str, Any]:
    """
    Simulated ReAct Agent Flow: Context -> Plan -> Action -> Result
    """
    
    # 1. Context Retrieval (Simulated LLM Thought 1)
    metadata = retrieve_metadata_for_file(file_id)
    
    # A real LLM would use the question and metadata to identify the target sheet/columns.
    # We hardcode the result for demonstration purposes:
    if "sales" in question.lower() and "region" in question.lower():
        target_sheet = "Sales Data" 
        relevant_columns = "date, region, revenue"
    else:
        target_sheet = list(metadata[0]['sheet_name']) if metadata else "Sheet1"
        relevant_columns = ", ".join([m['column_name'] for m in metadata[:3]])
        
    
    # 2. Analysis Plan Generation (Simulated LLM Thought 2)
    # The LLM generates the necessary Python code based on the context and question.
    if "total revenue" in question.lower() and "west" in question.lower():
        pandas_code = f"""
df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
total_revenue = df[df['region'].str.lower() == 'west']['revenue'].sum()
# Output the result using the custom print function
print(json.dumps({{
    "type": "summary",
    "value": total_revenue,
    "label": "Total Revenue (West)",
    "currency": "USD"
}}))
"""
        text_summary = "Based on my analysis, the total revenue for the Western region is calculated below."

    else:
        # Generic descriptive query
        pandas_code = f"""
# Show a head of the data grouped by the first relevant column
summary_df = df.groupby('{relevant_columns.split(', ')[1]}')['{relevant_columns.split(', ')[2]}'].sum().reset_index().head(5)
print(json.dumps({{
    "type": "table",
    "data": summary_df.to_dict(orient='records'),
    "columns": list(summary_df.columns)
}}))
"""
        text_summary = f"Here is a breakdown of the {relevant_columns.split(', ')[2]} column grouped by {relevant_columns.split(', ')[1]}."

    
    # 3. Action Execution (Tool Call)
    execution_result = execute_pandas_code(file_id, target_sheet, pandas_code)
    
    # 4. Final Response
    if execution_result['success']:
        return {
            "text_summary": text_summary,
            "data": execution_result['result']
        }
    else:
        return {
            "text_summary": f"I encountered an error during data processing: {execution_result['error']}",
            "data": {"type": "error", "message": execution_result['error']}
      }
