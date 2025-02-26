import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSnackbar } from "./snackBarComp";
import { Box, Button, TextField, Typography, Paper } from "@mui/material";
import { motion } from "framer-motion";
import LockIcon from "@mui/icons-material/Lock";

const MessageInput = () => {
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const showSnackbar = useSnackbar();

  const handleNext = () => {
    if (!message) return showSnackbar("Por favor introduzca un mensaje", "warning");
    navigate("/key-generation", { state: { message } });
  };

  return (
    <Box
      sx={{
        height: "100vh",
        backgroundImage:
          "url('./image.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        textAlign: "center",
        position: "relative",
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
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ zIndex: 2 }}
      >
        <Paper
          elevation={8}
          sx={{
            padding: "30px",
            borderRadius: "10px",
            maxWidth: "450px",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(10px)",
            color: "white",
          }}
        >
          <Box display="flex" flexDirection="column" alignItems="center" mb={2}>
            <LockIcon sx={{ fontSize: 50, color: "#90caf9" }} />
            <Typography variant="h4" gutterBottom>
              Protocolo BB84 
            </Typography>
          </Box>

          <Typography variant="body1" paragraph sx={{ fontSize: "16px", opacity: 0.8 }}>
            BB84 es un protocolo de distribución cuántica de claves (QKD) que permite
            compartir claves secretas de manera segura. Se basa en la mecánica cuántica para
            prevenir ataques de espionaje.
          </Typography>

          <Typography variant="h5" gutterBottom>
             Escribe tu Mensaje
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Escribe aquí..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            variant="outlined"
            sx={{
              bgcolor: "rgba(255, 255, 255, 0.2)",
              borderRadius: "5px",
              input: { color: "white" },
              textarea: { color: "white" },
              "& .MuiOutlinedInput-notchedOutline": { borderColor: "white" },
              "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#90caf9" },
              "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#2196f3" },
            }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            sx={{ marginTop: "20px", width: "100%" }}
          >
            Siguiente
          </Button>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default MessageInput;
