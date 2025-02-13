import React, { useState } from 'react';
import { UploadCloud } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('/upload-face', {
        method: 'POST',
        body: formData,
      });
      setResponse(await res.text());
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-4xl font-bold mb-8">Face Recognition</h1>
      <div className="flex flex-col items-center space-y-4">
        <input 
          type="file" 
          onChange={handleFileChange} 
          className="block w-full text-sm text-gray-500
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-full file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-50 file:text-blue-700
                     hover:file:bg-blue-100"
        />
        <button 
          onClick={handleUpload} 
          className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700"
        >
          <UploadCloud className="w-5 h-5 mr-2" />
          Upload
        </button>
        <pre className="mt-4 p-4 bg-white rounded-lg shadow-md w-full max-w-2xl overflow-x-auto">{response}</pre>
      </div>
    </div>
  );
}

export default App;