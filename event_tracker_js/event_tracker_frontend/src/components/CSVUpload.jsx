import { useState } from 'react';
import { uploadCSV } from '../api';

function CSVUpload({ navigateTo }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [attendeesAdded, setAttendeesAdded] = useState(0);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError("Please select a valid CSV file");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError("Please select a CSV file");
      return;
    }
    
    setUploading(true);
    setError(null);
    
    try {
      const response = await uploadCSV(file);
      setUploadSuccess(true);
      setAttendeesAdded(response.attendees.length);
    } catch (error) {
      console.error("Error uploading CSV:", error);
      setError("Failed to upload CSV file. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="csv-upload">
      <h2>Upload Attendees CSV</h2>
      
      {uploadSuccess ? (
        <div className="upload-success">
          <div className="success-message">
            <h3>Upload Successful!</h3>
            <p>Attendees were added to the system.</p>
          </div>
          <div className="success-actions">
            <button onClick={() => navigateTo('attendees')}>View Attendees</button>
            <button onClick={() => {
              setFile(null);
              setUploadSuccess(false);
              setAttendeesAdded(0);
            }}>Upload Another File</button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-container">
            <p>Please select a CSV file with the following columns:</p>
            <ul className="csv-format">
              <li><strong>name:</strong> Attendee's full name</li>
              <li><strong>email:</strong> Attendee's email address</li>
              <li><strong>role:</strong> Attendee's  role</li>
              <li><strong>phone number:</strong> Attendee's phone number</li>
            </ul>
            
            <div className="file-input">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                disabled={uploading}
                id="csv-file"
              />
              <label htmlFor="csv-file" className={uploading ? "disabled" : ""}>
                {file ? file.name : "Select CSV File"}
              </label>
            </div>
            
            {error && <p className="error-message">{error}</p>}
          </div>
          
          <button
            type="submit"
            disabled={!file || uploading}
            className="upload-button"
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>
      )}
    </div>
  );
}

export default CSVUpload;