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
  const [data, setData] = useState([]);

  const funct = async () => {
    const response = await fetch("/api/data")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        return data;
      });
    setData(response);
  };

  return (
    <>
      <h1>Information</h1>
      <p>
        <button onClick={funct}> Refresh data</button>
      </p>
      <ul>
        {data.map((solverData, index) => (
          <li key={index}>
            <h2>{solverData[0]}</h2> 
            {Object.entries(solverData[1] as Record<string, unknown>).map(([fileName, fileData], fileIndex) => (
              <div key={fileIndex}>
                <h3>{fileName}</h3> 
                {Object.entries(fileData as Record<string, unknown>).map(([dataFileName, dataItems], dataIndex) => (
                  <div key={dataIndex}>
                    <h4>{dataFileName}</h4> 
                    <ul>
                      {(dataItems as DataItem[]).map((dataItem: DataItem, itemIndex) => (
                        <li key={itemIndex}>
                          Status: {dataItem.status} <br />
                          Opt Goal: {dataItem.opt_goal} <br />
                          Opt Value: {dataItem.opt_value} <br />
                          Execution Time: {dataItem.execution_time}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ))}
          </li>
        ))}
      </ul>
    </>
  );
}

export default Info;