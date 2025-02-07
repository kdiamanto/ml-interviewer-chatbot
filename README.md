# Junior ML Engineer at ITML - Interview Chatbot

## Domain and Motivation
This chatbot is designed to conduct initial screening interviews for a Junior ML Engineer position at ITML. The choice of an ML interviewer chatbot is particularly fitting as it:
- Demonstrates practical application of NLP in a real-world scenario
- Provides consistent interview experiences
- Can effectively assess technical knowledge through keyword analysis
- Showcases the intersection of conversational AI and technical recruitment

## Implemented Scenarios
The chatbot implements three main interview scenarios:

1. **Initial Screening and Background Assessment**
   - Gathers candidate information
   - Analyzes educational background using university database
   - Validates academic qualifications against job requirements

2. **Technical Knowledge Validation**
   - Assesses ML/NLP expertise through targeted questions
   - Validates responses using keyword analysis
   - Adapts questioning based on candidate responses

3. **Career Goals and Logistics Discussion**
   - Explores candidate's career aspirations
   - Discusses practical aspects (start date, location)
   - Handles job-specific inquiries

## Data Source Integration

### 1. University Course Database
- **Purpose**: Validates and analyzes candidates' educational background
- **Implementation**: JSON database containing university programs and relevant courses from top institutions worldwide
- **Rationale**: Enables contextual discussion of candidate's academic background
- **Features**: 
  - Comprehensive course listings
  - Programming language requirements
  - Course categorization (NLP, ML, Programming)
  - Educational level classification

### 2. Technical Knowledge Validator
- **Purpose**: Assesses technical responses using keyword analysis
- **Implementation**: Categorized keyword dictionary for ML/NLP concepts including:
  - Transformers: transformer, bert, gpt, attention
  - ML Concepts: machine learning, deep learning, neural network, lstm, rnn, sequence
  - NLP Tasks: classification, sentiment analysis, text processing
  - Frameworks: pytorch, tensorflow, keras
  - Methodology: preprocessing, pipeline, model, training
- **Rationale**: Provides objective validation of technical knowledge
- **Features**:
  - Multi-category matching system
  - Adaptive response validation
  - Progressive difficulty adjustment

## University Database Enrichment
The project includes a dedicated utility for enriching the university course database:

Location: utils/university_data_collector.py
Purpose: Facilitates adding new universities and courses to the database
Features:

Support for both local and Google Colab environments
Automated data validation
Database statistics tracking
Backup functionality
Google Drive integration for Colab

Using the Data Collector

## 1. Local Usage
from utils.university_data_collector import UniversityDataCollector

# Initialize collector
collector = UniversityDataCollector('data/databases/university-courses-complete.json')

# Add new institution
new_courses = [
    {
        'name': 'Advanced Machine Learning',
        'level': 'Graduate',
        'languages': ['Python', 'PyTorch'],
        'type': 'NLP'
    }
]

collector.add_institution(
    country='Greece',
    institution_name='Athens University of Economics and Business',
    courses=new_courses
)
## 2. Google Colab Usage
collector = UniversityDataCollector('path/to/database.json', use_colab=True)

## Implementation Challenges and Solutions

1. **Challenge**: Managing Conversation Flow
   - **Solution**: Implemented slot tracking for interview progress
   - **Impact**: Ensures natural progression through interview stages

2. **Challenge**: Technical Response Validation
   - **Solution**: Developed multi-category keyword matching system
   - **Impact**: More accurate assessment of technical knowledge

3. **Challenge**: University Recognition
   - **Solution**: Implemented fuzzy matching for university names
   - **Impact**: Better handling of educational background validation

## Setup Instructions

1. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Training the Model**
```bash
# Train the model
rasa train

# Test the model in shell
rasa shell
```

