# =============================================================================
# STUDENT PERFORMANCE ANALYSIS SYSTEM
# =============================================================================
# What this program does:
#   1. Loads student records from a CSV file (students.csv)
#   2. Builds Student objects (AIUStudent or ScholarshipStudent)
#   3. Calculates averages and grades
#   4. Checks scholarship eligibility
#   5. Prints a performance report AND saves it as report.txt
#
# OOP PILLARS DEMONSTRATED IN THIS FILE:
#   • ENCAPSULATION  -> private/protected attributes + getters/setters
#   • ABSTRACTION    -> abstract base class Student(ABC) with @abstractmethod
#   • INHERITANCE    -> Student -> AIUStudent -> ScholarshipStudent
#   • POLYMORPHISM   -> get_details() / get_scholarship_status() behave
#                       differently depending on the object's real class
# =============================================================================

import csv
from abc import ABC, abstractmethod   # ABC = Abstract Base Class


# -----------------------------------------------------------------------------
# STANDALONE VALIDATION HELPER
# -----------------------------------------------------------------------------
# Why a module-level function instead of a method?
#   • It is used by BOTH Student.set_mark() AND Student.calculate_average()
#   • Keeping it outside the class = single source of truth for "what is a
#     valid mark?" -- if the rule changes, it changes in ONE place.
# -----------------------------------------------------------------------------
def check_mark(mark):
    # isinstance() ensures the value is a number (int or float).
    # Reject strings, None, lists, etc. before they ever get stored.
    if not isinstance(mark, (int, float)):
        raise ValueError(f"The Mark must be a number, got: {mark}")

    # Business rule: marks must be within the 0..100 range.
    # Anything outside this range is considered invalid input.
    if mark < 0 or mark > 100:
        raise ValueError(f"The Mark must be between 0 and 100, got: {mark}")


# =============================================================================
# PART 1 + 2: ABSTRACTION & ENCAPSULATION
# =============================================================================
# Student is an ABSTRACT BASE CLASS:
#   • It cannot be instantiated directly.
#   • It forces every concrete subclass to implement get_details().
#   • This is the ABSTRACTION pillar -- we describe WHAT a student is,
#     not HOW each specific student type should describe itself.
# =============================================================================
class Student(ABC):

    def __init__(self, student_id, fname, lname, programme, marks):
        # ENCAPSULATION:
        #   Single underscore "_"  = PROTECTED (convention: internal use)
        #   Double underscore "__" = PRIVATE   (name-mangled to _Student__marks)
        #
        # Protected attributes are still accessible, but subclasses &
        # related code are expected to use them. Outsiders should not.
        self._student_id = student_id
        self._fname      = fname
        self._lname      = lname
        self._programme  = programme

        # PRIVATE: Only Student's own methods can touch this dict.
        # Python name-mangles it to self._Student__marks.
        self.__marks = {}

        # Fill the private dict through set_mark() so that every mark
        # runs through validation -- even the initial ones from the CSV.
        for subject, mark in marks.items():
            self.set_mark(subject, mark)

    # -------------------------------------------------------------------------
    # GETTERS
    # -------------------------------------------------------------------------
    # Why getters instead of public attributes?
    #   The caller reads values without being able to assign arbitrary
    #   values directly to the underlying attributes.
    # -------------------------------------------------------------------------
    def get_student_id(self):
        return self._student_id

    def get_full_name(self):
        # Simple string concatenation of first + last name.
        return self._fname + " " + self._lname

    def get_programme(self):
        return self._programme

    def get_marks(self):
        # DEFENSIVE COPY: dict(...) creates a shallow copy of the private
        # marks dictionary. If a caller modifies the returned dict, the
        # internal state of the object is NOT affected.
        return dict(self.__marks)

    # -------------------------------------------------------------------------
    # SETTER (with validation)
    # -------------------------------------------------------------------------
    def set_mark(self, subject, mark):
        # Validate BEFORE storing -- the only writing path to __marks.
        check_mark(mark)
        self.__marks[subject] = mark

    # -------------------------------------------------------------------------
    # FLEXIBLE AVERAGE (variadic *marks)
    # -------------------------------------------------------------------------
    # This method has a DUAL behaviour:
    #   calculate_average()               -> average of stored marks
    #   calculate_average(70, 80, 90)     -> average of these 3 values
    #   calculate_average(70, 80, 90, 60) -> average of any number of values
    #
    # The *marks parameter bundles ALL positional args into a tuple.
    # If empty, we fall back to using the student's own stored marks.
    # -------------------------------------------------------------------------
    def calculate_average(self, *marks):

        # Case A: caller provided NO arguments -> use own stored marks.
        if len(marks) == 0:
            marks = list(self.__marks.values())

        # Edge case: no stored marks and no arguments -> cannot average.
        if len(marks) == 0:
            raise ValueError("There are no marks to average")

        # Re-validate every mark passed in (they did not go through set_mark).
        for mark in marks:
            check_mark(mark)

        # Arithmetic mean.
        return sum(marks) / len(marks)

    # -------------------------------------------------------------------------
    # GRADE CALCULATION
    # -------------------------------------------------------------------------
    # get_grade() delegates to calculate_average() instead of reading
    # __marks directly -- this respects encapsulation and means any
    # subclass that alters averaging logic automatically changes grading.
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # ABSTRACT METHOD (the CONTRACT)
    # -------------------------------------------------------------------------
    # @abstractmethod + ABC = every concrete subclass MUST implement this.
    # Student itself can never be instantiated.
    # This is the ABSTRACTION pillar in action: we define WHAT every
    # student must be able to do (describe itself), not HOW.
    # -------------------------------------------------------------------------
    @abstractmethod
    def get_details(self):
        pass


