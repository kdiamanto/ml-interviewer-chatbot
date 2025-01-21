# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json
import os
import logging
from datetime import datetime
from difflib import get_close_matches

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionProvideJobDetails(Action):
    def name(self) -> Text:
        return "action_provide_job_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        name = tracker.get_slot("name")
        interview_progress = tracker.get_slot("interview_progress") or "introduction"
        
        # Avoid repeating if already provided
        if tracker.get_slot("job_details_provided"):
            return []

        job_details = {
            "title": "Junior Machine Learning Engineer (NLP)",
            "company": "ITML",
            "location": "Athens, Greece",
            "requirements": [
                "BSc/MSc in Computer Science, Data Science or related field",
                "Strong programming skills in Python",
                "Experience with ML frameworks (PyTorch, TensorFlow)",
                "Knowledge of NLP techniques and deep learning",
                "Good understanding of NLP algorithms and architectures",
                "Experience with version control systems (e.g., Git)",
                "Good communication skills in English"
            ],
            "responsibilities": [
                "Develop and implement NLP solutions",
                "Work on EU research projects",
                "Build and optimize ML models",
                "Process and analyze textual data",
                "Collaborate with research teams",
                "Create technical documentation"
            ]
        }

        message = (f"Let me tell you about the {job_details['title']} position at {job_details['company']}.\n\n"
                  f"Key Responsibilities:\n")
        
        for resp in job_details['responsibilities']:
            message += f"• {resp}\n"
            
        message += f"\nRequired Skills & Qualifications:\n"
        for req in job_details['requirements']:
            message += f"• {req}\n"

        dispatcher.utter_message(text=message)

        if interview_progress == "introduction":
            next_message = f"Now, {name if name else ''}, could you tell me about your education? Which university did you attend?"
            dispatcher.utter_message(text=next_message)
            return [
                SlotSet("job_details_provided", True),
                SlotSet("interview_progress", "education")
            ]
        
        return [SlotSet("job_details_provided", True)]

class ActionAnalyzeEducationBackground(Action):
    def name(self) -> Text:
        return "action_analyze_education_background"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            name = tracker.get_slot("name")
            university_name = tracker.get_slot("university_name")
            study_program = tracker.get_slot("study_program")

            if not university_name:
                message = "Could you please specify which university you attended?"
                dispatcher.utter_message(text=message)
                return []

            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)
            json_path = os.path.join(project_dir, "data", "databases", "university-courses-complete.json")

            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    university_data = json.load(file)
            except FileNotFoundError:
                logger.error(f"University database not found at {json_path}")
                message = (
                    f"Thank you for sharing that{' ' + name if name else ''}. "
                    "Could you tell me about your experience with NLP and ML projects?"
                )
                dispatcher.utter_message(text=message)
                return [
                    SlotSet("education_analyzed", True),
                    SlotSet("interview_progress", "experience")
                ]

            all_universities = []
            for country in university_data["universities"]:
                for institution in country["institutions"]:
                    all_universities.append((institution["name"], country["country"], institution))

            university_names = [u[0] for u in all_universities]
            matches = get_close_matches(university_name, university_names, n=1, cutoff=0.6)

            if matches:
                found_university = next(u for u in all_universities if u[0] == matches[0])
                university_info = found_university[2]
                country = found_university[1]

                relevant_courses = {"NLP": [], "ML": [], "Programming": []}
                programming_langs = set()

                for course in university_info["courseList"]:
                    course_name = course["name"].lower()
                    course_type = course["type"]
                    
                    if "nlp" in course_name or course_type == "NLP":
                        relevant_courses["NLP"].append(course["name"])
                    elif "machine learning" in course_name or "deep learning" in course_name:
                        relevant_courses["ML"].append(course["name"])
                    elif course_type == "Programming":
                        relevant_courses["Programming"].append(course["name"])
                    
                    if course.get("languages"):
                        programming_langs.update(course["languages"])

                message = f"I see you studied at {university_info['name']} in {country}. "
                
                if study_program:
                    message += f"Your focus on {study_program} is particularly relevant for this position. "

                if any(courses for courses in relevant_courses.values()):
                    message += "\n\nI notice your university offers relevant courses:"
                    for category, courses in relevant_courses.items():
                        if courses:
                            message += f"\n\n{category} courses:"
                            for course in courses[:2]:
                                message += f"\n• {course}"

                if programming_langs:
                    message += f"\n\nThe curriculum includes experience with: {', '.join(programming_langs)}"

            else:
                # Enhanced fallback for unrecognized university
                message = (
                    f"While I don't have detailed information about your university in my database, "
                    f"I'm very interested in hearing about your studies{' ' + name if name else ''}. "
                    f"Could you tell me about any specific ML or NLP courses you took?"
                )

            message += "\n\nCould you share your practical experience with ML and NLP technologies?"
            dispatcher.utter_message(text=message)
            return [
                SlotSet("education_analyzed", True),
                SlotSet("interview_progress", "experience")
            ]

        except Exception as e:
            logger.error(f"Error in education analysis: {str(e)}")
            message = f"Thank you for sharing that{' ' + name if name else ''}. Could you tell me about your experience with NLP and ML projects?"
            dispatcher.utter_message(text=message)
            return [
                SlotSet("education_analyzed", True),
                SlotSet("interview_progress", "experience")
            ]
