import { useState } from "react";
import { useNavigate } from "react-router-dom";

const MessageInput = () => {
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleNext = () => {
    if (!message) return alert("Por favor, ingresa un mensaje.");
    navigate("/key-generation", { state: { message } });
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>✍️ Escribe tu Mensaje</h2>
      <textarea
        rows="4"
        cols="50"
        placeholder="Escribe aquí..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <br />
      <button onClick={handleNext}>Siguiente</button>
    </div>
  );
};

export default MessageInput;