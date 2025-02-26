import { useLocation } from "react-router-dom";
import { useState } from "react";
import { useSnackbar } from "./snackBarComp";
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Grid2,
  CircularProgress,
} from "@mui/material";
import { motion } from "framer-motion";
import LockIcon from "@mui/icons-material/Lock";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import { encryptMessage, decryptMessage } from "../services/encryptationService";

const EncryptionScreen = () => {
  const location = useLocation();
  const selectedKey = location.state?.selectedKey;
  const message = location.state?.message;
  const alicekey = location.state?.aliceKey;
  const showSnackbar = useSnackbar();

  const [loading, setLoading] = useState(false);
  const [encryptedMessage, setEncryptedMessage] = useState("");
  const [decryptedMessage, setDecryptedMessage] = useState("");

  const handleEncrypt = async () => {
    setLoading(true);
    try {
      const encryptedData = await encryptMessage(message, alicekey);
      setEncryptedMessage(encryptedData);
    } catch {
      showSnackbar("Error al encriptar el mensaje", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDecrypt = async () => {
    setLoading(true);
    try {
      const decryptedData = await decryptMessage(encryptedMessage, selectedKey, encryptedMessage.iv);
      setDecryptedMessage(decryptedData);
    } catch {
      showSnackbar("Ocurrió un error al desencriptar", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundImage: "url('/image.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: "relative",
        px: 3,
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
          zIndex: 1,
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        style={{ zIndex: 2, width: "100%", maxWidth: "900px" }}
      >
        <Grid2 container spacing={4} alignItems="center"  sx={{ zIndex: 2, position: "relative" }}>
          <Grid2 item xs={12} md={6} size={6}>
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, delay: 0.3 }}
            >
              <Card
                sx={{
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                  backdropFilter: "blur(10px)",
                  color: "white",
                  borderRadius: "12px",
                  p: 3,
                }}
              >
                <CardContent>
                  <Box display="flex" flexDirection="column" alignItems="center" mb={2}>
                    <LockIcon sx={{ fontSize: 50, color: "#90caf9" }} />
                    <Typography variant="h5" gutterBottom>
                      Cifrado AES-128
                    </Typography>
                  </Box>
                  <Typography variant="body1" paragraph sx={{ opacity: 0.9 }}>
                    AES (Advanced Encryption Standard) es un algoritmo de cifrado simétrico 
                    utilizado para proteger datos. En este sistema, utilizamos una clave de 16 bits 
                    para cifrar los mensajes con seguridad.
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.8 }}>
                    Gracias a su estructura y resistencia a ataques, AES se ha convertido en 
                    el estándar global para la seguridad de la información.
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid2>

          
          <Grid2 item xs={12} md={7} size={6}>
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, delay: 0.5 }}
            >
              <Card
                sx={{
                  backgroundColor: "rgba(255, 255, 255, 0.15)",
                  backdropFilter: "blur(10px)",
                  color: "white",
                  borderRadius: "12px",
                  p: 3,
                  textAlign: "center",
                }}
              >
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Encriptación y Desencriptación 
                  </Typography>

                  <Typography variant="body1" sx={{ mb: 2 }}>
                    <strong>Mensaje enviado:</strong> {message}
                  </Typography>

                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleEncrypt}
                    sx={{ mb: 2, width: "100%" }}
                    disabled={loading}
                    startIcon={<LockIcon />}
                  >
                    {loading ? <CircularProgress size={24} color="inherit" /> : "Cifrar Mensaje"}
                  </Button>

                  {encryptedMessage && (
                    <>
                      <Typography variant="body1" sx={{ my: 2 }}>
                        <strong>Mensaje Cifrado:</strong> {encryptedMessage.ciphertext}
                      </Typography>
                      <Button
                        variant="contained"
                        color="secondary"
                        onClick={handleDecrypt}
                        sx={{ mb: 2, width: "100%" }}
                        disabled={loading}
                        startIcon={<VpnKeyIcon />}
                      >
                        {loading ? <CircularProgress size={24} color="inherit" /> : "Descifrar Mensaje"}
                      </Button>
                    </>
                  )}

                  {decryptedMessage && (
                    <Typography variant="body1" sx={{ mt: 2, color: "#90caf9" }}>
                      <strong>Mensaje Descifrado:</strong> {decryptedMessage}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid2>
        </Grid2>
      </motion.div>
    </Box>
  );
};

export default EncryptionScreen;
