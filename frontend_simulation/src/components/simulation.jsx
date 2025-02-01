import React, { useState } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";


const KeyExchange = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [useInterceptor, setUseInterceptor] = useState(false);
  const [possibleCircuits, setPossibleCircuits] = useState([]);
  const [finallyKey, setFinallyKey] = useState(null);
  const [privateKeyAlice, setPrivateKeyAlice] = useState(null);
  const [privateKeyBob, setPrivateKeyBob] = useState(null);
  const [publicKeyAlice, setPublicKeyAlice] = useState(null);
  const [publicKeyBob, setPublicKeyBob] = useState(null);




  const location = useLocation();
  const navigate = useNavigate();
  const selectedKey = location.state?.selectedKey;
  const message = location.state?.message;

  const getCSRFToken = () => {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];
  };

  const handleEncrypt = () => {
    navigate("/encrypt", { state: { selectedKey: finallyKey, message: message, aliceKey: privateKeyAlice } });
  };

  const handleShowCircuits = async () => {
    setLoading(true);
    try {

      const response = await axios.get(
        "http://127.0.0.1:8000/show-qcircuits/",
      );
      setPossibleCircuits(response.data.show_circuits);
    } catch (error) {
      console.error("Error al obtener circuitos:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCorrectKey = async () => {
    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/correct/", {
        alice_key: privateKeyAlice,
        bob_key: privateKeyBob,
      });
      setFinallyKey(response.data.corrected_key);
    } catch (error) {
      console.error("Error correcting key:", error);
    }
    setLoading(false);
  };

  const handleStartExchange = async () => {
    setLoading(true);

    try {
      if (selectedKey) {
        const csrfToken = getCSRFToken();
        if (!csrfToken) {
          console.error("CSRF token not found");
          return;
        }

        const response = await axios.post(
          "http://127.0.0.1:8000/simulate/",
          {
            alice_bits: selectedKey,
            interceptor: useInterceptor, 
            message_length: message.length
          });

        setResults(response.data);
        setFinallyKey(response.data.bob_key);
        setPrivateKeyAlice(response.data.private_key_alice)
        setPrivateKeyBob(response.data.private_key_bob)
        setPublicKeyAlice(response.data.public_key_alice)
        setPublicKeyBob(response.data.public_key_bob)
      }
    } catch (error) {
      console.error("Error al iniciar el intercambio de claves:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedKey) {
    return (
      <div style={{ textAlign: "center", marginTop: "2rem" }}>
        <h1>Error</h1>
        <p>No se seleccionó ninguna clave. Regresa al generador de claves.</p>
        <button onClick={() => navigate("/")}>Volver</button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Intercambio de Claves</h1>

      <button style={styles.button} onClick={handleShowCircuits}>
        Mostrar Circuitos
      </button>


      {possibleCircuits.length > 0 && (
        <div>
          <h2>Circuitos Cuánticos</h2>
          <div style={styles.circuitContainer}>
            {possibleCircuits.map((circuit, index) => (
              <div key={index}>
                <img src={`data:image/png;base64,${circuit.image}`} alt={`Circuit ${index + 1}` } style={styles.circuitImage} />
                <p style={{marginLeft: "50px"}}><strong>Bit: </strong> {circuit.bit} | <strong>Base: </strong> {circuit.base}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {!results && (
        <div style={styles.interceptorSection}>
          <label style={styles.label}>
            <input
              type="checkbox"
              checked={useInterceptor}
              onChange={(e) => setUseInterceptor(e.target.checked)}
            />
            Añadir Interceptor
          </label>
        </div>
      )}

      {!results && (
        <button style={styles.button} onClick={handleStartExchange} disabled={loading}>
          {loading ? "Procesando..." : "Iniciar Intercambio"}
        </button>
      )}
      {results && (
        <div style={styles.results}>
          <h2>Resultados</h2>
          <p>
            <strong>Clave de Alice:</strong> {results.alice_key}
          </p>
          <p>
            <strong>Clave de Bob:</strong> {results.bob_key}
          </p>
          <p>
            <strong>Clave de Alice pública:</strong> {publicKeyAlice}
          </p>
          <p>
            <strong>Clave de Bob pública:</strong> {publicKeyBob}
          </p>
          <p>
            <strong>Clave de Alice privada:</strong> {privateKeyAlice}
          </p>
          <p>
            <strong>Clave de Bob privada:</strong> {privateKeyBob}
          </p>
          <p>
            <strong>Porcentaje de error:</strong> {results.qber.toFixed(2)} %
          </p>
          <p>
            <strong>Porcentaje de error para la clave publicada:</strong> {results.qber_public.toFixed(2)} %
          </p>
        </div>
      )}
      {results && results.qber.toFixed(2)  && (
        <div>
          <button style={styles.button} onClick={handleEncrypt} disabled={loading}>
            Encriptar el mensaje
          </button>
        </div>
      )}

      {results && (
        <div>
          <button style={styles.button} onClick={handleCorrectKey} disabled={loading}>
            {loading ? "Corrigiendo..." : "Corregir Clave"}
          </button>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    textAlign: "center",
    padding: "50px",
  },
  title: {
    fontSize: "28px",
    marginBottom: "20px",
  },
  circuitContainer: {
    display: "flex",
    justifyContent: "center",  // Espaciado entre los circuitos
    alignItems: "center",  // Centrado verticalmente
    flexWrap: "wrap",  // Para que se ajuste en pantallas más pequeñas
    gap: "100px",
  },

  interceptorSection: {
    marginBottom: "20px",
  },
  button: {
    padding: "10px 20px",
    fontSize: "16px",
    backgroundColor: "#28A745",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    marginBottom: "20px",
  },
  results: {
    marginTop: "30px",
    textAlign: "left",
  },
};

export default KeyExchange;