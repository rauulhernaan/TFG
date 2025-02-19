import React from "react";
import { Box, Button, Typography } from "@mui/material";
import * as motion from "motion/react-client"

const Home = ({ onStart }) => {
  return (
    <Box
      sx={{
        height: "100vh",
        backgroundImage: "url('https://images.unsplash.com/photo-1534744971734-e1628d37ea01?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        textAlign: "center",
        color: "white",
        position: "relative",
      }}
    >
      {/* Filtro de fondo oscuro */}
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
      <Box sx={{ zIndex: 2, position: "relative" }}>
        <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
                duration: 0.4,
                scale: { type: "spring", visualDuration: 0.4, bounce: 0.5 },
            }}
            
            >
          <Typography variant="h3" gutterBottom>
            Simulación QKD BB84
          </Typography>
          <Typography variant="body1" paragraph>
            Bienvenido a la simulación del protocolo BB84 para intercambio de claves cuánticas.
            Presiona el botón para comenzar.
          </Typography>
          <Button variant="contained" color="primary" onClick={onStart}>
            Comenzar Intercambio de Claves
          </Button>
        </motion.div>
      </Box>


    </Box>
  );
};

export default Home;
