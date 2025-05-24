import React from "react";
import Chatbot from "./Chatbot";

function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        minWidth: "100vw",
        backgroundImage: 'url("/background.png")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "fixed",
        inset: 0,
      }}
    >
      <Chatbot />
    </div>
  );
}

export default App;
