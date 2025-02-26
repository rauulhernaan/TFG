import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useSnackbar } from "./snackBarComp";
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CardMedia,
  CircularProgress,
  Grid2,
  Switch,
  FormControlLabel,
} from "@mui/material";
import { motion } from "framer-motion";
import { startKeyExchange, correctKey, getQuantumCircuits } from "../services/simulationService";


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
  const showSnackbar = useSnackbar();

  const location = useLocation();
  const navigate = useNavigate();
  const selectedKey = location.state?.selectedKey;
  const message = location.state?.message;

  const handleEncrypt = () => {
    navigate("/encrypt", {
      state: { selectedKey: finallyKey, message: message, aliceKey: privateKeyAlice },
    });
  };

  const handleCorrectKey = async () => {
    setLoading(true);
    try {
      const data = await correctKey(results.alice_key, results.bob_key);
      setFinallyKey(data.corrected_key);
    } catch (error) {
      showSnackbar("Error al corregir la clave", "error");
    }
    setLoading(false);
  };

  const handleShowCircuits = async () => {
    setLoading(true);
    try {
      const circuits = await getQuantumCircuits();
      setPossibleCircuits(circuits);
    } catch (error) {
      showSnackbar("Error al obtener circuitos", "error");
    }
    setLoading(false);
  };

  const handleStartExchange = async () => {
    setLoading(true);
    try {
      if (selectedKey) {
        const data = await startKeyExchange(selectedKey, useInterceptor);
        setResults(data);
        setFinallyKey(data.bob_key);
        setPrivateKeyAlice(data.private_key_alice);
        setPrivateKeyBob(data.private_key_bob);
        setPublicKeyAlice(data.public_key_alice);
        setPublicKeyBob(data.public_key_bob);
      }
    } catch (error) {
      showSnackbar("Error al iniciar el intercambio de claves", "error");
    }
    setLoading(false);
  };

  const highlightDifferences = (aliceKey, bobKey) => {
    return aliceKey.split('').map((bit, index) => {
      if (bit !== bobKey[index]) {
        return <span key={index} style={{ color: "red", fontWeight: "bold" }}>{bit}</span>;
      } else {
        return <span key={index}>{bit}</span>;
      }
    });
  };

  return (
    <Box
      sx={{
        minHeight: "100vh", 
        backgroundImage: "url('/image.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        color: "white",
        position: "relative",
        backgroundAttachment: "fixed", 
      }}
    >
      <Box
        sx={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
        }}
      />
      <Container sx={{ zIndex: 1, textAlign: "center", maxWidth: "md" }}>
        <Typography variant="h3" gutterBottom marginTop={1}>
          Intercambio de Claves BB84
        </Typography>
        <Card sx={{ backgroundColor: "rgba(255, 255, 255, 0.15)", color: "white", padding: "10px", mt: 3, mb: 3 }}>
            <CardContent>
              <Typography variant="body1" paragraph>
                Esta simulación utiliza el protocolo BB84 para realizar el intercambio de claves cuánticas. A través de este protocolo, Alice y Bob pueden intercambiar una clave secreta con seguridad, incluso si un interceptor está presente en el canal de comunicación. La simulación está implementada con Qiskit, una herramienta de computación cuántica, y la corrección de errores se realiza mediante el uso de un algoritmo de reconciliación.
              </Typography>

            </CardContent>
        </Card>
       
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
         
          <Button variant="contained" color="secondary" onClick={handleShowCircuits} sx={{ width: "32%" }}>
            {loading ? <CircularProgress size={24} /> : "Mostrar Circuitos"}
          </Button>
          
       
          <FormControlLabel
            control={<Switch checked={useInterceptor} onChange={(e) => setUseInterceptor(e.target.checked)} />}
            label={<Typography>Añadir Interceptor</Typography>}
            sx={{ width: "32%" }}
          />
          
         
          <Button variant="contained" color="success" onClick={handleStartExchange} disabled={loading} sx={{ width: "32%" }}>
            {loading ? <CircularProgress size={24} /> : "Iniciar Intercambio"}
          </Button>
        </Box>

        {possibleCircuits.length > 0 && (
          <Grid2 container spacing={3} justifyContent="center">
            {possibleCircuits.map((circuit, index) => (
              <Grid2 item key={index} xs={12} sm={6} md={4}>
                <motion.div whileHover={{ scale: 1.05 }}>
                  <Card sx={{ background: "#ffffffcc" }}>
                    <CardMedia
                      component="img"
                      style={{ width: "100%", height: "auto", maxHeight: "300px" }}
                      image={`data:image/png;base64,${circuit.image}`}
                      alt={`Circuit ${index + 1}`}
                    />
                    <CardContent>
                      <Typography variant="body1"><strong>Bit:</strong> {circuit.bit}</Typography>
                      <Typography variant="body1"><strong>Base:</strong> {circuit.base}</Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid2>
            ))}
          </Grid2>
        )}
        
        {results && (
          <Card sx={{ backgroundColor: "rgba(255, 255, 255, 0.15)", color: "white", padding: "20px", mt: 3, mb: 3 }}>
            <CardContent>
              <Typography variant="h5" mb={2} >Resultados</Typography>
              <Typography><strong>Clave de Alice:</strong> {results.alice_key}</Typography>
              <Typography><strong>Clave de Bob:</strong> {results.bob_key}</Typography>
              <Typography><strong>Clave de Alice pública:</strong> {publicKeyAlice}</Typography>
              <Typography><strong>Clave de Bob pública:</strong> {publicKeyBob}</Typography>
              <Typography><strong>Clave de Alice privada:</strong> {privateKeyAlice}</Typography>
              <Typography><strong>Clave de Bob privada:</strong> {privateKeyBob}</Typography>
              <Typography><strong>Porcentaje de error:</strong> {results.qber?.toFixed(2)}%</Typography>
              <Typography><strong>Porcentaje de error para la clave publicada:</strong> {results.qber_public?.toFixed(2)}%</Typography>
              <Typography variant="body1"  mt={2} mb={2}>
                <strong>Bits diferentes entre las claves de Alice y Bob: </strong>
                {highlightDifferences(results.alice_key, finallyKey)}
              </Typography>

              <Box sx={{ display: "flex", justifyContent: "center", gap: "16px", mt: 2 }}>
                <Button variant="contained" color="primary" onClick={handleEncrypt}>
                   Encriptar el mensaje
                </Button>
                
                <Button variant="contained" color="error" onClick={handleCorrectKey} disabled={loading}>
                  {loading ? "Corrigiendo..." : "Corregir Clave"}
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}
      </Container>
    </Box>
  );
};

export default KeyExchange;
