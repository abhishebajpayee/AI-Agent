import React from 'react';

// Placeholder Table Component
export const Table = ({ data, columns }) => {
    if (!data || data.length === 0) return <p>No data to display in table.</p>;
    
    // Ensure data is an array of objects
    const keys = columns || Object.keys(data[0]);

    return (
        <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 border">
                <thead className="bg-gray-50">
                    <tr>
                        {keys.map(key => (
                            <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                {key.replace(/_/g, ' ')}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {data.map((row, index) => (
                        <tr key={index}>
                            {keys.map(key => (
                                <td key={key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {row[key] !== undefined ? row[key].toLocaleString() : '-'}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

// Placeholder Chart Component (Ideally uses Plotly/Chart.js)
export const BarChart = ({ data, spec }) => {
    if (!data) return <p>No chart data available.</p>;
    
    // Simple rendering of the first key/value pair in data
    const keys = Object.keys(data);
    
    return (
        <div className="border p-4 bg-white shadow-inner">
            <h3 className="text-lg font-semibold mb-2">Bar Chart Visualization (Simulated)</h3>
            <p className="text-sm">Showing the top 5 entries:</p>
            <ul className="list-disc ml-6">
                {keys.slice(0, 5).map(key => (
                    <li key={key}>{key}: **{data[key].toLocaleString()}**</li>
                ))}
            </ul>
        </div>
    );
};
