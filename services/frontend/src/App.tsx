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
  stopped: boolean;
}

function App() {
  const [list, set_list] = use_state<Solver_Data[]>([]);
  const [selected_items, set_selected_items] = use_state<Solver_Data[]>([]);
  const [mzn_file_content, set_mzn_file_content] = use_state<string>("");
  const [solver_results_list, set_solver_results_list] = use_state<
    Solver_Result[]
  >([]);

  use_effect(() => {
    fetch_data_get();
  }, []);

  const fetch_stop_solver = async (item: Solver_Result) => {
    item.stopped = true;
    set_solver_results_list((prevResults) =>
      prevResults.map((result) =>
        result.solver_identifier === item.solver_identifier
          ? { ...result, stopped: true }
          : result
      )
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

  const handle_start_solvers = async () => {
    set_solver_results_list([]);

    try {
      selected_items.forEach(async (item, index) => {
        item.solver_identifier = uuidv4();
        set_solver_results_list((prevResults) => [
          ...prevResults,
          {
            name: item.name,
            result: "",
            execution_time: 0,
            mzn_identifier: item.mzn_identifier,
            solver_identifier: item.solver_identifier,
            stopped: false,
          },
        ]);

        try {
          const response = await fetch("/api/startsolver", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              item,
              mzn_file_content,
            }),
          });

          if (!response.ok) {
            throw new Error(
              `Error starting solver ${item.name}: ${response.statusText}`
            );
          }

          const result_data = await response.json();

          set_solver_results_list((prev_results) => {
            const updated_results = [...prev_results];
            updated_results[index] = {
              name: item.name,
              result: result_data.result,
              execution_time: result_data.execution_time,
              mzn_identifier: item.mzn_identifier,
              solver_identifier: item.solver_identifier,
              stopped: false,
            };
            return updated_results;
          });
        } catch (error) {
          console.error(`Error starting solver ${item.name}:`, error);
        }
      });
    } catch (error) {
      console.error("Error starting solvers:", error);
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
          {solver_results_list.map((item, index) => (
            <div key={index} className="solver-item">
              {item.result === "" && !item.stopped ? (
                <>
                  <div>Name: {item.name}</div>
                  <div>Solver ID: {item.solver_identifier}</div>
                  <div>Waiting for results...</div>
                  <button onClick={() => fetch_stop_solver(item)}>Stop</button>
                </>
              ) : (
                <>
                  <div>Name: {item.name}</div>
                  <div>Solver ID: {item.solver_identifier}</div>
                  {item.stopped ? (
                    <div>Stopped</div>
                  ) : (
                    <>
                      <div>Result: {item.result}</div>
                      <div>Execution Time: {item.execution_time}</div>
                    </>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default App;
