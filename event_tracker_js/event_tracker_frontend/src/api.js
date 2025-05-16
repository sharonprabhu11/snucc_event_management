
const API_URL = "http://localhost:8000";

export const getAttendees = async (search = "", skip = 0, limit = 100) => {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  params.append("skip", skip);
  params.append("limit", limit);
  
  const response = await fetch(`${API_URL}/attendees?${params}`);
  if (!response.ok) {
    throw new Error("Failed to fetch attendees");
  }
  return response.json();
};


export const getAttendee = async (identifier) => {
  const response = await fetch(`${API_URL}/attendee/${identifier}`);
  if (!response.ok) {
    throw new Error("Failed to fetch attendee");
  }
  return response.json();
};


export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${API_URL}/upload-csv`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error("Failed to upload CSV");
  }
  return response.json();
};

// Update attendee status
export const updateAttendee = async (identifier, updates) => {
  const response = await fetch(`${API_URL}/attendee/${identifier}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updates),
  });
  
  if (!response.ok) {
    throw new Error("Failed to update attendee");
  }
  return response.json();
};

// Get QR code for an attendee
export const getQRCode = async (identifier) => {
  const response = await fetch(`${API_URL}/qrcode/${identifier}`);
  if (!response.ok) {
    throw new Error("Failed to get QR code");
  }
  return response.json();
};

// Get event stats
export const getStats = async () => {
  const response = await fetch(`${API_URL}/stats`);
  if (!response.ok) {
    throw new Error("Failed to fetch stats");
  }
  return response.json();
};