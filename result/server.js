const express = require("express");
const { Pool } = require("pg");
const app = express();
const port = process.env.PORT || 3000;

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

app.get("/health", (_, res)=>res.json({ok:true}));

app.get("/rounds/:id/results", async (req,res)=>{
  const { id } = req.params;
  const sql = `
    SELECT o.id AS option_id, o.label, COUNT(v.id)::int AS votes
    FROM options o LEFT JOIN votes v ON v.option_id=o.id
    WHERE o.round_id=$1
    GROUP BY o.id,o.label
    ORDER BY votes DESC`;
  const { rows } = await pool.query(sql, [id]);
  res.json(rows);
});

app.listen(port, ()=>console.log("result listening", port));