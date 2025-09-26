import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid

from .database import initialize_db, store_file_metadata
from .ai_agent import get_agent_response
from .agent_tools import DATA_STORE # Import the global store

# --- FASTAPI SETUP ---
app = FastAPI()

# Allow CORS for development (React on different port)
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database on startup
@app.on_event("startup")
def startup_event():
    initialize_db()

# --- DATA MODELS ---
class QueryRequest(BaseModel):
    file_id: str
    question: str
    
# --- HELPER: DATA CLEANING ---

def clean_dataframe(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """Handles data inconsistency, unnamed columns, and type inference."""
    
    # Drop rows where ALL values are NaN (often trailing rows in Excel)
    df = df.dropna(how='all')
    
    # 1. Standardize and Rename Columns
    new_cols = {}
    # Use the first row as headers if the actual header is "Unnamed" or empty
    if df.iloc[0].isnull().all() or df.columns.astype(str).str.contains('Unnamed:').any():
        df.columns = df.iloc[0].fillna(pd.Series([f'Unnamed_Col_{i}' for i in range(len(df.columns))])).astype(str)
        df = df[1:].reset_index(drop=True)

    for col in df.columns:
        raw_col_name = str(col).strip()
        new_col_name = raw_col_name.lower().replace(' ', '_').replace('.', '').strip()
        new_cols[col] = new_col_name
            
    df = df.rename(columns=new_cols)
    
    # 2. Type Conversion and Cleaning (Robustness)
    for col in df.columns:
        # Try to convert to numeric, excluding common ID/code columns
        if not any(keyword in col.lower() for keyword in ['id', 'code', 'ref']):
             df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop columns with extremely high NaN rate after conversion (e.g., if a text column was coerced to NaN)
        if df[col].isnull().sum() > len(df) * 0.5: # More than 50% NaN
             print(f"Warning: Dropping column {col} due to high NaN rate after cleaning.")
             df = df.drop(columns=[col])

    return df

# --- API ENDPOINTS ---

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Accepts Excel file, cleans it, and stores data and metadata."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Must be an Excel file (.xlsx or .xls)")

    try:
        content = await file.read()
        xls = pd.ExcelFile(io.BytesIO(content))
        file_id = str(uuid.uuid4()) # Use a real unique ID
        
        sheet_data = {}
        column_metadata = {}
        
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            
            # Robust Cleaning
            cleaned_df = clean_dataframe(df, sheet_name)
            sheet_data[sheet_name] = cleaned_df
            
            # Semantic Modeling (Simulated LLM Description generation)
            metadata = {
                col: f"A column named '{col}' from the '{sheet_name}' sheet, containing {cleaned_df[col].dtype} data."
                for col in cleaned_df.columns
            }
            column_metadata[sheet_name] = metadata
            
        DATA_STORE[file_id] = sheet_data # Store data in memory
        store_file_metadata(file_id, file.filename, column_metadata) # Store metadata in DB
        
        return {"file_id": file_id, "sheets": list(sheet_data.keys()), "message": "File processed successfully."}

    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@app.post("/query/")
async def handle_query(request: QueryRequest):
    """Passes query to the AI Agent for processing."""
    if request.file_id not in DATA_STORE:
        raise HTTPException(status_code=404, detail="File ID not found. Upload again.")
    
    # The call to the core AI Agent
    result = get_agent_response(request.file_id, request.question)
    
    return {"result": result}
