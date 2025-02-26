import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL;

export const generateKey = async (useQuantumMethod) => {
  try {
    const response = await axios.post(`${API_URL}/generate-key/`, {
      quantum_method: useQuantumMethod,
    });
    return response.data;
  } catch (error) {
    console.error("Error al generar la clave:", error);
    throw error;
  }
};
