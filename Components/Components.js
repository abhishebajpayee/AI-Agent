import React, { useState } from 'react';
import axios from 'axios';
import { Table } from './VisualizationComponents'; // Import placeholder

// Read API_BASE_URL from environment variables
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function DataAgent() {
    const [file, setFile] = useState(null);
    const [fileId, setFileId] = useState(null);
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [agentResponse, setAgentResponse] = useState(null);
    const [error, setError] = useState('');

    const handleFileUpload = async () => {
        if (!file) {
            setError('Please select a file to upload.');
            return;
        }
        setLoading(true);
        setError('');
        setFileId(null);
        setAgentResponse(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post(`${API_BASE_URL}/upload/`, formData);

            setFileId(response.data.file_id);
            alert(`File processed! ID: ${response.data.file_id}. Ready to query.`);

        } catch (err) {
            setError(`Upload failed: ${err.response?.data?.detail || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleQuerySubmit = async (e) => {
        e.preventDefault();
        if (!fileId || !query) {
            setError('Please upload a file and enter a query.');
            return;
        }

        setLoading(true);
        setError('');
        
        try {
            const response = await axios.post(`${API_BASE_URL}/query/`, { 
                file_id: fileId, 
                question: query 
            });

            setAgentResponse(response.data.result);

        } catch (err) {
            setError(`Query failed: ${err.response?.data?.detail || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const renderDataPayload = (data) => {
        if (!data) return null;

        switch (data.type) {
            case 'table':
                return <Table data={data.data} columns={data.columns} />;
            case 'summary':
                return (
                    <div className="p-4 bg-green-100 border border-green-300 rounded">
                        <p className="text-xl font-bold">{data.label}: {data.currency} {data.value.toLocaleString()}</p>
                    </div>
                );
            case 'error':
                return <p className="text-red-600">Visualization Error: {data.message}</p>
            default:
                return <p>Data payload type: **{data.type}** (Not rendered)</p>;
        }
    };

    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-4xl font-extrabold mb-6 text-gray-800">📊 AI Data Agent Platform</h1>
            
            {/* File Upload Section */}
            <div className="p-6 border-2 border-dashed border-blue-300 bg-blue-50 rounded-xl mb-8">
                <input 
                    type="file" 
                    accept=".xlsx,.xls" 
                    onChange={(e) => setFile(e.target.files[0])} 
                    className="mr-4 text-sm"
                />
                <button 
                    onClick={handleFileUpload} 
                    disabled={!file || loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                    {loading && !fileId ? 'Processing Data...' : 'Upload & Process Excel'}
                </button>
                {fileId && <p className="text-sm mt-3 text-green-700 font-medium">✅ File Ready for Querying (ID: {fileId.substring(0, 8)}...)</p>}
            </div>

            {/* Query Section */}
            <form onSubmit={handleQuerySubmit} className="mb-8">
                <label className="block text-lg font-medium mb-2 text-gray-700">Ask a Business Question:</label>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="E.g., What was the total revenue for Product A in the Western region last month?"
                    disabled={!fileId || loading}
                    className="border border-gray-300 p-3 w-3/4 rounded-l-lg focus:ring-2 focus:ring-green-500"
                />
                <button 
                    type="submit" 
                    disabled={!fileId || !query || loading}
                    className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-r-lg transition"
                >
                    {loading && fileId ? 'Getting Insights...' : 'Get Insights'}
                </button>
            </form>

            {/* Error Display */}
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-8" role="alert">
                    <strong className="font-bold">Error!</strong>
                    <span className="block sm:inline"> {error}</span>
                </div>
            )}

            {/* Agent Response Section */}
            {agentResponse && (
                <div className="bg-white p-6 shadow-lg rounded-xl">
                    <h2 className="text-2xl font-bold mb-4 text-gray-800">Agent's Response</h2>
                    <p className="text-gray-700 mb-4">{agentResponse.text_summary}</p>
                    
                    {/* Render the data payload dynamically */}
                    <div className="mt-6">
                        {renderDataPayload(agentResponse.data)}
                    </div>
                </div>
            )}
        </div>
    );
}

export default DataAgent;
