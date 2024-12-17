import os
from datetime import datetime
import pandas as pd
import face_recognition
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

class AttendanceSystemApp(App):
    STUDENT_FILE = "students.csv"
    SUBJECT_FILE = "subjects.csv"
    FACE_FILE = "faces.csv"

    def build(self):
        self.setup_files()

        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        mark_button = Button(
            text='Mark Attendance',
            size_hint=(1, 0.2)
        )
        mark_button.bind(on_press=self.mark_attendance)
        self.root.add_widget(mark_button)

        detention_button = Button(
            text='Release Detention List',
            size_hint=(1, 0.2)
        )
        detention_button.bind(on_press=self.release_detention_list)
        self.root.add_widget(detention_button)

        enroll_button = Button(
            text='Enroll Students',
            size_hint=(1, 0.2)
        )
        enroll_button.bind(on_press=self.enroll_students)
        self.root.add_widget(enroll_button)

        return self.root

    def setup_files(self):
        # Check and create students.csv
        if not os.path.exists(self.STUDENT_FILE):
            student_columns = ["Student Name", "Scholar No", "Branch", "Semester", "Email ID"]
            pd.DataFrame(columns=student_columns).to_csv(self.STUDENT_FILE, index=False)

        # Check and create subjects.csv
        if not os.path.exists(self.SUBJECT_FILE):
            subject_columns = ["Subject", "Branch", "Semester"]
            pd.DataFrame(columns=subject_columns).to_csv(self.SUBJECT_FILE, index=False)

        # Check and create faces.csv
        if not os.path.exists(self.FACE_FILE):
            face_columns = ["Scholar No", "Face Encoding"]
            pd.DataFrame(columns=face_columns).to_csv(self.FACE_FILE, index=False)

    def mark_attendance(self, instance):
        # Check if students.csv is empty
        students_df = pd.read_csv(self.STUDENT_FILE)
        if students_df.empty:
            self.show_popup("Error", "Enroll students first.")
            return

        # Check if subjects.csv is empty
        subjects_df = pd.read_csv(self.SUBJECT_FILE)
        if subjects_df.empty:
            self.prompt_subject_details(students_df)
            return

        # If subjects exist, let the user choose
        self.choose_existing_or_new_subject(subjects_df, students_df)

    def prompt_subject_details(self, students_df):
        # Prompt user to enter subject, branch, and semester
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Subject input
        subject_layout = BoxLayout(orientation='horizontal')
        subject_label = Label(text='Subject:', size_hint=(0.3, 1))
        subject_input = TextInput(multiline=False, size_hint=(0.7, 1))
        subject_layout.add_widget(subject_label)
        subject_layout.add_widget(subject_input)
        popup_layout.add_widget(subject_layout)

        # Branch input
        branch_layout = BoxLayout(orientation='horizontal')
        branch_label = Label(text='Branch:', size_hint=(0.3, 1))
        branch_input = TextInput(multiline=False, size_hint=(0.7, 1))
        branch_layout.add_widget(branch_label)
        branch_layout.add_widget(branch_input)
        popup_layout.add_widget(branch_layout)

        # Semester input
        semester_layout = BoxLayout(orientation='horizontal')
        semester_label = Label(text='Semester:', size_hint=(0.3, 1))
        semester_input = TextInput(multiline=False, size_hint=(0.7, 1))
        semester_layout.add_widget(semester_label)
        semester_layout.add_widget(semester_input)
        popup_layout.add_widget(semester_layout)

        # Submit button
        submit_button = Button(text='Submit', size_hint=(1, 0.2))
        popup_layout.add_widget(submit_button)

        # Popup creation
        popup = Popup(title='Enter Subject Details', content=popup_layout, size_hint=(0.8, 0.6))

        def on_submit(instance):
            subject = subject_input.text.strip()
            branch = branch_input.text.strip()
            semester = semester_input.text.strip()

            if not all([subject, branch, semester]):
                self.show_popup("Error", "Please fill in all fields.")
                return

            # Check if branch-semester pair exists in students.csv
            filtered_students = students_df[
                (students_df['Branch'].astype(str) == str(branch)) & (students_df['Semester'].astype(str) == str(semester))
            ]
            if filtered_students.empty:
                self.show_popup("Error", f"No students found for {branch} Semester {semester}.")
            else:
                # Read existing subjects from subjects.csv
                subjects_df = pd.read_csv(self.SUBJECT_FILE)

                # Check for duplicate subject-branch-semester
                if ((subjects_df["Subject"].astype(str) == str(subject)) &
                    (subjects_df["Branch"].astype(str) == str(branch)) &
                    (subjects_df["Semester"].astype(str) == str(semester))).any():
                    self.show_popup("Error", f"The subject '{subject}' for {branch} Semester {semester} already exists.")
                else:
                    # Add new subject to subjects.csv
                    new_subject = pd.DataFrame([[subject, branch, semester]], columns=["Subject", "Branch", "Semester"])
                    subjects_df = pd.concat([subjects_df, new_subject], ignore_index=True)
                    subjects_df.to_csv(self.SUBJECT_FILE, index=False)

                    # Create subject file
                    subject_file = f"{subject}-{branch}-{semester}.csv"
                    filtered_students[["Scholar No"]].to_csv(subject_file, index=False)
                    self.show_popup("Success", f"Subject '{subject}' added and attendance file created.")

            popup.dismiss()


        submit_button.bind(on_press=on_submit)
        popup.open()

    def choose_existing_or_new_subject(self, subjects_df, students_df):
        # Popup to choose between existing or new subject
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Button for selecting an existing subject
        select_existing_button = Button(text="Select Existing Subject", size_hint=(1, 0.2))
        popup_layout.add_widget(select_existing_button)

        # Button to add new subject
        add_subject_button = Button(text="Add New Subject", size_hint=(1, 0.2))
        popup_layout.add_widget(add_subject_button)

        # Popup creation
        popup = Popup(title='Choose Subject', content=popup_layout, size_hint=(0.8, 0.6))

        def on_select_existing(instance):
            # Create a new popup to choose an existing subject
            subject_popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

            # Spinner for existing subjects
            spinner_values = [
                f"{row['Subject']}({row['Branch']}-{row['Semester']})"
                for _, row in subjects_df.iterrows()
            ]
            subject_spinner = Spinner(
                text="Select Subject",
                values=spinner_values,
                size_hint=(1, 0.2)
            )
            subject_popup_layout.add_widget(subject_spinner)

            # Button to proceed
            proceed_button = Button(text="Proceed", size_hint=(1, 0.2))
            subject_popup_layout.add_widget(proceed_button)

            # New popup for existing subjects
            subject_popup = Popup(
                title='Select Existing Subject',
                content=subject_popup_layout,
                size_hint=(0.8, 0.6)
            )

            def on_proceed(instance):
                if subject_spinner.text == "Select Subject":
                    # Check if no subject is selected
                    self.show_popup("Error", "Select a subject first.")
                else:
                    # Popup to accept the number of class photos
                    def process_photos(photo_count):
                        photos = []

                        # Collect photos one by one
                        for i in range(photo_count):
                            photo_popup_layout = BoxLayout(orientation='vertical')
                            file_chooser = FileChooserListView(path=os.path.expanduser("~"))
                            photo_popup_layout.add_widget(file_chooser)

                            upload_button = Button(text="Upload", size_hint=(1, 0.2))
                            photo_popup_layout.add_widget(upload_button)

                            photo_popup = Popup(
                                title=f"Upload Photo {i + 1}",
                                content=photo_popup_layout,
                                size_hint=(0.8, 0.6)
                            )

                            def on_file_selected(instance):
                                selected_files = file_chooser.selection
                                if selected_files:
                                    photos.append(selected_files[0])
                                    photo_popup.dismiss()
                                    if len(photos) == photo_count:
                                        process_attendance(photos)

                            upload_button.bind(on_press=on_file_selected)
                            photo_popup.open()

                    def process_attendance(photos):
                        # Extract the subject's details from the spinner
                        import re
                        subject_details = subject_spinner.text
                        match = re.match(r'(\w+)\((\w+)-(\d+)\)', subject_details)

                        if match:
                            subject_code = match.group(1).lower()     
                            branch_code = match.group(2).lower()      
                            semester = match.group(3).lower()         
                            
                            subject_csv_file = f"{subject_code}-{branch_code}-{semester}.csv"
                        else:
                            raise ValueError(f"Invalid subject format: {subject_details}")

                        # Read the subject attendance CSV to fetch scholar numbers
                        subject_df = pd.read_csv(subject_csv_file)
                        scholar_numbers = subject_df['Scholar No'].tolist()

                        # Read the faces.csv to fetch encodings for scholar numbers
                        faces_df = pd.read_csv("faces.csv")
                        known_encodings = {}
                        for _, row in faces_df.iterrows():
                            if row['Scholar No'] in scholar_numbers:
                                known_encodings[row['Scholar No']] = eval(row['Face Encoding'])

                        # Initialize a dictionary to mark attendance
                        attendance = {scholar: 0 for scholar in scholar_numbers}

                        # Process each photo
                        for photo_path in photos:
                            unknown_image = face_recognition.load_image_file(photo_path)
                            unknown_encodings = face_recognition.face_encodings(unknown_image)

                            for unknown_encoding in unknown_encodings:
                                for scholar, known_encoding in known_encodings.items():
                                    result = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
                                    if result[0]:
                                        attendance[scholar] = 1

                        # Add attendance to the subject's CSV file
                        today_date = datetime.now().strftime('%Y-%m-%d')
                        subject_df[today_date] = subject_df['Scholar No'].apply(lambda x: attendance[x])
                        subject_df.to_csv(subject_csv_file, index=False)

                        self.show_popup("Success", "Attendance marked successfully.")

                    # New popup to accept the number of photos
                    num_photos_popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
                    num_photos_input = TextInput(multiline=False, input_filter='int', hint_text='Enter number of class photos')
                    num_photos_popup_layout.add_widget(num_photos_input)

                    submit_button = Button(text="Submit", size_hint=(1, 0.2))
                    num_photos_popup_layout.add_widget(submit_button)

                    num_photos_popup = Popup(
                        title="Enter Number of Photos",
                        content=num_photos_popup_layout,
                        size_hint=(0.8, 0.6)
                    )

                    def on_submit_photos(instance):
                        try:
                            num_photos = int(num_photos_input.text)
                            if num_photos > 0:
                                num_photos_popup.dismiss()
                                process_photos(num_photos)
                            else:
                                self.show_popup("Error", "Enter a valid number of photos.")
                        except ValueError:
                            self.show_popup("Error", "Enter a valid number of photos.")

                    submit_button.bind(on_press=on_submit_photos)
                    num_photos_popup.open()



            proceed_button.bind(on_press=on_proceed)
            subject_popup.open()

        def on_add_new_subject(instance):
            popup.dismiss()
            self.prompt_subject_details(students_df)

        select_existing_button.bind(on_press=on_select_existing)
        add_subject_button.bind(on_press=on_add_new_subject)
        popup.open()

    def release_detention_list(self, instance):
        self.show_popup('Release Detention List', 'This feature is under development.')

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text='Close', size_hint=(1, 0.2))
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_input_popup(self, title, callback):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        input_box = TextInput(multiline=False, size_hint=(1, 0.2))
        popup_layout.add_widget(input_box)
        submit_button = Button(text='Submit', size_hint=(1, 0.2))
        popup_layout.add_widget(submit_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))

        def on_submit(instance):
            popup.dismiss()
            callback(input_box.text)

        submit_button.bind(on_press=on_submit)
        popup.open()

    def enroll_students(self, instance):
        # Show student enrollment popup
        self.show_student_enrollment_popup()

    def show_student_enrollment_popup(self):
        # Create popup with multiple input fields
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Name input
        name_layout = BoxLayout(orientation='horizontal')
        name_label = Label(text='Name:', size_hint=(0.3, 1))
        self.name_input = TextInput(multiline=False, size_hint=(0.7, 1))
        name_layout.add_widget(name_label)
        name_layout.add_widget(self.name_input)
        popup_layout.add_widget(name_layout)

        # Scholar No input
        scholar_layout = BoxLayout(orientation='horizontal')
        scholar_label = Label(text='Scholar No:', size_hint=(0.3, 1))
        self.scholar_input = TextInput(multiline=False, size_hint=(0.7, 1))
        scholar_layout.add_widget(scholar_label)
        scholar_layout.add_widget(self.scholar_input)
        popup_layout.add_widget(scholar_layout)

        # Branch input
        branch_layout = BoxLayout(orientation='horizontal')
        branch_label = Label(text='Branch:', size_hint=(0.3, 1))
        self.branch_input = TextInput(multiline=False, size_hint=(0.7, 1))
        branch_layout.add_widget(branch_label)
        branch_layout.add_widget(self.branch_input)
        popup_layout.add_widget(branch_layout)

        # Semester input
        semester_layout = BoxLayout(orientation='horizontal')
        semester_label = Label(text='Semester:', size_hint=(0.3, 1))
        self.semester_input = TextInput(multiline=False, size_hint=(0.7, 1))
        semester_layout.add_widget(semester_label)
        semester_layout.add_widget(self.semester_input)
        popup_layout.add_widget(semester_layout)

        # Email input
        email_layout = BoxLayout(orientation='horizontal')
        email_label = Label(text='Email ID:', size_hint=(0.3, 1))
        self.email_input = TextInput(multiline=False, size_hint=(0.7, 1))
        email_layout.add_widget(email_label)
        email_layout.add_widget(self.email_input)
        popup_layout.add_widget(email_layout)

        # Submit button
        submit_button = Button(text='Submit', size_hint=(1, 0.2))
        popup_layout.add_widget(submit_button)

        # Create popup
        self.enrollment_popup = Popup(title='Enroll Student', content=popup_layout, size_hint=(0.8, 0.6))
        submit_button.bind(on_press=self.validate_student_details)
        self.enrollment_popup.open()

    def validate_student_details(self, instance):
        # Collect input values
        name = self.name_input.text.strip()
        scholar_no = self.scholar_input.text.strip()
        branch = self.branch_input.text.strip()
        semester = self.semester_input.text.strip()
        email = self.email_input.text.strip()

        # Validate all fields are filled
        if not all([name, scholar_no, branch, semester, email]):
            self.show_popup("Invalid Input", "Please fill in all fields.")
            return

        # Check if Scholar No already exists
        students_df = pd.read_csv(self.STUDENT_FILE)
        if scholar_no in students_df['Scholar No'].values:
            # Scholar No exists, skip the enrollment
            self.enrollment_popup.dismiss()
            self.show_popup("Duplicate Scholar No", f"Scholar No {scholar_no} already exists.")
            return

        # Proceed to face capture
        self.enrollment_popup.dismiss()
        self.capture_student_face(name, scholar_no, branch, semester, email)

    def capture_student_face(self, name, scholar_no, branch, semester, email):
        # Create a file chooser popup for face image
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(path=os.path.expanduser("~"))
        content.add_widget(file_chooser)

        # Select button
        select_button = Button(text='Select Image', size_hint=(1, 0.2))
        content.add_widget(select_button)

        # Create popup
        face_popup = Popup(title='Select Student Face Image', content=content, size_hint=(0.9, 0.9))

        def on_select(instance):
            selected_file = file_chooser.selection and file_chooser.selection[0]
            if selected_file:
                face_popup.dismiss()
                self.process_face_image(selected_file, name, scholar_no, branch, semester, email)
            else:
                self.show_popup("Error", "No image selected.")

        select_button.bind(on_press=on_select)
        face_popup.open()
    def process_face_image(self, face_image_path, name, scholar_no, branch, semester, email):
        try:
            # Load and encode face
            image = face_recognition.load_image_file(face_image_path)
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                raise ValueError("No face detected in the image.")

            # Save student details
            students_df = pd.read_csv(self.STUDENT_FILE)
            new_student = pd.DataFrame([[name, scholar_no, branch, semester, email]], 
                                        columns=students_df.columns)
            students_df = pd.concat([students_df, new_student], ignore_index=True)
            students_df.to_csv(self.STUDENT_FILE, index=False)

            # Save face encoding
            faces_df = pd.read_csv(self.FACE_FILE)
            face_encoding = face_encodings[0].tolist()
            new_face = pd.DataFrame([[scholar_no, face_encoding]], 
                                     columns=faces_df.columns)
            faces_df = pd.concat([faces_df, new_face], ignore_index=True)
            faces_df.to_csv(self.FACE_FILE, index=False)

            # Show success popup
            self.show_popup("Enrollment Success", f"Student {name} enrolled successfully.")

        except Exception as e:
            self.show_popup("Face Recognition Error", str(e))

if __name__ == '__main__':
    AttendanceSystemApp().run()