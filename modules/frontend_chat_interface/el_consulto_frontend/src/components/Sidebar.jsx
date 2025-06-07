import React from 'react';
import logo from '../assets/logo.png';
import './Sidebar.css';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <img src={logo} alt="El Consulto Logo" className="sidebar__logo" />
      <h2 className="sidebar__title">الكُونْسُلْتُو<br/>EL CONSULTO</h2>
    </aside>
  );
}
