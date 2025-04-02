# AI-Powered Academic Research Paper Recommendation System

## Overview
This project is an AI-powered recommendation system designed to help researchers, students, and academics discover relevant research papers based on their interests and reading history. The system utilizes machine learning algorithms to analyze user behavior, research topics, and citation patterns to provide accurate, personalized recommendations.

## Features
- **Personalized Recommendations:** Suggests research papers tailored to user preferences and past interactions.
- **Advanced Filtering:** Filter results by publication year, author, or research domain.
- **Data-Driven Insights:** Provides recommendations based on citation analysis and topic modeling.
- **External Integrations:** Connects with major research databases (planned feature).

## Technologies Used
- Python 3.11 (or older)
- Machine Learning Libraries: Scikit-learn
- Natural Language Processing (NLP): spaCy
- Database: PostgreSQL 
- Frontend: JavaFX (for GUI, if applicable)

## Setup Instructions (For Programmers to edit)
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ReeceFuxan/AI-System-Project.git

2. ```bash
   cd AI-System-Project
	or
   cd C:/path/path/AI-System-Project

!! Committing Changes
git status
git add .
git commit -m "Message"
git push origin main

3. Run ElasticSearch (depends on install) NEW BASH WINDOW
   Reece - I created its own folder in my C: drive
   ```bash
   cd C:/elasticsearch/bin
   cmd elasticsearch.bat

   !! Check if running using browser
   http://localhost:9200

4. Run Uvicorn for FastAPI NEW BASH WINDOW
   ```bash
   cd C:/AI-System-Project
   source env/Scripts/Activate
   python -m uvicorn backend.main_fastapi:app --reload
