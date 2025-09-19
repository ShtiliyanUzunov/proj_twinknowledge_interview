<h1>Twinknowledge interview task submission</h1>

Contains code for basic implementation for the game of <b>Jeopardy.</b>


    <b>To run locally - copy the .env_example file to .env, and fill all required fields.</b>

    0. Run the ingestion script. It's a one time script that downloads the dataset, filters it, creates a Postgres database, and table, and stores  it inside it. To run the ingestion set your PYTHONPATh to the root of the project
        $env:PYTHONPATH = "C:\<your_path_here>\proj_twinknowledge_interview"
        execute the ingestion command: python .\operations\ingestion.py

    1. To setup the UI go to the ui folder and run "npm install", then run "npm run dev"
    2. To setup the Server - go to the root folder, install the requirements.txt file. 
        Set the PYTHONPATH to the root of the project:
        $env:PYTHONPATH = "C:\<your_path_here>\proj_twinknowledge_interview"
        execute the server start command: python .\web\server.py