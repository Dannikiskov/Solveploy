import { useState as use_state } from "react";
import { useEffect as use_effect } from "react";
import { v4 as uuidv4 } from "uuid";

import "./App.css";

interface Solver_Data {
  name: string;
  mzn_identifier: string;
  solver_identifier: string;
}

interface Solver_Result extends Solver_Data {
  result: string;
  execution_time: number;
}

function App() {
  const [list, set_list] = use_state<Solver_Data[]>([]);
  const [selected_items, set_selected_items] = use_state<Solver_Data[]>([]);
  const [mzn_file_content, set_mzn_file_content] = use_state<string>("");
  const [running_solvers, set_running_solvers] = use_state<Solver_Data[]>([]);
  const [solver_results_list, set_solver_results_list] = use_state<
    Solver_Result[]
  >([]);

  use_effect(() => {
    fetch_data_get();
  }, []);

  use_effect(() => {
    console.log("solver_results_list");
    console.log(solver_results_list);
  }, [solver_results_list]);

  use_effect(() => {
    console.log("running_solvers");
    console.log(running_solvers);
  }, [running_solvers]);

  const fetch_stop_solver = async (item: Solver_Data) => {
    set_running_solvers((prevItems) =>
      prevItems.filter((i) => i.name !== item.name)
    );

    try {
      const response = await fetch("/api/stopsolver", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ item }),
      });

      if (!response.ok) {
        throw new Error(`Error stopping solvers: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Error stopping solvers:", error);
    }
  };

  const fetch_data_get = async () => {
    try {
      const response = await fetch("/api/solvers", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      const updatedData = data.map((item: Solver_Data) => ({
        ...item,
        solver_identifier: uuidv4(),
      }));
      set_list(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handle_item_click = (item: Solver_Data) => {
    if (selected_items.find((i) => i.name === item.name)) {
      set_selected_items((prevItems) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      set_selected_items((prevItems) => [...prevItems, item]);
    }
  };

  const handle_start_solvers = () => {
    set_running_solvers(selected_items);
    selected_items.forEach(fetch_start_solvers);
  };

  const fetch_start_solvers = async (item: Solver_Data) => {
    try {
      const response = await fetch("/api/startsolver", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ item, mzn_file_content }),
      });

      let updated_item = await response.json();
      if (!response.ok) {
        updated_item = {
          ...item,
          result: "Error starting solver",
          execution_time: 0,
          stopped: true,
        };
        throw new Error(`Error starting solvers: ${response.statusText}`);
      }
      if (updated_item !== "Solver stopped") {
        set_solver_results_list((prevItems: Solver_Result[]) => [
          ...prevItems,
          {
            name: item.name,
            solver_identifier: item.solver_identifier,
            result: updated_item.result,
            execution_time: updated_item.execution_time,
            mzn_identifier: item.mzn_identifier,
          },
        ]);
      }

      // Update state here
      set_running_solvers((prevItems) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } catch (error) {
      console.error("Error starting solvers:", error);
      return {
        ...item,
        result: "Error starting solver",
        execution_time: 0,
        stopped: true,
      };
    }
  };

  const handle_file_change = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        set_mzn_file_content(reader.result as string);
      };
      reader.readAsText(file);
    }
  };

  return (
    <>
      <h1>Solveploy</h1>
      <div>
        <input onChange={handle_file_change} type="file" />
      </div>
      <br />
      <h2>Available Solvers</h2>
      <div className="grid">
        {list.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selected_items.includes(item) ? "selected" : ""
            }`}
            onClick={() => handle_item_click(item)}
          >
            <div>Name: {item.name}</div>
            <div>MZN ID: {item.mzn_identifier}</div>
            <div>Solver ID: {item.solver_identifier}</div>
          </div>
        ))}
      </div>
      <br />
      <button onClick={handle_start_solvers}>Start Solvers</button>
      <br />
      <div>
        <h2>Solver Results</h2>
        <div className="grid">
          {running_solvers.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Solver ID: {item.solver_identifier}</div>
              <div>Waiting for result</div>
              <button onClick={() => fetch_stop_solver(item)}>
                Stop Solver
              </button>
            </div>
          ))}
          {solver_results_list.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Solver ID: {item.solver_identifier}</div>
              <div>Result: {item.result}</div>
              <div>Execution Time: {item.execution_time}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default App;
