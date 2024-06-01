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
  const [satData, setSatData] = useState<any[]>([]);
  
  const satGet = async () => {
    const response = await fetch("/api/data/sat")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        return data;
      });
      setSatData(response);
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
            <h2 style={{ border: '1px solid white', display: 'inline-block', padding: '8px'}}>{solverData[0]}</h2>
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
                          Goal: {dataItem.opt_goal} <br />kgp
                          Objective: {dataItem.opt_value} <br />
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
      </p>
      <div>
      {satData.map(([solverName, files]) => (
      <div key={solverName}>
        <h2 style={{ border: '1px solid white', display: 'inline-block', padding: '8px'}}>{solverName}</h2>
        {files.map((file: { sat_file_name: string, status: string, execution_time: number }) => (
        <div key={file.sat_file_name}>
          <p>SAT File Name: {file.sat_file_name}</p>
          <p>Status: {file.status}</p>
          <p>Execution Time: {file.execution_time} seconds</p>
          <hr style={{margin: '2px'}} />
        </div>
        
      ))}
      <hr style={{margin: '2px'}} />
      </div>
    ))}
    <hr style={{margin: '2px'}} />
      </div>
    </>
  );
}

export default Info;