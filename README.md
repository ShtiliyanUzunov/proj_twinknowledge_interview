<h1>Twinknowledge interview task submission</h1>

Contains code for basic implementation for the game of <b>Jeopardy.</b>

<b>Solution steps</b>
    1. Generated the UI structure using React + Typescript by using an existing template:
        "npm create vite@latest . -- --template react-ts --yes"
    2. Wrote an ingestion script that should be run one time to prepare the data. Used LLM to help with the task.

<b>Setup</b>
    0. Run the ingestion script. It's a one time script that downloads the dataset, filters it, creates a Postgres database, and table, and stores  it inside it. To run the ingestion successfully - <b>copy tthe .env_example file to .env, and fill all required fields.</b>

    1. To setup the UI go to the ui folder and run "npm install", then run "npm run dev"