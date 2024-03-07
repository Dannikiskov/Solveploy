import React from 'react';
import { Link } from 'react-router-dom';
import './App.css';

const Nav: React.FC = () => {
    return (
        <div>
            <Link to="/mzn"><button>Minizinc</button></Link>
            <Link to="/sat"><button>Satisfiability</button></Link>
        </div>
    );
};

export default Nav;