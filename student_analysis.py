# Student Performance Analysis System
# Loads student records from a CSV(students.csv) file, and then calculates the averages and grades,
# checks for the student's scholarship eligibility and prints a performance report.(report.txt)

import csv
from abc import ABC, abstractmethod


# each of the students mark in the program will go through the same check
def check_mark(mark):
    if not isinstance(mark, (int, float)):
        raise ValueError(f"The Mark must be a number, got: {mark}")
    if mark < 0 or mark > 100:
        raise ValueError(f"The Mark must be between 0 and 100, got: {mark}")



# part2: encapsulation and abstraction part 

class Student(ABC):
    def __init__(self, student_id, fname, lname, programme, marks):
        # single underscore means its protected.
        self._student_id = student_id
        self._fname = fname
        self._lname = lname
        self._programme = programme
        # double underscore means its private, so only Student's own methods touch it and can work or modify it 
        self.__marks = {}
        for subject, mark in marks.items():
            self.set_mark(subject, mark)

    # ---- getters are used here so that the other code doesn't touch the any attribute directly ----
    def get_student_id(self):
        return self._student_id

    def get_full_name(self):
        return self._fname + " " + self._lname

    def get_programme(self):
        return self._programme

    def get_marks(self):
        # this function is used here to give back a copy so nobody can change the real marks by accident
        return dict(self.__marks)

    def set_mark(self, subject, mark):
        check_mark(mark)
        self.__marks[subject] = mark

    # ---- flexible interface using *marks ----
    # calculate_average()              -> calculates the average of the student's marks
    # calculate_average(70, 80, 90)    -> calculates the average of three marks that are given separately
    # calculate_average(70, 80, 90, 60) -> this works for any number of marks
    def calculate_average(self, *marks):
        if len(marks) == 0:
            marks = list(self.__marks.values())

        if len(marks) == 0:
            raise ValueError("There are no marks to average")

        for mark in marks:
            check_mark(mark)

        return sum(marks) / len(marks)

    def get_grade(self):
        average = self.calculate_average()
        if average >= 80:
            return "A"
        elif average >= 70:
            return "B"
        elif average >= 60:
            return "C"
        elif average >= 50:
            return "D"
        else:
            return "F"

    # abstract method: every subclass MUST write its own version
    @abstractmethod
    def get_details(self):
        pass


# AIUStudent: a normal student, will fill in the abstract method
class AIUStudent(Student):
    def get_details(self):
        return f"AIU student in {self.get_programme()}, grade {self.get_grade()}"

    # here when a normal student have no scholarship, this says should say N/A
    def get_scholarship_status(self):
        return "N/A"

# part 4: ScholarshipStudent will inherit from AIUStudent class above part
class ScholarshipStudent(AIUStudent):
    def __init__(self, student_id, fname, lname, programme, marks, scholarship_amount):
        # the function below will let the parent class to set up all the normal students data
        super().__init__(student_id, fname, lname, programme, marks)
        self.scholarship_amount = scholarship_amount

    # here a scholarship will need an average of at least 85 marks
    def is_eligible(self):
        return self.calculate_average() >= 85

    # overriding get_details: reuse the parent's text and add scholarship info
    def get_details(self):
        details = super().get_details()
        if self.is_eligible():
            return details + f" | scholarship of {self.scholarship_amount:,} (eligible)"
        return details + " | on scholarship list but average is below 85"

    # overriding will get_scholarship_status too
    def get_scholarship_status(self):
        if self.is_eligible():
            return "Eligible"
        return "Not eligible"



# part 3: the PerformanceAnalyzer class 
# It holds the student objects themselves, it doesn't copy their data at all.
class PerformanceAnalyzer:
    def __init__(self, students):
        if len(students) == 0:
            raise ValueError("Need at least one student to analyse")
        self.students = students

    def highest_average(self):
        best = self.students[0]
        for student in self.students:
            if student.calculate_average() > best.calculate_average():
                best = student
        return best

    def lowest_average(self):
        worst = self.students[0]
        for student in self.students:
            if student.calculate_average() < worst.calculate_average():
                worst = student
        return worst

    def class_average(self):
        total = 0
        for student in self.students:
            total += student.calculate_average()
        return total / len(self.students)

    # ---- part7: the report, this report will be generated then it will be save as report.txt ----
    # filename is optional, if given the report is also saved to a file
    def generate_report(self, filename=None):
        lines = []
        lines.append("STUDENT PERFORMANCE REPORT")
        lines.append("=" * 100)
        lines.append(
            f"{'ID':<8}{'Name':<18}{'Prog':<6}{'Math':>6}{'English':>9}{'Science':>9}"
            f"{'Average':>9}{'Grade':>7}  Scholarship"
        )
        lines.append("-" * 100)

        for student in self.students:
            marks = student.get_marks()
            lines.append(
                f"{student.get_student_id():<8}{student.get_full_name():<18}"
                f"{student.get_programme():<6}{marks['Math']:>6}{marks['English']:>9}"
                f"{marks['Science']:>9}{student.calculate_average():>9.2f}"
                f"{student.get_grade():>7}  {student.get_scholarship_status()}"
            )

        top = self.highest_average()
        bottom = self.lowest_average()
        lines.append("-" * 100)
        lines.append("CLASS PERFORMANCE SUMMARY")
        lines.append(f"Highest average: {top.get_full_name()} ({top.calculate_average():.2f})")
        lines.append(f"Lowest average:  {bottom.get_full_name()} ({bottom.calculate_average():.2f})")
        lines.append(f"Class average:   {self.class_average():.2f}")
        lines.append("=" * 100)

        report = "\n".join(lines)

        if filename:
            with open(filename, "w") as file:
                file.write(report)

        return report



# Read the CSV file and build the student objects from the file contents
def load_students(filename):
    students = []
    with open(filename) as file:
        reader = csv.DictReader(file)
        for row in reader:
            marks = {
                "Math": float(row["Math"]),
                "English": float(row["English"]),
                "Science": float(row["Science"]),
            }
            amount = int(row["ScholarshipAmount"])

            # here a scholarship amount means they are a ScholarshipStudent
            if amount > 0:
                student = ScholarshipStudent(row["StudentID"], row["FName"], row["LName"],
                                             row["Programme"], marks, amount)
            else:
                student = AIUStudent(row["StudentID"], row["FName"], row["LName"],
                                     row["Programme"], marks)
            students.append(student)
    return students


def main():
    students = load_students("students.csv")

    # part 5: polymorphism
    print("POLYMORPHISM DEMO")
    for student in students:
        print(f"{student.get_full_name()}: {student.get_details()}")

    # part 6: the interface part 
    print("\nFLEXIBLE AVERAGE DEMONSTRATION")
    first = students[0]
    print("Own marks:        ", round(first.calculate_average(), 2))
    print("Three marks:      ", round(first.calculate_average(70, 80, 90), 2))
    print("Five marks:       ", round(first.calculate_average(70, 80, 90, 60, 55), 2))
    try:
        first.calculate_average(70, 150)
    except ValueError as error:
        print("Invalid input caught:", error)

    # part 7: the report part 
    print()
    analyzer = PerformanceAnalyzer(students)
    print(analyzer.generate_report("report.txt"))


main()
