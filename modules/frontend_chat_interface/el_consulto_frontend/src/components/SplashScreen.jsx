import React from "react";
import "./SplashScreen.css";
import logo from "../assets/logo.png";

export default function SplashScreen() {
  return (
    <div
      className="splash-screen"
      role="status"
      aria-label="Loading El Consulto"
    >
      <img
        src={logo}
        alt="El Consulto Logo"
        className="splash-logo"
      />
    </div>
  );
}
