import { useLocation } from "react-router-dom";
import { useState } from "react";
import axios from "axios";


const EncryptionScreen = () => {
  const location = useLocation();
  const selectedKey = location.state?.selectedKey;
  const message = location.state?.message;
  const alicekey = location.state?.aliceKey;

  const [loading, setLoading] = useState(false);

  const [encryptedMessage, setEncryptedMessage] = useState("");
  const [decryptedMessage, setDecryptedMessage] = useState("");

  const getCSRFToken = () => {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];
  };

   const handleEncrypt = async () => {
      setLoading(true);
      try {
          const response = await axios.post(
            "http://127.0.0.1:8000/encrypt/",
            {
              message: message,
              key: alicekey, 
            });
  
            setEncryptedMessage(response.data.encrypted_message);
      } catch (error) {
        console.error("Error al encriptar el mensaje:", error);
      } finally {
        setLoading(false);
      }
    };

  const handleDecrypt = async () => {
    setLoading(true);
    const csrfToken = getCSRFToken();
      if (!csrfToken) {
        console.error("CSRF token not found");
        return;
      }
      try {
          const response = await axios.post(
            "http://127.0.0.1:8000/decrypt/",
            {
              encrypted_message: encryptedMessage,
              key: selectedKey, 
            });
  
            setDecryptedMessage(response.data.message);
      } catch (error) {
        console.error("Error al desencriptar el mensaje:", error);
      } finally {
        setLoading(false);
      }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>🔐 Encriptación y Desencriptación</h2>
      <h2>Mensaje enviado</h2>
      <p><strong>{message}</strong></p>
      <button onClick={handleEncrypt}>Cifrar Mensaje</button>
      {encryptedMessage && (
        <>
          <p><strong>Mensaje Cifrado:</strong> {encryptedMessage}</p>
          <button onClick={handleDecrypt}>Descifrar Mensaje</button>
        </>
      )}
      {decryptedMessage && <p><strong>Mensaje Descifrado:</strong> {decryptedMessage}</p>}
    </div>
  );
};

export default EncryptionScreen;
