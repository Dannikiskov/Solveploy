import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

// Components
import Mzn from "./Mzn";
import Sat from "./Sat";
import Maxsat from "./Maxsat";
import Nav from "./Nav";

function App() {
  return (
    <Router>
      <Nav />
      <Routes>
        <Route path="/mzn" element={<Mzn />} />
        <Route path="/sat" element={<Sat />} />
        <Route path="/maxsat" element={<Maxsat />} />
      </Routes>
    </Router>
  );
}

export default App;
