import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { Box, Button, Typography, CircularProgress, Card, CardContent, LinearProgress, Chip, Divider } from "@mui/material";
import Grid from '@mui/material/Grid2';
import { motion } from "framer-motion";
import { useSnackbar } from './snackBarComp';
import SecurityIcon from '@mui/icons-material/Security';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import BarChartIcon from '@mui/icons-material/BarChart';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';


const KeyGenerator = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [key, setKey] = useState("");
  const [entropy, setEntropy] = useState(null);
  const [randomnessTests, setRandomnessTests] = useState(null);
  const [loading, setLoading] = useState(false);
  const message = location.state?.message;
  const showSnackbar = useSnackbar();

  const generateKey = async () => {
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/generate-key/");
      setKey(response.data.key);
      setEntropy(response.data.entropy);
      setRandomnessTests(response.data.randomness_tests);
    } catch (error) {
      showSnackbar("Error al generar la clave", 'error');
    }
    setLoading(false);
  };

  const handleAcceptKey = () => {
    navigate("/key-exchange", { state: { selectedKey: key, message: message } });
  };


  return (
    <Box
      sx={{
        height: "100vh",
        backgroundImage: "url('/image.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        color: "white",
        position: "relative",
      }}
    >
      {/* Filtro oscuro */}
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

      {/* Contenido en dos columnas */}
      <Grid container spacing={4} sx={{ zIndex: 2, position: "relative", maxWidth: "1200px" }}>
        <Grid item xs={12} md={5} size={4}>
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card sx={{ backgroundColor: "rgba(255, 255, 255, 0.15)", color: "white", padding: "20px" }}>
              <CardContent>
                <Divider aria-hidden="true" sx={{ my: 2 }}  >
                    <Chip
                      icon={<SecurityIcon />}
                      label="Tipo de Clave Segura"
                      color="primary"
                      sx={{ fontSize: "16px", fontWeight: "bold", padding: "10px" }}
                    />
                </Divider>
                <Typography variant="body1">
                  En esta etapa, se generará una clave de <strong>64 bits</strong> utilizando un modelo de 
                  <strong> inteligencia artificial de tipo GAN (Generative Adversarial Network)</strong>. 
                  Este enfoque permite mejorar la aleatoriedad y seguridad de la clave.
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Sección derecha: Generación y resultados */}
        <Grid item xs={12} md={7} size={7}>
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card sx={{ backgroundColor: "rgba(255, 255, 255, 0.2)", color: "white", padding: "20px" }}>
              <CardContent>
                <Box sx={{ 
                    display: "flex", 
                    flexDirection: "column", 
                    alignItems: "center", 
                    justifyContent: "center", 
                    textAlign: "center" 
                  }}>
                  <Typography sx={{ justifyContent: 'center' }} variant="h5" gutterBottom>Generador de Claves</Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={generateKey}
                    disabled={loading}
                    sx={{ mt: 2 }}
                  >
                    {loading ? <CircularProgress size={24} sx={{ color: "white" }} /> : "Generar Clave"}
                  </Button>
                </Box>

                {/* Resultados */}
                {key && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    style={{ marginTop: "20px" }}
                  >
                    {/* Clave generada */}
                    <Typography variant="h6" gutterBottom sx={{ mt: 2, display: "flex", alignItems: "center" }}>
                      <VpnKeyIcon sx={{ marginRight: 1 }} /> Clave Generada:
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        wordBreak: "break-word",
                        backgroundColor: "rgba(0, 0, 0, 0.3)",
                        padding: "10px",
                        borderRadius: "8px",
                      }}
                    >
                      {key}
                    </Typography>

                    {/* Resultados visuales */}
                    <Typography variant="h6" sx={{ mt: 3, display: "flex", alignItems: "center" }}>
                      <BarChartIcon sx={{ marginRight: 1 }} /> Calidad de la Clave:
                    </Typography>

                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2">🧩 Entropía Binaria:</Typography>
                      <LinearProgress variant="determinate" value={entropy * 100} sx={{ height: 10, borderRadius: 5 }} />
                    </Box>

                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2">📏 Prueba Monobit:</Typography>
                      <LinearProgress variant="determinate" value={randomnessTests?.monobit * 100} sx={{ height: 10, borderRadius: 5 }} />
                    </Box>

                    <Button
                      variant="contained"
                      startIcon={<CheckCircleIcon />}
                      sx={{
                        mt: 3,
                        backgroundColor: "green" ,
                        cursor:"pointer",
                      }}
                      onClick={handleAcceptKey}
                      disabled={false}
                    >
                      Aceptar y Proceder
                    </Button>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default KeyGenerator;