# =============================================================================
# PART 3: INHERITANCE (Level 1)
# =============================================================================
# AIUStudent is a NORMAL student (no scholarship).
# It INHERITS all getters, set_mark, calculate_average, get_grade
# from Student, and simply fulfils the abstract get_details() contract.
# =============================================================================
class AIUStudent(Student):

    # Implements the abstract method -> class becomes CONCRETE (instantiable).
    def get_details(self):
        return f"AIU student in {self.get_programme()}, grade {self.get_grade()}"

    # Default scholarship status for a normal student.
    # This will be OVERRIDDEN by ScholarshipStudent.
    # This is the BASE behaviour in a polymorphic pair.
    def get_scholarship_status(self):
        return "N/A"


# =============================================================================
# PART 4: INHERITANCE (Level 2) + POLYMORPHISM
# =============================================================================
# ScholarshipStudent INHERITS from AIUStudent (3-level chain:
# ABC -> Student -> AIUStudent -> ScholarshipStudent).
#
# It also OVERRIDES get_details() and get_scholarship_status(),
# which is what makes the polymorphism demo in main() meaningful:
# same method call, different behaviour based on real object class.
# =============================================================================
class ScholarshipStudent(AIUStudent):

    def __init__(self, student_id, fname, lname, programme, marks,
                 scholarship_amount):
        # super().__init__(...) runs Student.__init__, which:
        #   • stores the protected attributes
        #   • creates the private __marks dict
        #   • validates & stores each mark
        # Without this, none of the inherited getters would work.
        super().__init__(student_id, fname, lname, programme, marks)

        # Extra attribute specific to scholarship students.
        # (Public here for simplicity; could be _scholarship_amount.)
        self.scholarship_amount = scholarship_amount

    # Business rule: scholarship eligibility requires average >= 85.
    # calculate_average() is inherited, so we get the whole marks
    # averaging machinery for free.
    def is_eligible(self):
        return self.calculate_average() >= 85

    # -------------------------------------------------------------------------
    # OVERRIDING get_details()
    # -------------------------------------------------------------------------
    # We reuse the PARENT's description via super().get_details()
    # and APPEND scholarship info. This is the classic pattern of
    # "extend, don't replace".
    # -------------------------------------------------------------------------
    def get_details(self):
        details = super().get_details()   # AIUStudent's version
        if self.is_eligible():
            # {amount:,} adds thousands separators, e.g. 1,500,000
            return details + f" | scholarship of {self.scholarship_amount:,} (eligible)"
        return details + " | on scholarship list but average is below 85"

    # -------------------------------------------------------------------------
    # OVERRIDING get_scholarship_status()
    # -------------------------------------------------------------------------
    # AIUStudent returned "N/A"; here we return the real status.
    # THIS is the second polymorphic pair.
    # -------------------------------------------------------------------------
    def get_scholarship_status(self):
        if self.is_eligible():
            return "Eligible"
        return "Not eligible"


