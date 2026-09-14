import React from "react";
import "./SplashScreen.css";
import logo from "../assets/logo.png";

export default function SplashScreen() {
  return (
    <div className="splash-screen" role="status" aria-label="Loading conversational AI platform">
      <img src={logo} alt="Conversational AI Platform logo" className="splash-logo" />
    </div>
  );
}
