import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

const KeyGenerator = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [key, setKey] = useState("");
  const [entropy, setEntropy] = useState(null);
  const [randomnessTests, setRandomnessTests] = useState(null);
  const [loading, setLoading] = useState(false);
  const message = location.state?.message;


  const generateKey = async () => {
    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/generate-key/", { message_length: message.length });
      setKey(response.data.key);
      setEntropy(response.data.entropy);
      setRandomnessTests(response.data.randomness_tests);
    } catch (error) {
      console.error("Error generating key:", error);
    }
    setLoading(false);
  };

  const handleAcceptKey = () => {
    navigate("/key-exchange", { state: { selectedKey: key, message: message } });
  };

  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      <h1>Generador de Claves</h1>
      <button onClick={generateKey} disabled={loading}>
        {loading ? "Generando..." : "Generar Clave"}
      </button>
      {key && (
        <div style={{ marginTop: "1rem" }}>
          <h2>Clave Generada:</h2>
          <p>{key}</p>
          <h3>Resultados de las pruebas:</h3>
          <p>Entropía Binaria: {entropy}</p>
          <p>Prueba Monobit: {randomnessTests?.monobit?.toFixed(2)}</p>
          <button
            onClick={handleAcceptKey}
            style={{
              marginTop: "1rem",
              backgroundColor: randomnessTests?.runs ? "green" : "gray",
              color: "white",
              padding: "0.5rem 1rem",
              border: "none",
              cursor: randomnessTests?.runs ? "pointer" : "not-allowed",
            }}
          >
            Aceptar y Proceder
          </button>
        </div>
      )}
    </div>
  );
};

export default KeyGenerator;