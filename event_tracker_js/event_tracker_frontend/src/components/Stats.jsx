import { useState, useEffect } from 'react';
import { getStats } from '../api';

function Stats({ navigateTo }) {
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

  // Calculate percentages
  const calculatePercentage = (value, total) => {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
  };

  const registeredPercentage = calculatePercentage(stats.registered, stats.total);
  const lunchPercentage = calculatePercentage(stats.lunch_collected, stats.total);
  const kitPercentage = calculatePercentage(stats.kit_collected, stats.total);

  return (
    <div className="stats-page">
      <h2>Event Statistics</h2>
      
      {loading ? (
        <p>Loading statistics...</p>
      ) : (
        <div className="stats-container">
          <div className="stats-summary">
            <h3>Summary</h3>
            <div className="stats-table">
              <table>
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Count</th>
                    <th>Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Total Attendees</td>
                    <td>{stats.total}</td>
                    <td>100%</td>
                  </tr>
                  <tr>
                    <td>Registered</td>
                    <td>{stats.registered}</td>
                    <td>{registeredPercentage}%</td>
                  </tr>
                  <tr>
                    <td>Lunch Collected</td>
                    <td>{stats.lunch_collected}</td>
                    <td>{lunchPercentage}%</td>
                  </tr>
                  <tr>
                    <td>Kit Collected</td>
                    <td>{stats.kit_collected}</td>
                    <td>{kitPercentage}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="stats-visual">
            <h3>Visual Breakdown</h3>
            <div className="progress-bars">
              <div className="progress-item">
                <label>Registered:</label>
                <div className="progress-bar-container">
                  <div 
                    className="progress-bar" 
                    style={{ width: `${registeredPercentage}%` }}
                  ></div>
                  <span className="progress-text">{registeredPercentage}%</span>
                </div>
              </div>
              
              <div className="progress-item">
                <label>Lunch Collected:</label>
                <div className="progress-bar-container">
                  <div 
                    className="progress-bar" 
                    style={{ width: `${lunchPercentage}%` }}
                  ></div>
                  <span className="progress-text">{lunchPercentage}%</span>
                </div>
              </div>
              
              <div className="progress-item">
                <label>Kit Collected:</label>
                <div className="progress-bar-container">
                  <div 
                    className="progress-bar" 
                    style={{ width: `${kitPercentage}%` }}
                  ></div>
                  <span className="progress-text">{kitPercentage}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Stats;