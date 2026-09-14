import React from "react";
import logo from "../assets/logo.png";
import "./Sidebar.css";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <img src={logo} alt="Conversational AI Platform logo" className="sidebar__logo" />
      <h2 className="sidebar__title">CONVERSATIONAL<br />AI</h2>
    </aside>
  );
}
