import logo from './logo.svg';
import { BrowserRouter as Router, Route, Routes, useNavigate } from "react-router-dom";
import React, { useEffect } from "react";
import './App.css';
import Home from "./components/home";
import KeyExchange from "./components/simulation";
import KeyGeneration from "./components/generateKey";
import EncryptionScreen from "./components/encrypt";
import MessageInput from "./components/message";
import { getCSRFToken } from "./utils/utils"
import { SnackbarProvider } from "./components/snackBarComp";

const App = () => {

  useEffect(() => {
    getCSRFToken();
  }, []);

  return (
    <SnackbarProvider>
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/message" element={<MessageInput />} />
        <Route path="/key-exchange" element={<KeyExchange />} />
        <Route path="/key-generation" element={<KeyGeneration />} />
        <Route path="/encrypt" element={<EncryptionScreen />} />
      </Routes>
    </Router>
    </SnackbarProvider>
  );
};

const HomePage = () => {
  const navigate = useNavigate();
  return <Home onStart={() => navigate("/message")} />;
};

export default App;