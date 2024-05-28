import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";;
import "./App.css";
import React, { useRef } from 'react';
import { saveAs } from 'file-saver';


interface SatSolverData {
  name: string;
  version: string;
  jobIdentifier: string;
  cpu?: number;
  memory?: number;
  cores?: number;
  params?: string; 
}

interface SatJobResult extends SatSolverData {
  result: string;
  executionTime?: number;
  status: string;
  optValue: number;
}

type SolverTimes = {
  [solver: string]: number;
};

type Schedule = {
  result: SolverTimes;
};


function Sat() {
  const dataFileInput = useRef(null);
  const satFileInput = useRef(null);
  const [satSolverList, setSatSolverList] = useState<SatSolverData[]>([]);
  const [selectedSatSolvers, setSelectedSatSolvers] = useState<SatSolverData[]>(
    []
  );
  const [expanded, setExpanded] = useState(false);
  const [t, setT] = useState<number>(0);
  const [k, setK] = useState<number>(0);
  const [satFileContent, setSatFileContent] = useState<string>("");
  const [satFileName, setSatFileName] = useState<string>("");
  const [runningSatJobs, setRunningSatJobs] = useState<SatSolverData[]>([]);
  const [bestResult, setBestResult] = useState<SatJobResult | null>(null);
  const [folderMapping, setFolderMapping] = useState<{ [key: string]: { sat: { file: File, content: string }[] } }>({});
  const [oneProb, setprob] = useState<boolean>(true);
  const [schedule, setSchedule] = useState<Schedule | null>(null);

  useEffect(() => {
    fetchDataGet();
  }, []);

  useEffect(() => {
    console.log("Selected solvers:", selectedSatSolvers);
  }, [selectedSatSolvers]);

  useEffect(() => {
    console.log(folderMapping)
  }, [folderMapping])

  useEffect(() => {
    console.log("Running solvers:", runningSatJobs);
  }, [runningSatJobs]);

  const clearFiles = () => {
    setSatFileContent("");
    if (dataFileInput.current) (dataFileInput.current as HTMLInputElement).value = "";
    if (satFileInput.current) (satFileInput.current as HTMLInputElement).value = "";
  };

  // const fetchStopJob = async (item: SatSolverData) => {
  //   setRunningSatJobs((prevItems: Array<SatSolverData>) =>
  //     prevItems.filter((i) => i.name !== item.name)
  //   );

  //   const solverId = item.jobIdentifier;
  //   console.log("Solver ID: ", solverId)
  //   try {
  //     const response = await fetch(`/api/jobs/sat/${solverId}`, {
  //       method: "DELETE",
  //       headers: {
  //         "Content-Type": "application/json",
  //       },
  //     });

  //     if (!response.ok) {
  //       throw new Error(`Error stopping solvers: ${response.statusText}`);
  //     }
  //   } catch (error) {
  //     console.error("Error stopping solvers:", error);
  //   }
  // };

  const fetchDataGet = async () => {
    try {
      const response = await fetch("/api/solvers/sat", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      const updatedData = data.map((item: SatSolverData) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
        cpu: 0,
        memory: 0,
      }));
      setSatSolverList(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleItemClick = (item: SatSolverData) => {
    if (selectedSatSolvers.find((i: any) => i.name === item.name)) {
      setSelectedSatSolvers((prevItems: Array<SatSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedSatSolvers((prevItems: Array<SatSolverData>) => [
        ...prevItems,
        item,
      ]);
    }
    //console.log(selectedSatSolvers);
  };

  const handleStartSolvers = () => {
    setBestResult(null);
    setRunningSatJobs(selectedSatSolvers);
    selectedSatSolvers.forEach(fetchStartSolvers);
    setSelectedSatSolvers([]);
    setSatSolverList((prevList) =>
      prevList.map((item) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }))
    );
  };

  const updateItemCpu = (item: SatSolverData, cpu: number) => {
    setSatSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, cpu } : prevItem
      )
    );
    console.log(item.cpu)
  }

  const updateItemMemory = (item: SatSolverData, memory: number) => {
    setSatSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, memory } : prevItem
      )
    );
    console.log(item.memory);
  }

  const updateItemCores = (item: SatSolverData, cores: number) => {
    setSatSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, cores } : prevItem
      )
    );
    console.log(item.memory);
  }

  const updateItemParams = (event: React.ChangeEvent<HTMLInputElement>, item: SatSolverData) => {
      const file = event.target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          const fileContent = reader.result as string;
          setSatSolverList((prevList) =>
            prevList.map((prevItem) =>
              prevItem.name === item.name ? { ...prevItem, params: fileContent } : prevItem
            )
          );
        };
        reader.readAsText(file);
      }
      console.log(item.params);
  }

  const fetchStartSolvers = async (item: SatSolverData) => {
    console.log("satFileName ", satFileName)
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item,
          satFileContent,
          satFileName,
          instructions: "StartSatJob",
          optGoal: "satisfy",
        }),
      });

      await response.json() as any;
      //console.log(data);
      // fetch("/api/jobs/sat", {
      //   method: "DELETE",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      // });
      
      // Remove the item from runningSatSolvers list
      setRunningSatJobs((prevItems: Array<SatSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );

    } catch (error) {
      console.error("Error starting solvers:", error);
    }
  }

  const fetchStartSolverWithContent = (item: SatSolverData, satString: string, fileName: string) => {
    console.log("ITEM: ", item)
    console.log("SAT: ", satString)
    const updatedItem = {
      ...item,
      jobIdentifier: uuidv4().slice(0, 8),
    };

    fetch("/api/jobs", {
      method: "POST",
      headers: {
      "Content-Type": "application/json",
      },
      body: JSON.stringify({
      item: updatedItem,
      satFileContent : satString,
      satFileName: fileName,
      instructions: "StartSatJob",
      noresult: true
      }),
    }).catch(error => {
      console.error("Error starting solvers:", error);
    });
  }


  const handleSatFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSatFileName(file.name);
      const reader = new FileReader();
      reader.onload = () => {
        const fileContent = reader.result as string;
        setSatFileContent(fileContent);
      };
      reader.readAsText(file);
    }
  };


  const downloadResult = () => {
    if (!bestResult) return;
  
    const content = `Solver Information
Name: ${bestResult.name}
Version: ${bestResult.version}
Output
Status: ${bestResult.status}
Execution Time: ${bestResult.executionTime} milliseconds
Result: 
${bestResult.result}
    `;
  
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    saveAs(blob, 'result.txt');
  };


  // const stopAllSolvers = async () => {
  //   setRunningSatJobs([]);
  //   try {
  //     const response = await fetch("/api/jobs/sat", {
  //       method: "DELETE",
  //       headers: {
  //         "Content-Type": "application/json",
  //       },
  //     });
  //     if (!response.ok) {
  //       console.error("Error stopping all solvers:", response.statusText);
  //     }
  //   } catch (error) {
  //     console.error("Error stopping all solvers:", error);
  //   }
  // };


  async function startSunny(): Promise<any> {
    console.log("Starting SUNNY");
    console.log("k: ", k);
    console.log("T: ", t);
    console.log("solvers:", selectedSatSolvers);
    const response = await fetch("/api/sunny", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        k,
        T: t,
        solvers: selectedSatSolvers,
        backupSolver: selectedSatSolvers[selectedSatSolvers.length - 1],
        fileContent: satFileContent,
        solverType: "sat",
      }),
    });
    if (!response.ok) {
      console.error("Error starting SUNNY:", response.statusText);
    }
    console.log("SUNNY started");
    setSelectedSatSolvers([]);
    let responeAsJson = await response.json();
    console.log(responeAsJson);
    setSchedule(responeAsJson);
  }

  const handleFolderChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileMapping: { [key: string]: {
        sat: { file: File, content: string }[]; }
      } = {}; // Wrap the entire destructuring assignment in parentheses
  
      for (let i = 0; i < e.target.files.length; i++) {
        const file = e.target.files[i] as any;
        const pathParts = file.webkitRelativePath.split('/');
        const folder = pathParts[pathParts.length - 2]; // Get the parent folder name
  
        if (!fileMapping[folder]) {
          fileMapping[folder] = { sat: [] };
        }
  
        const fileContent = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = event => resolve(event.target?.result as string);
          reader.onerror = error => reject(error);
          reader.readAsText(file);
        });

        if (file.name.endsWith('.cnf')) {
          fileMapping[folder].sat.push({ file, content: fileContent });
        }
      }
  
      // console.log(fileMapping);
      setFolderMapping(fileMapping);
    }
  };

  const startSolverWithAllFiles = async () => {
    for (const solver of selectedSatSolvers) {
      for (const folder in folderMapping) {
        console.log(folder)
        const { sat } = folderMapping[folder];
        if (sat) {
          for (const file of sat) {
            fetchStartSolverWithContent(solver, file.content, file.file.name);
          }
        }
      }
    }
  }

  async function handleRefresh(): Promise<void> {
    try {
      const response = await fetch("/api/results", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item: bestResult,
          type: "sat",
          optGoal: "satisfy",
        }),
      });
      if (!response.ok) {
        console.error("Error fetching results:", response.statusText);
        return; // Exit early if response is not OK
      }
      const data = await response.json() as SatJobResult;
      console.log("DATA", data);
      if (data != null){
        setBestResult(data);
      }
      
      
    } catch (error) {
      console.error("Error fetching results:", error);
    }
  }
  


  return (
    <>
    <br />
    <div>
      <button className="small-button" style={{ marginRight: '5px' }} onClick={() => setprob(true)}>Solve problem</button>
      <button className="small-button" onClick={() => setprob(false)}>Knowledge base expansion</button>
    </div>
    <div>
      <hr style={{margin: '20px'}} />
    </div>
    <div>
      {oneProb ? (
        <div>
          <div>
            <h3>Upload SAT file</h3>
            <input ref={satFileInput} onChange={handleSatFileChange} type="file" />
          </div>
          <br></br>
          <div>
            <br></br>
            <button className="small-button" style={{margin: '20px'}} onClick={clearFiles}>Clear files</button>
          </div>
          <hr style={{margin: '20px'}} />
          <br />
          <button onClick={() => setExpanded(!expanded)}>SUNNY</button>
      <br />
      {expanded && (
        <div>
          Last chosen solver is backup solver.
          <br />
          <input
            type="text"
            placeholder="k"
            onChange={(e) => setK(Number(e.target.value))}
          />
          <br />
          <input
            type="text"
            placeholder="T"
            onChange={(e) => setT(Number(e.target.value))}
          />
          <br />
          <button onClick={startSunny}>Get SUNNY portfolio</button>
          {schedule && (
              <div>
                <h3>Schedule</h3>
                <div>
                  {Object.entries(schedule.result).map(([solver, time], index) => (
                    <div key={index}>
                      {solver}: {time} milliseconds
                    </div>
                  ))}
                </div>
              </div>
            
            )}
        </div>
        
      )}
        </div>
      ) : (
        <div>
          <h3>Upload folder</h3>
          {React.createElement('input', {
            type: 'file',
            webkitdirectory: '',
            mozdirectory: '',
            directory: '',
            onChange: handleFolderChange
          })}
        </div>
      )}
    </div>
      
      <div>
        <br />
      </div>
      <br />
      <h2>Available Solvers</h2>
      <div className="grid">
        {satSolverList.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedSatSolvers.find((i) => i.name === item.name) ? "selected" : ""
            }`}
          >
            <div>Name: {item.name}</div>
            <div>Version: {item.version}</div>
            <div>
              <input
                type="number"
                placeholder="CPU"
                onChange={(e) => {updateItemCpu(item, Number(e.target.value))}}
              />
              <br />
              <input
                type="number"
                placeholder="Memory"
                onChange={(e) => {updateItemMemory(item, Number(e.target.value))}}
              />
              <br />
              {item.name === "glucose421" && (
              <input
                type="number"
                placeholder="Cores"
                onChange={(e) => {updateItemCores(item, Number(e.target.value))}}
              />
            )}
            {item.name === "gimsatul" && (
              <input
                type="number"
                placeholder="Cores"
                onChange={(e) => {updateItemCores(item, Number(e.target.value))}}
              />
            )}
            
            <br style={{marginBottom: '5px'}} />
            <input onChange={(e) => {updateItemParams(e, item)}} type="file" />
            <br />
            <button className="small-button" onClick={() => handleItemClick(item)} disabled={!item.memory || !item.cpu}>Select</button>
            </div>
            </div>
      
        ))}
      </div>
      <br />
      <hr style={{margin: '20px'}} />
      <div>
        <div style={{ marginBottom: '20px' }}>

  
        </div>
      {oneProb ? (
        <div>

        <button  onClick={handleStartSolvers} >Start Solvers</button>  
        </div>
      ) : (
        <div>
          <button onClick={startSolverWithAllFiles} >Start Solvers + </button>
        </div>
      )}
    </div>
      <br />
      <div >
        <h2>Running Solvers</h2>
        <div className="grid">
          {runningSatJobs.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              {/* <button className="small-button" onClick={() => fetchStopJob(item)}>Stop Solver</button> */}
        </div>
          ))}
        
        </div>
        </div>
        {/* <button className="small-button" onClick={stopAllSolvers}>Stop All Solvers</button> */}
        <div>
        <br />
        <h2>Result</h2>
        <div>    
          {bestResult && (
            <div className="result-container">
              <h4>Solver Information</h4>
              <div>Name: {bestResult.name}</div>
              <div>Version: {bestResult.version}</div>
              <h4>Output</h4>
              <div>Status: {bestResult.status}</div>
              <div>Execution Time: {bestResult.executionTime} milliseconds</div>
              <div>Result: {bestResult.result}</div>
              <br />
              <button onClick={downloadResult}>Download Result</button>
            </div>
          )}
        </div>
        <div style={{ marginBottom: '20px' }}>
          <button onClick={handleRefresh}>Refresh Result</button>
        </div>
      </div>
    </>
  );
}

export default Sat;