class ActionValidateTechnicalResponse(Action):
    def name(self) -> Text:
        return "action_validate_technical_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # If we're already in advanced stages, don't validate
        if tracker.get_slot("interview_progress") in ["logistics", "future_goals"]:
            return []

        name = tracker.get_slot("name")
        last_message = tracker.latest_message.get("text", "").lower()

        # If already validated, move to future goals
        if tracker.get_slot("technical_validated"):
            message = f"Excellent {name}! Let's talk about your career goals. Where do you see yourself professionally in 5 years?"
            dispatcher.utter_message(text=message)
            return [
                SlotSet("interview_progress", "future_goals")
            ]

        technical_keywords = {
            "transformers": ["transformer", "bert", "gpt", "attention"],
            "ml_concepts": ["machine learning", "deep learning", "neural network", "lstm", "rnn", "sequence"],
            "nlp_tasks": ["classification", "sentiment analysis", "text processing", "nlp"],
            "frameworks": ["pytorch", "tensorflow", "keras"],
            "methodology": ["preprocessing", "pipeline", "model", "training"]
        }

        matched_categories = set()
        for category, keywords in technical_keywords.items():
            for keyword in keywords:
                if keyword in last_message:
                    matched_categories.add(category)

        # If we have enough technical depth in the response
        if len(matched_categories) >= 2:
            message = f"Excellent {name}! Your technical knowledge is impressive. Let's talk about your future goals. Where do you see yourself professionally in 5 years?"
            dispatcher.utter_message(text=message)
            return [
                SlotSet("technical_validated", True),
                SlotSet("interview_progress", "future_goals")
            ]
        else:
            # If response lacks technical depth, ask for more specific details
            message = f"Could you provide more specific technical examples{' ' + name if name else ''}? For instance, what ML frameworks or specific techniques have you used?"
            dispatcher.utter_message(text=message)
            return []

class ActionSaveCandidateInfo(Action):
    def name(self) -> Text:
        return "action_save_candidate_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get current directory and create candidates folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)
            candidates_dir = os.path.join(project_dir, "candidates")
            os.makedirs(candidates_dir, exist_ok=True)

            candidate_info = {
                "name": tracker.get_slot("name"),
                "university": tracker.get_slot("university_name"),
                "study_program": tracker.get_slot("study_program"),
                "experience_years": tracker.get_slot("experience_years"),
                "start_date": tracker.get_slot("start_date"),
                "future_role": tracker.get_slot("future_role"),
                "technical_validated": tracker.get_slot("technical_validated"),
                "interview_progress": tracker.get_slot("interview_progress"),
                "timestamp": datetime.now().isoformat()
            }

            if candidate_info["name"]:
                filename = f"candidate_{candidate_info['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(candidates_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(candidate_info, f, indent=2, ensure_ascii=False)

            name = tracker.get_slot("name")
            message = (
                f"Thank you for your time today{' ' + name if name else ''}. "
                "Our team will review your profile and contact you soon about next steps."
            )
            dispatcher.utter_message(text=message)
            
            return [SlotSet("interview_progress", "closing")]

        except Exception as e:
            logger.error(f"Error saving candidate info: {str(e)}")
            name = tracker.get_slot("name")
            message = (
                f"Thank you for your time today{' ' + name if name else ''}. "
                "We'll be in touch about next steps."
            )
            dispatcher.utter_message(text=message)
            return [SlotSet("interview_progress", "closing")]
