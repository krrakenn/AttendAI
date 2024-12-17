# Attend-A: Automated Attendance System

## Overview
Attend-A is a software application designed to automate the process of taking attendance in classrooms using facial recognition. Instead of manual roll calls, teachers can capture and upload class photos, and the software will identify students and mark their attendance. The system is personalized for individual teachers and ensures secure access to their data.

## Features
- **Facial Recognition:** Uses the `face_recognition` library to identify students in class photos.
- **Personalized System:** Each teacher has their own dataset and access control.
- **Student Enrollment:** Students must be enrolled by providing their details and a reference photo.
- **Multi-Photo Support:** Handles multiple class photos for larger classrooms.
- **CSV Integration:** Attendance and student data are stored in CSV files for easy access and manipulation.
- **Error Handling:** Prevents duplicate entries for students, subjects, and incomplete data submissions.
- **Subject-Based Attendance:** Teachers can define subjects and mark attendance for specific subjects.

## Technologies Used
- **Face Recognition Library:** For recognizing and comparing faces.
- **Kivy:** For creating the user interface.
- **Pandas:** For managing CSV files and manipulating data.
- **Python Modules:**
  - `os`: File operations.
  - `datetime`: For date and time stamping.

## How It Works
1. **Student Enrollment:**
   - Teachers enroll students by providing their details (e.g., name, scholar number, branch) and uploading their reference photos.
   - Face encodings (128 landmarks) are generated and stored for each student.

2. **Marking Attendance:**
   - Teachers create a subject and associate it with specific students.
   - They upload one or more class photos to capture all students present.
   - The software compares faces in the photo(s) with the enrolled students’ face encodings and marks attendance.

3. **Attendance Output:**
   - Generates a CSV file containing the attendance data for the selected subject and date.
   - Marks students present if they are recognized in the uploaded photo(s); others are marked absent.

## Example Workflow
1. Enroll students with their name, scholar number, branch, and a reference photo.
2. Add a subject (e.g., DSA for 5th semester CSE students).
3. Capture and upload class photos.
4. The system identifies students in the photos and updates the attendance CSV file.

## Limitations
- Requires a GPU for optimal performance due to the computational demands of the `face_recognition` library.
- Performance may be slower on systems with lower hardware capabilities.

## Future Enhancements
- Centralized access for multiple teachers.
- Enhanced UI/UX for better usability.
- Support for more complex classroom scenarios.

## Installation and Usage
1. Install dependencies:
   ```bash
   pip install face_recognition pandas kivy
