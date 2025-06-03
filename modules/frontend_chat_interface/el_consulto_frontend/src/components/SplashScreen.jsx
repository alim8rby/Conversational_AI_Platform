// src/components/SplashScreen.jsx
import React from "react";
import "./SplashScreen.css";
import logo from "../assets/logo.png"; // adjust path if needed

export default function SplashScreen() {
  return (
    <div className="splash-screen">
      <img src={logo} alt="El Consulto Logo" className="splash-logo" />
    </div>
  );
}
