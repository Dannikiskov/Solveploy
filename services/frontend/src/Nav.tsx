import React from "react";
import { Link } from "react-router-dom";
import "./App.css";

const Nav: React.FC = () => {

  return (
    <div>
      <h1>Solveploy</h1>
      <Link to="/mzn">
        <button style={{ marginRight: '5px' }}>MZN</button>
      </Link>
      <Link to="/sat">
        <button style={{ marginRight: '5px' }}>SAT</button>
      </Link>
      <Link to="/maxsat">
        <button>MAXSAT</button>
      </Link>
      <Link to="/info">
        <button style={{ marginLeft: '5px' }}>Info</button>
      </Link>
    </div>
  );
};

export default Nav;
