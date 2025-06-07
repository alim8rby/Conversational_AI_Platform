import React from "react";
import "./SettingsPanel.css";

// Put a demo photo (e.g. user.jpg) in /public/
// it will be served from "/user.jpg".
export default function SettingsPanel({ theme, setTheme }) {
  return (
    <aside className="settings-panel">
      <div className="settings-panel__user">
        <img
          src="/user.jpg"
          alt="Demo User"
          className="settings-panel__avatar"
        />
        <span className="settings-panel__name">Demo User</span>
      </div>

      <div className="settings-panel__group">
        <label>Theme</label>
        <div className="settings-panel__toggle">
          <button
            className={theme === "light" ? "active" : ""}
            onClick={() => setTheme("light")}
          >
            Light
          </button>
          <button
            className={theme === "dark" ? "active" : ""}
            onClick={() => setTheme("dark")}
          >
            Dark
          </button>
        </div>
      </div>
    </aside>
  );
}