3. **Running the Chatbot**
```bash
# Start the Rasa server
rasa run --enable-api

# In a new terminal, start the action server
rasa run actions

4. **Required Files**
- Ensure `data/databases/university-courses-complete.json` is present
- Create a `candidates` directory for storing interview records

## Example Interview

Here's a sample interview conversation demonstrating the chatbot's capabilities:

```
Bot: Hello! I'm conducting interviews for ITML's Junior ML Engineer position. Before we begin, could you tell me your name?

Human: I'm Kostas

Bot: Nice to meet you, Kostas! I'm excited to learn more about your background. How are you feeling today?

Human: I'm good

Bot: That's wonderful to hear, Kostas! Let's talk about your interest in the ML Engineer position.

[Job details provided...]

Now, Kostas, could you tell me about your education? Which university did you attend?

Human: I studied at MIT.

Bot: I see you studied at MIT in USA.

I notice your university offers relevant courses:

NLP courses:

• Natural Language Processing

• Advanced Natural Language Processing

The curriculum includes experience with: Python

Could you share your practical experience with ML and NLP technologies?

Human: I've worked extensively on speech recognition systems using deep learning. I've implemented attention mechanisms and transformer architectures for speech-to-text applications.

example case 1:

Bot: Your experience in this area is very relevant to what we do, Kostas.

Your background is interesting, Kostas. Let me ask you a technical question now:

How would you approach a text classification problem from start to finish?

Human: In my approach, I'd start with preprocessing and building a data pipeline. For the model architecture, I'd use deep learning methods with transformers or LSTM networks. I'd implement this using PyTorch, focusing on sequence processing and classification techniques.

example case 2:

Bot: Your approach aligns well with how we work at ITML, Kostas.

Thank you for sharing your experience, Kostas. Let's move on to some technical questions now:

Could you explain your understanding of word embeddings and their importance in NLP?

Human: Word embeddings are fundamental in deep learning approaches to NLP, transforming text into vector representations. I've used frameworks like PyTorch to implement transformer models like BERT, which use contextual embeddings for text processing and classification tasks.

Bot: Excellent Kostas! Your technical knowledge is impressive. Let's talk about your future goals. Where do you see yourself professionally in 5 years?

Human: I aim to become a Senior ML Engineer, focusing on developing innovative NLP solutions.

Bot: Your career goals align well with ITML's growth trajectory, particularly in Senior ML Engineer. When would you be available to start if selected for the position, Kostas?

Human: I could start in two weeks.

Bot: Our office is located in Athens, Greece. Is this location suitable for you?

Human: Yes, that works perfectly.

Bot: We've covered a lot of ground, Kostas. Is there anything else you'd like to know about the position?

Human: No, thank you for your time.

Bot: Thank you for your time today Kostas. Our team will review your profile and contact you soon about next steps.

```

## Dialog Policy Experimentation

### Changes Made
1. Modified response validation threshold
   - Reduced from 3 to 2 matching categories
   - Added specific technical follow-up prompts

2. Implemented progressive technical validation
   - Allows multiple attempts before progression
   - Provides specific guidance for insufficient responses

### Rationale for Changes
- More natural conversation flow
- Better handling of varied response styles
- Improved candidate experience

### Observed Results
- More fluid technical discussions
- Reduced repetition in questions
- Better progression through interview stages

## Future Improvements
- Integration with job posting APIs
- Enhanced sentiment analysis for candidate responses
- More sophisticated technical response validation
- Integration with calendar systems for scheduling

## Presentation
The detailed presentation of this project can be found in the present repository as a pdf file - Rasa_Chatbot_Interviewer_Presentation_Diamantopoulos.pdf.

## Repository Structure
```
├── actions/

│   └── actions.py

├── data/

│   ├── nlu.yml

│   ├── rules.yml

│   ├── stories.yml

│   └── databases/

│       └── university-courses-complete.json

├── utils/

│   └── university_data_collector.py

├── presentations/

│   └── ml_interviewer_chatbot.pdf

├── domain.yml

├── config.yml

├── credentials.yml

├── endpoints.yml

├── models

├── tests

├── results

├── candidates

├── venv

└── README.md

```
