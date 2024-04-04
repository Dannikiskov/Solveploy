import React from "react";
import { Link } from "react-router-dom";
import "./App.css";

const Nav: React.FC = () => {
  return (
    <div>
      <h1>Solveploy</h1>
      <Link to="/mzn">
        <button>MZN</button>
      </Link>
      <Link to="/sat">
        <button>SAT</button>
      </Link>
      <Link to="/maxsat">
        <button>MAXSAT</button>
      </Link>
    </div>
  );
};

export default Nav;
