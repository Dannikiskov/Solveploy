import { useState } from "react";
import "./App.css";

interface DataItem {
  status: string;
  opt_goal: string;
  opt_value: string;
  data_file_name: string;
  execution_time: string;
}

function Info() {
  const [mznData, setMznData] = useState([]);
  const [satData, setSatData] = useState([]);
  const [maxsatData, setMaxsatData] = useState([]);

  const satGet = async () => {
    const response = await fetch("/api/data/sat")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        return data;
      });
      setSatData(response);
  }

  const maxsatGet = async () => {
    const response = await fetch("/api/data/maxsat")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        return data;
      });
      setMaxsatData(response);
  }

  const mznGet = async () => {
    const response = await fetch("/api/data/mzn")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        return data;
      });
      setMznData(response);
  };

  return (
    <>
      <h1>Information</h1>
      <h2>Minizinc</h2>
      <p>
        <button onClick={mznGet}> Refresh Minizinc data</button>
      </p>
      <ul>
        {mznData.map((solverData, index) => (
          <ul key={index}>
            <h2 style={{ border: '1px solid black', display: 'inline-block', padding: '8px', color: 'white' }}>{solverData[0]}</h2>
            {Object.entries(solverData[1] as Record<string, unknown>).map(([fileName, fileData], fileIndex) => (
              <div key={fileIndex}>
                <h3>{fileName}</h3> 
                {Object.entries(fileData as Record<string, unknown>).map(([dataFileName, dataItems], dataIndex) => (
                  <div key={dataIndex}>
                    <h4>{dataFileName}</h4> 
                    <ul>
                      {(dataItems as DataItem[]).map((dataItem: DataItem, itemIndex) => (
                        <ul key={itemIndex}>
                          Status: {dataItem.status} <br />
                          Opt Goal: {dataItem.opt_goal} <br />
                          Opt Value: {dataItem.opt_value} <br />
                          Execution Time: {dataItem.execution_time} milliseconds
                          <hr style={{margin: '2px'}} />
                        </ul>
                        
                      ))}
                      
                    </ul>
                  </div>
                ))}
              </div>
            ))}
            <hr style={{margin: '2px'}} />
          </ul>
        ))}
        <hr style={{margin: '2px'}} />
      </ul>
      <br />
      <h2>SAT</h2>
      <p>
        <button onClick={satGet}> Refresh SAT data</button>
        <ul>
          {satData}
        </ul>
      </p>
      <br />
      <h2>MAXSAT</h2>
      <p>
        <button onClick={maxsatGet}> Refresh MAXSAT data</button>
      </p>
      <ul>
        {maxsatData}
      </ul>
    </>
  );
}

export default Info;