# =============================================================================
# PART 3 (cont.): AGGREGATION / COMPOSITION
# =============================================================================
# PerformanceAnalyzer "HAS A" list of Students. It does not own their
# data -- the list is injected from outside. This is the classic
# has-a relationship (as opposed to is-a = inheritance).
# =============================================================================
class PerformanceAnalyzer:

    def __init__(self, students):
        # Guard clause: an empty list would crash highest_average()
        # because it accesses self.students[0].
        if len(students) == 0:
            raise ValueError("Need at least one student to analyse")
        self.students = students

    # -------------------------------------------------------------------------
    # MIN/MAX AVERAGE (linear scans)
    # -------------------------------------------------------------------------
    # These return the STUDENT OBJECT, not just the number, so the
    # caller can also ask for that student's name, grade, etc.
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # PART 7: REPORT GENERATION
    # -------------------------------------------------------------------------
    # filename is OPTIONAL:
    #   • If provided -> also writes the report to that file.
    #   • In both cases -> returns the report string (so main() can print it).
    # -------------------------------------------------------------------------
    def generate_report(self, filename=None):
        lines = []

        # ---- Header ----
        lines.append("STUDENT PERFORMANCE REPORT")
        lines.append("=" * 100)

        # Column headings with fixed widths:
        #   {:<8} = left-align, width 8
        #   {:>6} = right-align, width 6
        # This is what makes columns line up visually.
        lines.append(
            f"{'ID':<8}{'Name':<18}{'Prog':<6}{'Math':>6}{'English':>9}{'Science':>9}"
            f"{'Average':>9}{'Grade':>7}  Scholarship"
        )
        lines.append("-" * 100)

        # ---- One row per student ----
        for student in self.students:
            # get_marks() returns a defensive copy -- safe to index freely.
            marks = student.get_marks()
            lines.append(
                f"{student.get_student_id():<8}{student.get_full_name():<18}"
                f"{student.get_programme():<6}{marks['Math']:>6}{marks['English']:>9}"
                f"{marks['Science']:>9}{student.calculate_average():>9.2f}"
                f"{student.get_grade():>7}  {student.get_scholarship_status()}"
            )

        # ---- Summary section ----
        top    = self.highest_average()
        bottom = self.lowest_average()
        lines.append("-" * 100)
        lines.append("CLASS PERFORMANCE SUMMARY")
        lines.append(f"Highest average: {top.get_full_name()} ({top.calculate_average():.2f})")
        lines.append(f"Lowest average:  {bottom.get_full_name()} ({bottom.calculate_average():.2f})")
        lines.append(f"Class average:   {self.class_average():.2f}")
        lines.append("=" * 100)

        # Join all lines with newline separators.
        report = "\n".join(lines)

        # Optional file write. Context manager ensures file closes
        # even if an exception occurs mid-write.
        if filename:
            with open(filename, "w") as file:
                file.write(report)

        return report


# =============================================================================
# CSV LOADER (factory-style function)
# =============================================================================
# This is where CONDITIONAL INSTANTIATION happens:
#   • ScholarshipAmount > 0 -> ScholarshipStudent
#   • ScholarshipAmount == 0 -> AIUStudent
# The result is a HETEROGENEOUS list -- which is what makes the
# polymorphism demo in main() work.
# =============================================================================
def load_students(filename):
    students = []

    # Context manager -> auto-close the CSV file.
    with open(filename) as file:
        # DictReader maps each row's headers to keys.
        reader = csv.DictReader(file)

        for row in reader:
            # Convert CSV strings to proper numeric types.
            marks = {
                "Math":    float(row["Math"]),
                "English": float(row["English"]),
                "Science": float(row["Science"]),
            }
            amount = int(row["ScholarshipAmount"])

            # Conditional object creation based on scholarship amount.
            if amount > 0:
                student = ScholarshipStudent(
                    row["StudentID"], row["FName"], row["LName"],
                    row["Programme"], marks, amount
                )
            else:
                student = AIUStudent(
                    row["StudentID"], row["FName"], row["LName"],
                    row["Programme"], marks
                )

            students.append(student)

    return students


# =============================================================================
# MAIN
# =============================================================================
def main():
    students = load_students("students.csv")

    # -------------------------------------------------------------------------
    # PART 5: POLYMORPHISM DEMO
    # -------------------------------------------------------------------------
    # Same call (`student.get_details()`) on different object types
    # produces different output depending on the object's ACTUAL class.
    # This is runtime polymorphism via method overriding.
    # -------------------------------------------------------------------------
    print("POLYMORPHISM DEMO")
    for student in students:
        print(f"{student.get_full_name()}: {student.get_details()}")

    # -------------------------------------------------------------------------
    # PART 6: FLEXIBLE AVERAGE DEMO
    # -------------------------------------------------------------------------
    # Shows the *marks variadic interface in action:
    #   • no args -> own marks
    #   • 3 args  -> average of those 3
    #   • 5 args  -> average of those 5
    # Also shows the validation raising and being caught.
    # -------------------------------------------------------------------------
    print("\nFLEXIBLE AVERAGE DEMONSTRATION")
    first = students[0]
    print("Own marks:        ", round(first.calculate_average(), 2))
    print("Three marks:      ", round(first.calculate_average(70, 80, 90), 2))
    print("Five marks:       ", round(first.calculate_average(70, 80, 90, 60, 55), 2))

    # Deliberately bad input -> ValueError from check_mark() -> caught here.
    try:
        first.calculate_average(70, 150)
    except ValueError as error:
        print("Invalid input caught:", error)

    # -------------------------------------------------------------------------
    # PART 7: REPORT (printed AND saved to report.txt)
    # -------------------------------------------------------------------------
    print()
    analyzer = PerformanceAnalyzer(students)
    print(analyzer.generate_report("report.txt"))


# Entry point -- only runs when this file is executed directly.
main()