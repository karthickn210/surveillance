import React, { useState } from 'react';

const TargetUploader = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
            setUploadStatus('');
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        setUploadStatus('Uploading...');
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://localhost:8000/upload_target', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                setUploadStatus('Success! Tracking initialized.');
            } else {
                setUploadStatus('Upload failed.');
            }
        } catch (error) {
            console.error(error);
            setUploadStatus('Network error.');
        }
    };

    return (
        <div className="flex flex-col gap-4">
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-4 text-center hover:border-gray-500 transition-colors relative">
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                {preview ? (
                    <img src={preview} alt="Target Preview" className="mx-auto h-32 object-cover rounded" />
                ) : (
                    <div className="text-gray-400">
                        <p>Click to select image</p>
                        <span className="text-xs">JPG/PNG supported</span>
                    </div>
                )}
            </div>

            <button
                onClick={handleUpload}
                disabled={!selectedFile}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white py-2 px-4 rounded font-semibold transition-colors"
            >
                Set Tracking Target
            </button>

            {uploadStatus && (
                <div className={`text-sm text-center ${uploadStatus.includes('Success') ? 'text-green-500' : 'text-red-500'}`}>
                    {uploadStatus}
                </div>
            )}
        </div>
    );
};

export default TargetUploader;
