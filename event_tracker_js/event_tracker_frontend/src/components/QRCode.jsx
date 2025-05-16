import { useState, useEffect } from 'react';
import { getQRCode } from '../api';

function QRCode({ identifier }) {
  const [qrCode, setQrCode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQRCode = async () => {
      if (!identifier) {
        setError("No identifier provided");
        setLoading(false);
        return;
      }
      
      setLoading(true);
      try {
        const data = await getQRCode(identifier);
        setQrCode(data.qr_code);
        setError(null);
      } catch (error) {
        console.error("Error fetching QR code:", error);
        setError("Failed to load QR code");
      } finally {
        setLoading(false);
      }
    };

    fetchQRCode();
  }, [identifier]);

  if (loading) {
    return <div className="qr-loading">Loading QR code...</div>;
  }

  if (error) {
    return <div className="qr-error">{error}</div>;
  }

  return (
    <div className="qr-code">
      <img src={qrCode} alt={`QR Code for ${identifier}`} />
    </div>
  );
}

export default QRCode;