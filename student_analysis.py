
import csv
from abc import ABC, abstractmethod
def check_mark(mark):
    if not isinstance(mark, (int, float)):
        raise ValueError(f"The Mark must be a number, got: {mark}")
    if mark < 0 or mark > 100:
        raise ValueError(f"The Mark must be between 0 and 100, got: {mark}")



# encapsulation and abstraction part 

class Student(ABC):
    def __init__(self, student_id, fname, lname, programme, marks):
        self._student_id = student_id
        self._fname = fname
        self._lname = lname
        self._programme = programme
        # double underscore means its private, 
        self.__marks = {}
        for subject, mark in marks.items():
            self.set_mark(subject, mark)

    def get_student_id(self):
        return self._student_id

    def get_full_name(self):
        return self._fname + " " + self._lname

    def get_programme(self):
        return self._programme

    def get_marks(self):
        return dict(self.__marks)

    def set_mark(self, subject, mark):
        check_mark(mark)
        self.__marks[subject] = mark

    
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

    @abstractmethod
    def get_details(self):
        pass

class AIUStudent(Student):
    def get_details(self):
        return f"AIU student in {self.get_programme()}, grade {self.get_grade()}"

    def get_scholarship_status(self):
        return "N/A"

# part 4: ScholarshipStudent will inherit from AIUStudent class above part
class ScholarshipStudent(AIUStudent):
    def __init__(self, student_id, fname, lname, programme, marks, scholarship_amount):
        super().__init__(student_id, fname, lname, programme, marks)
        self.scholarship_amount = scholarship_amount

    def is_eligible(self):
        return self.calculate_average() >= 85

    def get_details(self):
        details = super().get_details()
        if self.is_eligible():
            return details + f" | scholarship of {self.scholarship_amount:,} (eligible)"
        return details + " | on scholarship list but average is below 85"

    def get_scholarship_status(self):
        if self.is_eligible():
            return "Eligible"
        return "Not eligible"



# part 3: the PerformanceAnalyzer class 
# It holds the student objects themselves
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



# this will read the csv file and build the objects from the details 
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
