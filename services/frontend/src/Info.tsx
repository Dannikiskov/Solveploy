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
        {(data as any[]).map((item, index) => (
          <li key={index}>
            <h2>{item[0]}</h2> {/* This is the solver name */}
            {Object.entries(item[1]).map(([fileName, fileData], fileIndex) => (
              <div key={fileIndex}>
                <h3>{fileName}</h3> {/* This is the file name */}
                <ul>
                  {(fileData as DataItem[]).map((dataItem, dataIndex) => (
                    <li key={dataIndex}>
                      Data File Name: {dataItem.data_file_name} <br />
                      Status: {dataItem.status} <br />
                      Opt Goal: {dataItem.opt_goal} <br />
                      Opt Value: {dataItem.opt_value} <br />
                      Execution Time: {dataItem.execution_time}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </li>
        ))}
      </ul>
    </>
  );
}

export default Info;