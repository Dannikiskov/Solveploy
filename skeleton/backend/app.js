import express from "express";
import cors from "cors";

const app = express();

app.use(
  cors({
    origin: ["http://127.0.0.1:3000"],
  })
);

app.get("/api/todos", (req, res) => {
  // Get the todos from the database.
  const todos = [
    { id: 1, text: "Do the dishes" },
    { id: 2, text: "Take out the trash" },
    { id: 3, text: "Clean the house" },
  ];

  // Wrap the todos array in a JSON object.
  const response = { todos };

  // Send the response back to the frontend.
  res.json(response);
});

app.listen(3001);
console.log("Listening on port 3001");
