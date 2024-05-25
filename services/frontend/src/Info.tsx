// import { useState } from "react";
// import { useEffect } from "react";

import "./App.css";





function Info() {

    const funct = () => {
      fetch("/api/data")
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        });
    };


  return (
    <>
        <h1>Information</h1>
        <p>
            <button onClick={funct}> Click me </button>
        </p>
    </>
  );
}

export default Info;




