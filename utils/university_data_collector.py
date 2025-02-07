#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
University Data Collector Module
------------------------------

This module provides tools for collecting and managing university course data
for the ML Interviewer Chatbot. It supports both local and Google Colab environments.

Features:
    - Add/update university course data
    - Support for local and Google Colab environments
    - Automatic Google Drive integration
    - Data validation and error handling
    - Database statistics
    - Automatic backups

Example:
    from university_data_collector import UniversityDataCollector
    
    # For local use
    collector = UniversityDataCollector('path/to/database.json')
    
    # For Google Colab
    collector = UniversityDataCollector('path/to/database.json', use_colab=True)

Author: Your Name
Date: February 2025
License: MIT
"""

import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import os
from datetime import datetime

@dataclass
class Course:
    """
    Data class representing a university course.
    
    Attributes:
        name (str): The name of the course
        level (str): Academic level (Undergraduate/Graduate/Both)
        languages (List[str]): Programming languages used in the course
        type (str): Course type (NLP/Programming/etc.)
    """
    name: str
    level: str
    languages: List[str]
    type: str

@dataclass
class Institution:
    """
    Data class representing an educational institution.
    
    Attributes:
        name (str): The name of the institution
        courseList (List[Course]): List of courses offered
    """
    name: str
    courseList: List[Course]

class UniversityDataCollector:
    """
    A class for collecting and managing university course data.
    Supports both local and Google Colab environments.
    
    Attributes:
        database_path (str): Path to the JSON database file
        use_colab (bool): Flag indicating if running in Google Colab
        current_data (Dict): The currently loaded database
    """
    
    def __init__(self, database_path: str, use_colab: bool = False):
        """
        Initialize the data collector.
        
        Args:
            database_path (str): Path to the JSON database file
            use_colab (bool): Set to True if running in Google Colab
            
        Raises:
            ImportError: If use_colab is True but not in Colab environment
        """
        self.database_path = database_path
        self.use_colab = use_colab
        
        # Mount Google Drive if using Colab
        if self.use_colab:
            try:
                from google.colab import drive
                drive.mount('/content/drive')
                print("Google Drive mounted successfully")
            except ImportError:
                print("Not running in Colab environment")
                self.use_colab = False
        
        # Load or create the database
        self.current_data = self.load_current_database()
    
    def load_current_database(self) -> Dict:
        """
        Load the database from file, handling both local and Colab paths.
        Creates a new database if none exists.
        
        Returns:
            Dict: The loaded database or a new empty database
            
        Note:
            In Colab mode, automatically adjusts paths to work with Google Drive
        """
        try:
            if self.use_colab:
                # Adjust path for Google Drive if needed
                if not self.database_path.startswith('/content/drive'):
                    self.database_path = os.path.join('/content/drive/MyDrive', self.database_path)
            
            with open(self.database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Database file not found at {self.database_path}")
            return self._create_new_database()
        except json.JSONDecodeError:
            print("Error decoding JSON. Creating new database...")
            return self._create_new_database()
    
    def _create_new_database(self) -> Dict:
        """
        Create a new database with the basic structure.
        
        Returns:
            Dict: A new empty database with predefined categories
        """
        return {
            "courses": {
                "NLP": [],
                "Programming": [],
                "Language Engineering": [],
                "Data Analysis": [],
                "Data Preprocessing": []
            },
            "universities": []
        }
    
    def save_database(self) -> None:
        """
        Save the database to file, creating backup if primary save fails.
        
        Creates a timestamped backup file if the primary save location
        is not accessible.
        
        Raises:
            OSError: If both primary and backup saves fail
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
            
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=2, ensure_ascii=False)
            print(f"Database saved successfully to {self.database_path}")
        except Exception as e:
            print(f"Error saving database: {str(e)}")
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f'university_database_backup_{timestamp}.json'
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=2, ensure_ascii=False)
            print(f"Backup saved to {backup_path}")

    def validate_course_type(self, course_type: str) -> bool:
        """
        Validate if a course type exists in the database.
        
        Args:
            course_type (str): The course type to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_types = set(self.current_data['courses'].keys())
        return course_type in valid_types

    def add_institution(self, country: str, institution_name: str, 
                       courses: List[Dict]) -> None:
        """
        Add a new institution or update an existing one.
        
        Args:
            country (str): Country name
            institution_name (str): Name of the institution
            courses (List[Dict]): List of course dictionaries
        
        Each course dictionary should have:
            - name: str
            - level: str (Undergraduate/Graduate/Both)
            - languages: List[str]
            - type: str (must match existing course types)
            
        Raises:
            ValueError: If any course type is invalid
        """
        try:
            # Validate course types before adding
            for course in courses:
                if not self.validate_course_type(course['type']):
                    raise ValueError(f"Invalid course type: {course['type']}")
            
            # Format courses into Course objects
            formatted_courses = [
                Course(
                    name=course['name'],
                    level=course['level'],
                    languages=course.get('languages', []),
                    type=course['type']
                ) for course in courses
            ]
            
            # Create institution object
            new_institution = Institution(
                name=institution_name,
                courseList=formatted_courses
            )
            
            # Add to database
            self._update_or_create_institution(country, new_institution)
            
            # Auto-save after successful addition
            self.save_database()
            
        except Exception as e:
            print(f"Error adding institution: {str(e)}")

    def _update_or_create_institution(self, country: str, new_institution: Institution) -> None:
        """
        Update existing institution or create new one.
        
        Args:
            country (str): Country name
            new_institution (Institution): Institution to add/update
            
        Note:
            This is an internal method used by add_institution
        """
        country_exists = False
        for country_data in self.current_data['universities']:
            if country_data['country'] == country:
                country_exists = True
                # Check if institution already exists
                inst_exists = False
                for inst in country_data['institutions']:
                    if inst['name'] == new_institution.name:
                        inst_exists = True
                        inst['courseList'] = [vars(course) for course in new_institution.courseList]
                        print(f"Updated existing institution: {new_institution.name}")
                        break
                if not inst_exists:
                    country_data['institutions'].append({
                        'name': new_institution.name,
                        'courseList': [vars(course) for course in new_institution.courseList]
                    })
                    print(f"Added new institution: {new_institution.name}")
                break
                
        if not country_exists:
            self.current_data['universities'].append({
                'country': country,
                'institutions': [{
                    'name': new_institution.name,
                    'courseList': [vars(course) for course in new_institution.courseList]
                }]
            })
            print(f"Added new country {country} with institution {new_institution.name}")

    def get_database_stats(self) -> Dict:
        """
        Get statistics about the current database.
        
        Returns:
            Dict: Statistics including:
                - total_countries: Number of countries
                - total_institutions: Number of institutions
                - total_courses: Total number of courses
                - courses_by_type: Distribution of courses by type
                - courses_by_level: Distribution by academic level
                - programming_languages: List of programming languages
        """
        stats = {
            'total_countries': len(self.current_data['universities']),
            'total_institutions': sum(len(country['institutions']) 
                                    for country in self.current_data['universities']),
            'total_courses': sum(len(institution['courseList'])
                               for country in self.current_data['universities']
                               for institution in country['institutions']),
            'courses_by_type': {},
            'courses_by_level': {'Undergraduate': 0, 'Graduate': 0, 'Both': 0},
            'programming_languages': set()
        }
        
        # Collect detailed statistics
        for country in self.current_data['universities']:
            for institution in country['institutions']:
                for course in institution['courseList']:
                    stats['courses_by_type'][course['type']] = \
                        stats['courses_by_type'].get(course['type'], 0) + 1
                    stats['courses_by_level'][course['level']] += 1
                    stats['programming_languages'].update(course.get('languages', []))
        
        stats['programming_languages'] = list(stats['programming_languages'])
        return stats

# Example usage
if __name__ == "__main__":
    # Local usage example
    collector = UniversityDataCollector('data/databases/university-courses-complete.json')
    
    # Add example institution
    example_courses = [
        {
            'name': 'Advanced Machine Learning',
            'level': 'Graduate',
            'languages': ['Python', 'PyTorch'],
            'type': 'NLP'
        },
        {
            'name': 'Statistical Language Models',
            'level': 'Graduate',
            'languages': ['Python'],
            'type': 'Data Analysis'
        }
    ]
    
    # Add the example institution
    collector.add_institution(
        country='Greece',
        institution_name='Athens University of Economics and Business',
        courses=example_courses
    )
    
    # Print database statistics
    stats = collector.get_database_stats()
    print("\nDatabase Statistics:")
    print(f"Total Countries: {stats['total_countries']}")
    print(f"Total Institutions: {stats['total_institutions']}")
    print(f"Total Courses: {stats['total_courses']}")
    print("\nCourses by Type:")
    for course_type, count in stats['courses_by_type'].items():
        print(f"  {course_type}: {count}")
    print("\nCourses by Level:")
    for level, count in stats['courses_by_level'].items():
        print(f"  {level}: {count}")
    print("\nProgramming Languages Used:")
    print(", ".join(stats['programming_languages']))
