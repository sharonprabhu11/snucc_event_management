import { useState, useEffect } from 'react';
import { getAttendees } from '../api';

function AttendeeList({ navigateTo, selectAttendee }) {
  const [attendees, setAttendees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [searchTimeout, setSearchTimeout] = useState(null);

  const fetchAttendees = async (searchTerm = '') => {
    setLoading(true);
    try {
      const data = await getAttendees(searchTerm);
      setAttendees(data);
    } catch (error) {
      console.error("Error fetching attendees:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendees();
  }, []);

  const handleSearchChange = (e) => {
    const searchTerm = e.target.value;
    setSearch(searchTerm);
    
    // Debounce search requests
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    setSearchTimeout(
      setTimeout(() => {
        fetchAttendees(searchTerm);
      }, 300)
    );
  };

  return (
    <div className="attendee-list">
      <h2>Attendees</h2>
      
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by name, email or ID..."
          value={search}
          onChange={handleSearchChange}
        />
      </div>
      
      {loading ? (
        <p>Loading attendees...</p>
      ) : attendees.length === 0 ? (
        <p>No attendees found.</p>
      ) : (
        <table className="attendees-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>ID</th>
              <th>Registered</th>
              <th>Lunch</th>
              <th>Kit</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {attendees.map((attendee) => (
              <tr key={attendee.identifier}>
                <td>{attendee.name}</td>
                <td>{attendee.email}</td>
                <td>{attendee.identifier}</td>
                <td>
                  <span className={attendee.registered ? "status-yes" : "status-no"}>
                    {attendee.registered ? "✓" : "✗"}
                  </span>
                </td>
                <td>
                  <span className={attendee.lunch_collected ? "status-yes" : "status-no"}>
                    {attendee.lunch_collected ? "✓" : "✗"}
                  </span>
                </td>
                <td>
                  <span className={attendee.kit_collected ? "status-yes" : "status-no"}>
                    {attendee.kit_collected ? "✓" : "✗"}
                  </span>
                </td>
                <td>
                  <button 
                    className="view-button"
                    onClick={() => selectAttendee(attendee)}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AttendeeList;