// import { useState } from "react";
// import { useEffect } from "react";

import { Key, useState } from "react";
import "./App.css";





function Info() {
    const [data, setData] = useState([]);

    const funct = async () => {
      const response = await fetch("/api/data")
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          return data; // Return the data instead of void
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
              {Array.isArray(item) ? (
                <ul>
                  {item.map((subItem: any, subIndex: Key | null | undefined) => (
                    <li key={subIndex}>{JSON.stringify(subItem)}</li>
                  ))}
                </ul>
              ) : (
                JSON.stringify(item)
              )}
            </li>
          ))}
        </ul>
    </>
  );
}

export default Info;




