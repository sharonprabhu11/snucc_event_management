import { useState } from 'react';
import Dashboard from './components/Dashboard';
import AttendeeList from './components/AttendeeList';
import AttendeeDetail from './components/AttendeeDetail';
import CSVUpload from './components/CSVUpload';
import Stats from './components/Stats';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedAttendee, setSelectedAttendee] = useState(null);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard navigateTo={setCurrentPage} />;
      case 'attendees':
        return (
          <AttendeeList 
            navigateTo={setCurrentPage} 
            selectAttendee={(attendee) => {
              setSelectedAttendee(attendee);
              setCurrentPage('attendeeDetail');
            }} 
          />
        );
      case 'attendeeDetail':
        return (
          <AttendeeDetail 
            attendee={selectedAttendee} 
            navigateTo={setCurrentPage} 
          />
        );
      case 'upload':
        return <CSVUpload navigateTo={setCurrentPage} />;
      case 'stats':
        return <Stats navigateTo={setCurrentPage} />;
      default:
        return <Dashboard navigateTo={setCurrentPage} />;
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Event Tracker</h1>
        <nav>
          <button onClick={() => setCurrentPage('dashboard')}>Dashboard</button>
          <button onClick={() => setCurrentPage('attendees')}>Attendees</button>
          <button onClick={() => setCurrentPage('upload')}>Upload CSV</button>
          <button onClick={() => setCurrentPage('stats')}>Stats</button>
        </nav>
      </header>
      <main>
        {renderPage()}
      </main>
    </div>
  );
}

export default App;