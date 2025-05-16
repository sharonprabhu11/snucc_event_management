import { useState, useEffect } from 'react';
import { getAttendee, updateAttendee, getQRCode } from '../api';

function AttendeeDetail({ attendee: initialAttendee, navigateTo }) {
  const [attendee, setAttendee] = useState(initialAttendee || {});
  const [loading, setLoading] = useState(!initialAttendee);
  const [updating, setUpdating] = useState(false);
  const [qrCode, setQrCode] = useState(null);
  const [qrLoading, setQrLoading] = useState(false);

  useEffect(() => {
    if (!initialAttendee && attendee.identifier) {
      const fetchAttendee = async () => {
        setLoading(true);
        try {
          const data = await getAttendee(attendee.identifier);
          setAttendee(data);
        } catch (error) {
          console.error("Error fetching attendee details:", error);
        } finally {
          setLoading(false);
        }
      };

      fetchAttendee();
    }
  }, [initialAttendee, attendee.identifier]);

  const fetchQRCode = async () => {
    if (!attendee.identifier) return;
    
    setQrLoading(true);
    try {
      const data = await getQRCode(attendee.identifier);
      setQrCode(data.qr_code);
    } catch (error) {
      console.error("Error fetching QR code:", error);
    } finally {
      setQrLoading(false);
    }
  };

  useEffect(() => {
    if (attendee.identifier) {
      fetchQRCode();
    }
  }, [attendee.identifier]);

  const handleUpdateStatus = async (field) => {
    setUpdating(true);
    
    const updates = {
      [field]: !attendee[field]
    };
    
    try {
      const updatedAttendee = await updateAttendee(attendee.identifier, updates);
      setAttendee(updatedAttendee);
    } catch (error) {
      console.error(`Error updating ${field}:`, error);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <p>Loading attendee details...</p>;
  }

  return (
    <div className="attendee-detail">
      <div className="detail-header">
        <button onClick={() => navigateTo('attendees')} className="back-button">
          ← Back to Attendees
        </button>
        <h2>Attendee Details</h2>
      </div>

      <div className="detail-container">
        <div className="attendee-info">
          <div className="info-group">
            <label>Name:</label>
            <p>{attendee.name}</p>
          </div>
          
          <div className="info-group">
            <label>Email:</label>
            <p>{attendee.email}</p>
          </div>
          
          <div className="info-group">
            <label>Identifier:</label>
            <p>{attendee.identifier}</p>
          </div>
          
          {attendee.registration_time && (
            <div className="info-group">
              <label>Registration Time:</label>
              <p>{new Date(attendee.registration_time).toLocaleString()}</p>
            </div>
          )}
          
          <div className="status-toggles">
            <h3>Status</h3>
            <div className="toggle-group">
              <label>Registered:</label>
              <button
                onClick={() => handleUpdateStatus('registered')}
                disabled={updating}
                className={`toggle-button ${attendee.registered ? 'active' : ''}`}
              >
                {attendee.registered ? "Yes" : "No"}
              </button>
            </div>
            
            <div className="toggle-group">
              <label>Lunch Collected:</label>
              <button
                onClick={() => handleUpdateStatus('lunch_collected')}
                disabled={updating}
                className={`toggle-button ${attendee.lunch_collected ? 'active' : ''}`}
              >
                {attendee.lunch_collected ? "Yes" : "No"}
              </button>
            </div>
            
            <div className="toggle-group">
              <label>Kit Collected:</label>
              <button
                onClick={() => handleUpdateStatus('kit_collected')}
                disabled={updating}
                className={`toggle-button ${attendee.kit_collected ? 'active' : ''}`}
              >
                {attendee.kit_collected ? "Yes" : "No"}
              </button>
            </div>
          </div>
        </div>

        <div className="qr-code-container">
          <h3>QR Code</h3>
          {qrLoading ? (
            <p>Loading QR code...</p>
          ) : qrCode ? (
            <div className="qr-code">
              <img src={qrCode} alt={`QR Code for ${attendee.identifier}`} />
              <p>Scan to verify attendee</p>
            </div>
          ) : (
            <p>Failed to load QR code</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default AttendeeDetail;