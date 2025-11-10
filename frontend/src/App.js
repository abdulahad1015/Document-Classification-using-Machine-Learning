import React, { useState } from 'react';
import './App.css';
import FileUpload from './FileUpload';
import MyFiles from './components/MyFiles';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

function App() {
  const [activePage, setActivePage] = useState('Upload');
  const [sidebarOpen, setSidebarOpen] = useState(true);
    const [toast, setToast] = useState(null); // { message: string } | null

  const toggleSidebar = () => setSidebarOpen((s) => !s);

    const showToast = (message) => {
      setToast({ message });
      setTimeout(() => setToast(null), 1600);
    };

    const handleSavedAndNavigate = (count) => {
      showToast(`${count} file${count === 1 ? '' : 's'} saved`);
      setActivePage('My Files');
    };

  return (
    <div className={`app ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      <Navbar onMenuClick={toggleSidebar} />
        {toast && (
          <div className="toast">{toast.message}</div>
        )}
      <Sidebar
        open={sidebarOpen}
        active={activePage}
        onSelect={setActivePage}
      />

      <main className="content">
        {activePage === 'Dashboard' && (
          <section>
            <h2>Dashboard</h2>
            <p>Quick overview of your recent activity.</p>
          </section>
        )}

        {activePage === 'Upload' && (
          <section>
            <h2>Upload Documents</h2>
            <p>Select one or more files to upload.</p>
              <FileUpload onSaved={handleSavedAndNavigate} />
          </section>
        )}

        {activePage === 'My Files' && (
          <MyFiles />
        )}

        {activePage === 'Settings' && (
          <section>
            <h2>Settings</h2>
            <p>Coming soon: customize your preferences.</p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
