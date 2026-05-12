HIV Antigen Prediction Tool

General: A full-stack application that uses coverage, evolutionary continuity, and conservation to predict a mRNA sequence that encodes for a universal antigen, to be used for vaccine development.

**GitHub Repository:** https://github.com/siffna/hiv-prediction-antigen

Features:

- NCBI: Implementing NCBI API to fetch and analyze multiple sequences of HIV strains
- Evolution Continuity: Analyzing antigen sections that is conserved throughout evolution.
- Conservation: Recognizing regions of sequence that is most resistant to mutation
-Confidence Scoring: Method of measuring and gauging success of predicted mRNA
-Charting: Visualizing the criteria's used in confidence scoring 
-mRNA: Generating a predicted mRNA sequence that is optimized.
-SQLite: Predictions are stored in SQLite database
-UI: Clean React frontend

Start:
     -Needed: Python , Node.js, npm 11+

Usage: 
1.) Open app in browser
2.) Paste any HIV sequence (>= 20 amino acids)
3.) Click, "Predict Universal Antigen"
4.) View results: Predicted antigen, mRNA sequence, coverage metrics, confidence score, mutation resistance

Test sequence: 
MGARASLRGGKLDAWERIRLRPGGRKKYRLKHIVWASRELERFAVNPGLLETSEGCRQILGQLQPALQTGSEELRSLFNTIAVLYCVHQRIEIKDTKEALDKIEEEQNKSKKKAQQAAADTGNSS

Architecture:
A.) Frontend (React):
App.jsx: Main orchestrator component
components/SequenceInput.jsx: Input form for HIV sequences
components/AntigenResults.jsx: Displays predicted antigen
components/AntigenMetrics.jsx: Charts and metrics visualization
App.css: Responsive styling

B.) Backend (Flask and Python)
app.py: (Flask server with prediction pipeline)
Database: SQLite (predictions.db)

C.) External APIs
NCBI Entrez: Fetches HIV protein sequences from NCBI database

How it works:
1.) Fetches and downloads relate HIV sequence based on pasted sequence- then downloading 50 HIV sequences
2.)Calculates evolutionary distances
3.) Conservation: Identifies stable amino acid positions
4.) Prediction of Antigen: Slides 20 amino acids, and scores on conservation, coverage, and mutation resistance: 35%,35%, and 30% respectively.
5.) Calculates metrics: (Coverage, confidence, mutation resistance)
6.) mRNA Design: Converts optimized amino sequence to mRNA that can be used to design mRNA vaccines

Inspiration:
I recently had a very aggressive flu- parainfluenza 3, which resulted in my hospitalization. After I got better, I got sick again- sparking y interest in high mutation viruses. The influenza virus I had most likely mutated but it is curable- HIV isn't. It  mutates quickly and attacks T-cells- the very cells meant to fight viruses. I wanted to explore the notion of generating mRNA that encodes for antigens, with a wide range of coverage across strains.

Impact: This could have a big impact in fining therapeutic vaccines for HIV and other diseases. With the advances in AI, we could generate more optimal antigen sequences. 

New technology: Python. Python is ideal for backends, and was recommended to me. Python is simple and has a large library database- including Numpy.

Technical Rationale:
Backend: Flask:
- Clean separation from frontEnd
-Handles heavy computation (NCBI queries, scoring)
-API keys are protected

Frontend: React:
- Dynamic changes upon data changes
-Convenience of React components
-Interactions handled
-Previous experience with React

Both:
-Frontend sends sequence to backend, using the API
-Backend handles complicated heavy lifting
-Frontend visualizes results
-Clean interactions

Technical Tradeoffs:
1.) Speed:
By using live NCBI queries, it the data acquisition is slower
Tradeoff: 6-60 seconds each predictions
Alternative: Download sequences locally

Why I chose this: Locally storing sequences might lead to outdated data being used

2.) Simplistic scoring:
The scoring for the sequences is not very strong. A machine learning/AI algorithm would have been best
Tradeoff: High simplicity, but missing out on potentially high accuracy
AlternativeL ESM2 protein language model or using Google Alphafold technology

Why I chose this: Simplicity and lack of expertise

Most difficult technical bug + overcoming:

I was unable to get the backend to retrieve the data from the NCBI database. An error message- "No sequence found", kept appearing.

Solution: I realized that the newer sections of the code did not update automatically. Also, my demo deployed on local host 5173, rather than the typical 3000.

AI Usage:
I used Claude throughout the entirety of this project, including in generating all the scripts.

Example of nuance added to AI usage:
I wanted a means of measuring the confidence of the antigen sequences. Claude generated the app.py file to deal with all the data analysis and confidence score. a Part of the original code was:
def calculate_confidence_score(antigen_data, coverage_metrics, conservation_map):
[conservation_confidence = antigen_data['conservation'] 
coverage_confidence = min(coverage_metrics['overall_coverage'] * 1.2, 1.0)
epitope_confidence = antigen_data['epitope_potential']

overall_confidence = (conservation_confidence * 0.35+
coverage_confidence * 0.35 +
epitope_confidence * 0.25)


return min(overall_confidence, 1.0)
]
It clearly shows a strong preference for high coverage, multiplying the score by 1.2 (20%). However, I felt that if a sequence was conserved across 50% of strains analyzed, that should have some weight. Therefore I made the following changes:

[def calculate_confidence_score(antigen_data, coverage_metrics, conservation_map):
conservation_inflation = 1
if antigen_data['conservation'] >= 0.5:
conservation_inflation = 1.2


conservation_confidence = min(antigen_data['conservation'] * conservation_inflation, 1)
coverage_confidence = min(coverage_metrics['overall_coverage'] * 1.2, 1.0)
epitope_confidence = antigen_data['epitope_potential']

overall_confidence = (conservation_confidence * 0.35+
coverage_confidence * 0.35 +
epitope_confidence * 0.25)


return min(overall_confidence, 1.0)]

I created a new variable called conservation_inflation, and set its value to 1. Then I made an if else statement: If the coverage is at least 50%, multiply the coverage score by 20%, so it has more weight.
