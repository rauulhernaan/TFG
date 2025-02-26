import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL; 

export const startKeyExchange = async (selectedKey, useInterceptor) => {
  try {
    const response = await axios.post(`${API_URL}/simulate/`, {
      alice_bits: selectedKey,
      interceptor: useInterceptor,
    });
    return response.data;
  } catch (error) {
    console.error("Error al iniciar el intercambio de claves:", error);
    throw error;
  }
};

export const correctKey = async (aliceKey, bobKey) => {
  try {
    const response = await axios.post(`${API_URL}/correct/`, {
      alice_key: aliceKey,
      bob_key: bobKey,
    });
    return response.data;
  } catch (error) {
    console.error("Error al corregir la clave:", error);
    throw error;
  }
};

export const getQuantumCircuits = async () => {
  try {
    const response = await axios.get(`${API_URL}/show-qcircuits/`);
    return response.data.show_circuits;
  } catch (error) {
    console.error("Error al obtener circuitos cuánticos:", error);
    throw error;
  }
};
