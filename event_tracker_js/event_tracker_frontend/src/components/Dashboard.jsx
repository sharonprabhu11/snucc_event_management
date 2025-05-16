import { useState, useEffect } from 'react';
import { getStats } from '../api';

function Dashboard({ navigateTo }) {
  const [stats, setStats] = useState({
    total: 0,
    registered: 0,
    lunch_collected: 0,
    kit_collected: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats();
        setStats(data);
      } catch (error) {
        console.error("Error fetching stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="dashboard">
      <h2>Event Dashboard</h2>
      
      {loading ? (
        <p>Loading stats...</p>
      ) : (
        <div className="stats-cards">
          <div className="stat-card">
            <h3>Total Attendees</h3>
            <p className="stat-number">{stats.total}</p>
          </div>
          <div className="stat-card">
            <h3>Registered</h3>
            <p className="stat-number">{stats.registered}</p>
            <p className="stat-percentage">
              {stats.total > 0 ? Math.round((stats.registered / stats.total) * 100) : 0}%
            </p>
          </div>
          <div className="stat-card">
            <h3>Lunch Collected</h3>
            <p className="stat-number">{stats.lunch_collected}</p>
            <p className="stat-percentage">
              {stats.total > 0 ? Math.round((stats.lunch_collected / stats.total) * 100) : 0}%
            </p>
          </div>
          <div className="stat-card">
            <h3>Kit Collected</h3>
            <p className="stat-number">{stats.kit_collected}</p>
            <p className="stat-percentage">
              {stats.total > 0 ? Math.round((stats.kit_collected / stats.total) * 100) : 0}%
            </p>
          </div>
        </div>
      )}

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button onClick={() => navigateTo('attendees')}>View Attendees</button>
          <button onClick={() => navigateTo('upload')}>Upload CSV</button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;