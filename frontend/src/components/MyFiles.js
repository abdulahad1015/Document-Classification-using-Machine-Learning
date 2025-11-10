import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MyFiles = () => {
  const [files, setFiles] = useState([]);
  // Using free-text classification now
  const [search, setSearch] = useState('');
  const [classFilter, setClassFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState(null);
  const [savedId, setSavedId] = useState(null);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      setLoading(true);
      const filesRes = await axios.get('/files/');
      setFiles(filesRes.data.files || []);
    } catch (e) {
      console.error(e);
      setError('Failed to load files.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const updateClassification = async (id, classification) => {
    try {
      setSavingId(id);
      await axios.patch('/files/', { id, classification });
      setFiles(prev => prev.map(f => (f.id === id ? { ...f, classification } : f)));
      setSavedId(id);
      setTimeout(() => setSavedId(null), 1200);
    } catch (e) {
      console.error(e);
      setError('Failed to save classification.');
    } finally {
      setSavingId(null);
    }
  };

  const deleteFile = async (id) => {
    try {
      await axios.delete('/files/', { data: { id } });
      setFiles(prev => prev.filter(f => f.id !== id));
    } catch (e) {
      console.error(e);
      setError('Failed to delete file.');
    }
  };

  const filtered = files.filter(f => {
    const nameOk = f.file_name.toLowerCase().includes(search.toLowerCase());
    const clsOk = classFilter ? (f.classification || '').toLowerCase().includes(classFilter.toLowerCase()) : true;
    return nameOk && clsOk;
  });

  if (loading) {
    return <section><h2>My Files</h2><p>Loading...</p></section>;
  }

  return (
    <section>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <h2>My Files</h2>
        <button className="primary-btn" onClick={load}>Refresh</button>
      </div>
      {error && <div className="alert error" style={{ marginBottom: '1rem' }}>{error}</div>}
      {files.length === 0 ? (
        <p>No files uploaded yet.</p>
      ) : (
        <div className="card" style={{ overflowX:'auto' }}>
          <div style={{ display:'flex', gap:'10px', padding:'0 .25rem 1rem' }}>
            <input
              className="text-input"
              placeholder="Search by name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ maxWidth: 260 }}
            />
            <input
              className="text-input"
              placeholder="Filter by classification..."
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value)}
              style={{ maxWidth: 260 }}
            />
          </div>
          <table className="table">
            <thead>
              <tr>
                <th style={{ textAlign:'left' }}>Name</th>
                <th style={{ textAlign:'left' }}>Classification</th>
                <th style={{ textAlign:'left' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(f => (
                <tr key={f.id}>
                  <td>{f.file_name}</td>
                  <td>
                    <input
                      className="text-input"
                      type="text"
                      value={f.classification || ''}
                      onChange={(e) => setFiles(prev => prev.map(x => x.id === f.id ? { ...x, classification: e.target.value } : x))}
                    />
                  </td>
                  <td>
                    <button
                      className="primary-btn"
                      onClick={() => updateClassification(f.id, f.classification)}
                      disabled={savingId === f.id}
                    >
                      {savingId === f.id ? 'Saving...' : (savedId === f.id ? 'Saved' : 'Save')}
                    </button>
                    <button
                      className="danger-btn"
                      style={{ marginLeft: 8 }}
                      onClick={() => deleteFile(f.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};

export default MyFiles;
