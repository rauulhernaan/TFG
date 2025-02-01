import React from "react";
import './home.scss'

const Home = ({ onStart }) => {
  return (
    <div className="container">
      <h1 className="tittle">Simulación QKD BB84</h1>
      <p className="description">
        Bienvenido a la simulación del protocolo BB84 para intercambio de claves cuánticas.
        Presiona el botón para comenzar.
      </p>
      <button className="button" onClick={onStart}>
        Comenzar Intercambio de Claves
      </button>
    </div>
  );
};


export default Home;
