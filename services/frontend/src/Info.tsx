// import { useState } from "react";
import { useEffect } from "react";

import "./App.css";





function Info() {

    useEffect(() => {
        fetch("/api/data")
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
          });
      });


  return (
    <>
        <h1>Information</h1>
        <p>
            This is a simple web application that allows you to solve
            optimization problems using different solvers.
        </p>
    </>
  );
}

export default Info;




