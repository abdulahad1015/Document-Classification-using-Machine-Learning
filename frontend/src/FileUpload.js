import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = ({ onSaved }) => {
    const [files, setFiles] = useState([]);
    const [status, setStatus] = useState('idle'); // idle | uploading | success | error
    const [error, setError] = useState(null);
    const [uploaded, setUploaded] = useState([]);
    const [progress, setProgress] = useState(0);
    const [edits, setEdits] = useState({}); // id -> edited classification

    const handleFileChange = (e) => {
        setFiles(Array.from(e.target.files));
        setStatus('idle');
        setUploaded([]);
        setError(null);
        setProgress(0);
    };

    const handleUpload = async () => {
        if (!files.length) return;
        setStatus('uploading');
        setError(null);
        const formData = new FormData();
        files.forEach(f => formData.append('files', f));

        try {
            const response = await axios.post('/upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (evt) => {
                    if (evt.total) {
                        const pct = Math.round((evt.loaded / evt.total) * 100);
                        setProgress(pct);
                    }
                }
            });
            const uploaded = response.data.uploaded_files || [];
            setUploaded(uploaded);
            // Seed editable classifications
            const seed = {};
            uploaded.forEach(f => { seed[f.id] = f.classification || ''; });
            setEdits(seed);
            setStatus('success');
        } catch (err) {
            console.error(err);
            setError('Upload failed. Please try again.');
            setStatus('error');
        }
    };

    const saveClassification = async (fileId) => {
        try {
            const newVal = edits[fileId] ?? '';
            await axios.patch('/files/', { id: fileId, classification: newVal });
            setUploaded(prev => prev.map(f => f.id === fileId ? { ...f, classification: newVal } : f));
            if (typeof onSaved === 'function') onSaved(1);
        } catch (e) {
            console.error(e);
            setError('Failed to save classification.');
        }
    };

    const saveAll = async () => {
        try {
            const patchPromises = uploaded.map(f => {
                const newVal = edits[f.id] ?? '';
                return axios.patch('/files/', { id: f.id, classification: newVal });
            });
            await Promise.all(patchPromises);
            setUploaded(prev => prev.map(f => ({ ...f, classification: edits[f.id] ?? '' })));
            if (typeof onSaved === 'function') onSaved(uploaded.length);
        } catch (e) {
            console.error(e);
            setError('Failed to save classifications.');
        }
    };

    return (
        <div className="upload-card">
            <div className="upload-header">
                <h3>Select Files</h3>
            </div>
            <div className="upload-body">
                <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    className="file-input"
                />
                {files.length > 0 && (
                    <ul className="file-list">
                        {files.map(f => (
                            <li key={f.name}>{f.name} <span className="size">({(f.size/1024).toFixed(1)} KB)</span></li>
                        ))}
                    </ul>
                )}
                <button
                    className="primary-btn"
                    onClick={handleUpload}
                    disabled={status === 'uploading' || !files.length}
                >
                    {status === 'uploading' ? 'Uploading...' : 'Upload'}
                </button>
                {status === 'uploading' && (
                    <div className="progress-bar">
                        <div className="progress" style={{ width: `${progress}%` }} />
                    </div>
                )}
                {status === 'success' && (
                        <div className="alert success">Uploaded {uploaded.length} file(s) successfully.</div>
                )}
                {status === 'error' && (
                        <div className="alert error">{error}</div>
                )}
                {status === 'idle' && files.length === 0 && (
                        <p className="hint">You can select multiple files.</p>
                )}
                {uploaded.length > 0 && (
                    <div className="results">
                        <h4>Classification</h4>
                        <button className="primary-btn" style={{ marginBottom:'0.75rem' }} onClick={saveAll}>Save All</button>
                        <ul>
                            {uploaded.map(f => (
                                <li key={f.id} style={{ display:'flex', alignItems:'center', gap:'8px' }}>
                                    <span style={{ minWidth: 160 }}>{f.file_name}</span>
                                    <input
                                      className="text-input"
                                      type="text"
                                      value={edits[f.id] ?? ''}
                                      onChange={(e) => setEdits(prev => ({ ...prev, [f.id]: e.target.value }))}
                                    />
                                    <button className="primary-btn" onClick={() => saveClassification(f.id)}>Save</button>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;