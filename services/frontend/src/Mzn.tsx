import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";;
import "./App.css";
import React, { useRef } from 'react';
import { saveAs } from 'file-saver';


interface MznSolverData {
  name: string;
  jobIdentifier: string;
  cpu?: number;
  memory?: number;
  params?: string; 
}

interface MznJobResult extends MznSolverData {
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

function Mzn() {
  const dataFileInput = useRef(null);
  const mznFileInput = useRef(null);
  const [mznSolverList, setMznSolverList] = useState<MznSolverData[]>([]);
  const [selectedMznSolvers, setSelectedMznSolvers] = useState<MznSolverData[]>(
    []
  );
  const [expanded, setExpanded] = useState(false);
  const [dznOrJson, setDznOrJson] = useState<string>("dzn");
  const [t, setT] = useState<number>(0);
  const [k, setK] = useState<number>(0);
  const [mznFileContent, setMznFileContent] = useState<string>("");
  const [mznFileName, setMznFileName] = useState<string>("");
  const [dataFileContent, setDataFileContent] = useState<string>("");
  const [dataFileName, setDataFileName] = useState<string>("");
  const [runningMznJobs, setRunningMznJobs] = useState<MznSolverData[]>([]);
  const [optGoalList] = useState<(string | null)[]>(["satisfy", "maximize", "minimize"]);
  const [optVal, setOptVal] = useState<string>("");
  const [bestResult, setBestResult] = useState<MznJobResult | null>(null);
  const [lastOptGoal, setLastOptGoal] = useState<string | null>();
  const [optGoal, setOptGoal] = useState<string | null>();
  const [folderMapping, setFolderMapping] = useState<{ [key: string]: { mzn: { file: File, content: string } | null, dzn: { file: File, content: string } | null, json: { file: File, content: string } | null} }>({});
  const [oneProb, setprob] = useState<boolean>(true);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [backupSolver, setBackupSolver] = useState<MznSolverData | null>(null);

  useEffect(() => {
    fetchDataGet();
  }, []);

  useEffect(() => {
    console.log("Selected solvers:", selectedMznSolvers);
  }, [selectedMznSolvers]);

  useEffect(() => {
    console.log("Running solvers:", runningMznJobs);
  }, [runningMznJobs]);

  const clearFiles = () => {
    setDataFileContent("");
    setMznFileContent("");
    if (dataFileInput.current) (dataFileInput.current as HTMLInputElement).value = "";
    if (mznFileInput.current) (mznFileInput.current as HTMLInputElement).value = "";
  };

  const fetchStopJob = async (item: MznSolverData) => {
    setRunningMznJobs((prevItems: Array<MznSolverData>) =>
      prevItems.filter((i) => i.name !== item.name)
    );

    const solverId = item.jobIdentifier;
    console.log("Solver ID: ", solverId)
    try {
      const response = await fetch(`/api/jobs/mzn/${solverId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Error stopping solvers: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Error stopping solvers:", error);
    }
  };

  const fetchDataGet = async () => {
    try {
      const response = await fetch("/api/solvers/mzn", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      const updatedData = data.map((item: MznSolverData) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
        cpu: 0,
        memory: 0,
      }));
      setMznSolverList(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleItemClick = (item: MznSolverData) => {
    setBackupSolver(item);
    if (selectedMznSolvers.find((i: any) => i.name === item.name)) {
      setSelectedMznSolvers((prevItems: Array<MznSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedMznSolvers((prevItems: Array<MznSolverData>) => [
        ...prevItems,
        item,
      ]);
    }
  };

  const handleStartSolvers = () => {
    setLastOptGoal(optGoal);
    setOptGoal("")
    setBestResult(null);
    setRunningMznJobs(selectedMznSolvers);
    selectedMznSolvers.forEach(fetchStartSolvers);
    setSelectedMznSolvers([]);
    setMznSolverList((prevList) =>
      prevList.map((item) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }))
    );
  };

  const updateItemCpu = (item: MznSolverData, cpu: number) => {
    setMznSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, cpu } : prevItem
      )
    );
    console.log(item.cpu)
  }

  const updateItemMemory = (item: MznSolverData, memory: number) => {
    setMznSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, memory } : prevItem
      )
    );
    console.log(item.memory);
  }

  const updateItemParams = (event: React.ChangeEvent<HTMLInputElement>, item: MznSolverData) => {
      const file = event.target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          const fileContent = reader.result as string;
          setMznSolverList((prevList) =>
            prevList.map((prevItem) =>
              prevItem.name === item.name ? { ...prevItem, params: fileContent } : prevItem
            )
          );
        };
        reader.readAsText(file);
      }
      console.log(item.params);
  }

  const fetchStartSolvers = async (item: MznSolverData) => {
    console.log("ITEM: ", item)
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item,
          mznFileContent,
          mznFileName,
          dataFileContent,
          dataFileName,
          dataFileType: dznOrJson,
          instructions: "StartMznJob",
          optVal: optVal,
          optGoal: optGoal
        }),
      });
      if (!response.ok) {
        console.error(response.statusText);
        // Remove the item from runningMznSolvers list
        setRunningMznJobs((prevItems: Array<MznSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
        );
        return;
      }
      const data = await response.json() as any;
      
      // Remove the item from runningMznSolvers list
      setRunningMznJobs((prevItems: Array<MznSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
      if (data.status == "OPTIMAL_SOLUTION" || (data.status == "SATISFIED" && lastOptGoal === "satisfy")) {
        stopAllSolvers();
      }

    } catch (error) {
      console.error("Error starting solvers:", error);
    }
  }

  const fetchStartSolverWithContent = (item: MznSolverData, mznString: string, dataString: string, suffix: string, mznName: string, dataName: string) => {
    console.log("ITEM: ", item)
    console.log("MZN: ", mznString)
    console.log("DATA: ", dataString)
    console.log("SUFFIX: ", suffix)
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
      mznFileContent : mznString,
      mznFileName: mznName,
      dataFileContent: dataString,
      dataFileName: dataName,
      dataFileType: suffix,
      instructions: "StartMznJob",
      optVal: optVal,
      optGoal: optGoal,
      noresult: true
      }),
    }).catch(error => {
      console.error("Error starting solvers:", error);
    });
  }


  const handleMznFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setMznFileName(file.name);
      const reader = new FileReader();
      reader.onload = () => {
        const fileContent = reader.result as string;
        setMznFileContent(fileContent);
      };
      reader.readAsText(file);
    }
  };


  const handleDataFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setDataFileName(file.name);
      if(file.name.endsWith(".json")){
        setDznOrJson(".json");
      }
      else{
        setDznOrJson(".dzn");
      }
      const reader = new FileReader();
      reader.onload = () => {
      setDataFileContent(reader.result as string);
      };
      reader.readAsText(file);
    }

  };

  const downloadResult = () => {
    if (!bestResult) return;
  
    const content = `Solver Information
Name: ${bestResult.name}
Output
Status: ${bestResult.status}
Goal: ${lastOptGoal}
Execution Time: ${bestResult.executionTime} milliseconds
Result: 
${bestResult.result}
    `;
  
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    saveAs(blob, 'result.txt');
  };


  const stopAllSolvers = async () => {
    setRunningMznJobs([]);
    try {
      const response = await fetch("/api/jobs/mzn", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) {
        console.error("Error stopping all solvers:", response.statusText);
      }
    } catch (error) {
      console.error("Error stopping all solvers:", error);
    }
  };


  async function startSunny(): Promise<any> {
    console.log("Starting SUNNY");
    console.log("k: ", k);
    console.log("T: ", t);
    console.log("solvers:", selectedMznSolvers);
    const response = await fetch("/api/sunny", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        k,
        T: t,
        solvers: selectedMznSolvers,
        backupSolver,
        fileContent: mznFileContent,
        dataContent: dataFileContent,
        dataFileType: dznOrJson,
        solverType: "mzn",
      }),
    });
    if (!response.ok) {
      console.error("Error starting SUNNY:", response.statusText);
    }
    console.log("SUNNY started");
    setSelectedMznSolvers([]);
    let responeAsJson = await response.json();
    console.log(responeAsJson);
    setSchedule(responeAsJson);
  }

  const handleFolderChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileMapping: { [key: string]: {
        mzn: { file: File, content: string } | null, dzn: { file: File, content: string } | null, json: { file: any; content: string; } | null 
} } = {};
  
      for (let i = 0; i < e.target.files.length; i++) {
        const file = e.target.files[i] as any;
        const pathParts = file.webkitRelativePath.split('/');
        const folder = pathParts[pathParts.length - 2]; // Get the parent folder name
  
        if (!fileMapping[folder]) {
          fileMapping[folder] = { mzn: null, dzn: null , json: null};
        }
  
        const fileContent = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = event => resolve(event.target?.result as string);
          reader.onerror = error => reject(error);
          reader.readAsText(file);
        });
  
        if (file.name.endsWith('.mzn')) {
          fileMapping[folder].mzn = { file, content: fileContent };
        } else if (file.name.endsWith('.dzn')) {
          fileMapping[folder].dzn = { file, content: fileContent };
        } else if (file.name.endsWith('.json')) {
          fileMapping[folder].json = { file, content: fileContent };
        }
      }

      setFolderMapping(fileMapping);
    }
  }

  const startSolverWithAllFiles = async () => {
    setLastOptGoal(optGoal);
    setOptGoal(""); 
    for (const solver of selectedMznSolvers) {
      for (const folder in folderMapping) {
        const { mzn, dzn, json } = folderMapping[folder];
        if ((mzn && dzn)) {
          fetchStartSolverWithContent(solver, mzn.content, dzn.content, '.dzn', mzn.file.name, dzn.file.name);
        }
        else if (mzn && json) {
          fetchStartSolverWithContent(solver, mzn.content, json.content, '.json', mzn.file.name, json.file.name);
        }
        else if(mzn) {
          fetchStartSolverWithContent(solver, mzn.content, "", "", mzn.file.name, "");
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
          type: "mzn",
          optGoal: lastOptGoal,
          optVal
        }),
      });
      if (!response.ok) {
        console.error("Error fetching results:", response.statusText);
        return;
      }
      const data = await response.json() as MznJobResult;
      console.log("DATA", data);
      if (data != null){
        setBestResult(data);
        setOptVal(data.optValue.toString());
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
            <h3>Upload MZN file</h3>
            <input ref={mznFileInput} onChange={handleMznFileChange} type="file" />
          </div>
          <br></br>
          <div>
            <h3>Upload Data file</h3>
            <input ref={dataFileInput} onChange={handleDataFileChange} type="file" />
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
                      {solver}: {Math.floor(time)} milliseconds
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
        {mznSolverList.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedMznSolvers.find((i) => i.name === item.name) ? "selected" : ""
            }`}
          >
            <div>Name: {item.name}</div>
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
        Choose Goal
        <br />
        <select
          value={optGoal ?? ""}
          onChange={(e) => {setOptGoal(e.target.value)}}
        >
        <option value=""></option>
        {optGoalList.map((value, index) => (
          <option key={index} value={value ?? ""}>{value}</option>
        ))}
      </select>
        </div>
      {oneProb ? (
        <div>

        <button  onClick={handleStartSolvers} disabled={!optGoal}>Start Solvers</button>  
        </div>
      ) : (
        <div>
          <button onClick={startSolverWithAllFiles} disabled={!optGoal}>Start Solvers</button>
        </div>
      )}
    </div>
      <br />
      
      {oneProb && 
      <div>
          <h2>Running Solvers</h2>
          <div className="grid">
            {runningMznJobs.map((item, index) => (
              <div key={index} className="solver-item">
                <div>Name: {item.name}</div>
                <button className="small-button" onClick={() => fetchStopJob(item)}>Stop Solver</button>
              </div>
            ))}
          </div>
      </div>
      }     
        <button className="small-button" onClick={stopAllSolvers}>Stop All Solvers</button>
        <div>
        <br />
        <h2>Result</h2>
        <div>    
          {bestResult && (
            <div className="result-container">
              <h4>Solver Information</h4>
              <div>Name: {bestResult.name}</div>
              <h4>Output</h4>
              <div>Status: {bestResult.status}</div>
              <div>Goal: {lastOptGoal}</div>
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

export default Mzn;




