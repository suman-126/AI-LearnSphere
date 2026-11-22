PYTHON_VARIABLES_QUESTIONS =[
    {
        "question": "Which operator is used to assign a value to a variable in Python?",
        "options": {
            "A": "+",
            "B": "=",
            "C": "==",
            "D": "*"
        },
        "correct_answer": "B",
        "explanation": "The assignment operator (=) assigns a value to a variable."
    },
    {
        "question": "Which of the following is a valid Python variable name?",
        "options": {
            "A": "2name",
            "B": "first-name",
            "C": "first_name",
            "D": "class"
        },
        "correct_answer": "C",
        "explanation": "A variable name can contain letters, digits and underscores, but it cannot start with a digit or be a reserved keyword."
    },
    {
        "question": "What is the value of x after this code executes?\nx = 10\nx = 25",
        "options": {
            "A": "10",
            "B": "25",
            "C": "35",
            "D": "An error occurs"
        },
        "correct_answer": "B",
        "explanation": "The second assignment replaces the previous value of x with 25."
    },
    {
        "question": "What is the data type of x?\nx = 12",
        "options": {
            "A": "str",
            "B": "float",
            "C": "int",
            "D": "bool"
        },
        "correct_answer": "C",
        "explanation": "The value 12 is a whole number, so its data type is int."
    },
    {
        "question": "What is the value of a after this statement?\na, b = 5, 8",
        "options": {
            "A": "5",
            "B": "8",
            "C": "13",
            "D": "None"
        },
        "correct_answer": "A",
        "explanation": "Multiple assignment assigns 5 to a and 8 to b."
    },
    {
        "question": "Are Python variable names case-sensitive?",
        "options": {
            "A": "No, uppercase and lowercase are always identical",
            "B": "Yes, name and Name are different",
            "C": "Only for numbers",
            "D": "Only inside functions"
        },
        "correct_answer": "B",
        "explanation": "Python distinguishes uppercase and lowercase letters in variable names."
    },
    {
        "question": "What does this code print?\nx = 4\nx = x + 3\nprint(x)",
        "options": {
            "A": "4",
            "B": "3",
            "C": "7",
            "D": "43"
        },
        "correct_answer": "C",
        "explanation": "The expression adds 3 to the current value of x, making x equal to 7."
    },
    {
        "question": "What happens when a variable is assigned a new value of a different type in Python?",
        "options": {
            "A": "Python always raises an error",
            "B": "The variable must be declared again",
            "C": "The variable can refer to a value of the new type",
            "D": "Python converts every value to a string"
        },
        "correct_answer": "C",
        "explanation": "Python is dynamically typed, so a variable can refer to values of different types at different times."
    },
    {
        "question": "What does the del statement do when used with a variable?",
        "options": {
            "A": "Deletes the variable name binding",
            "B": "Changes the variable into an integer",
            "C": "Prints the variable value",
            "D": "Creates a new variable"
        },
        "correct_answer": "A",
        "explanation": "The del statement removes the name binding, so the variable name can no longer be used unless assigned again."
    },

    {
        "question": "Which statement correctly creates a variable named age with the value 20?",
        "options": {
            "A": "variable age = 20",
            "B": "age = 20",
            "C": "int age = 20",
            "D": "create age = 20"
        },
        "correct_answer": "B",
        "explanation": "Python creates a variable when a value is assigned to a name using the assignment operator."
    },
    {
        "question": "What is the data type of the variable name?\nname = \"Alex\"",
        "options": {
            "A": "int",
            "B": "bool",
            "C": "str",
            "D": "float"
        },
        "correct_answer": "C",
        "explanation": "A value enclosed in quotation marks is a string, so the variable name refers to a str value."
    },
    {
        "question": "What is the data type of price?\nprice = 19.5",
        "options": {
            "A": "int",
            "B": "float",
            "C": "str",
            "D": "bool"
        },
        "correct_answer": "B",
        "explanation": "The number 19.5 contains a decimal point, so its type is float."
    },
    {
        "question": "What is the value of x after this statement?\nx = 7\nx += 3",
        "options": {
            "A": "7",
            "B": "3",
            "C": "10",
            "D": "73"
        },
        "correct_answer": "C",
        "explanation": "The += operator adds 3 to the current value of x and assigns the result back to x."
    },
    {
        "question": "What values are assigned by this statement?\na = b = 10",
        "options": {
            "A": "a is 10 and b is 0",
            "B": "a is 0 and b is 10",
            "C": "Both a and b are 10",
            "D": "An error occurs"
        },
        "correct_answer": "C",
        "explanation": "Chained assignment assigns the same value, 10, to both variables."
    },
    {
        "question": "What is the value of y after this code?\nx = 5\ny = x",
        "options": {
            "A": "0",
            "B": "5",
            "C": "x",
            "D": "An error occurs"
        },
        "correct_answer": "B",
        "explanation": "The assignment y = x assigns the current value of x to y, which is 5."
    },
    {
        "question": "Which character is commonly used at the beginning of a variable name to indicate a non-public attribute by convention?",
        "options": {
            "A": "#",
            "B": "@",
            "C": "_",
            "D": "$"
        },
        "correct_answer": "C",
        "explanation": "A leading underscore is a Python naming convention indicating that a name is intended for internal use."
    },
    {
        "question": "What is the value of result?\nfirst, second = 4, 6\nresult = first + second",
        "options": {
            "A": "4",
            "B": "6",
            "C": "10",
            "D": "46"
        },
        "correct_answer": "C",
        "explanation": "The variables first and second receive 4 and 6 respectively. Their sum is 10."
    },
    {
        "question": "What happens when this statement is executed?\nx = None",
        "options": {
            "A": "x refers to the special None value",
            "B": "x is automatically assigned zero",
            "C": "x becomes an empty string",
            "D": "Python raises a syntax error"
        },
        "correct_answer": "A",
        "explanation": "None is a special Python value commonly used to represent the absence of a value."
    },
    {
        "question": "What is the value of x after this code?\nx = 10\nx = \"Hello\"",
        "options": {
            "A": "10",
            "B": "\"Hello\"",
            "C": "Both values are stored in x",
            "D": "A type error occurs"
        },
        "correct_answer": "B",
        "explanation": "Python variables can be reassigned to values of different types. After the second assignment, x refers to the string Hello."
    },
    {
        "question": "Which built-in function can be used to check the type of a variable?",
        "options": {
            "A": "check()",
            "B": "datatype()",
            "C": "type()",
            "D": "variable()"
        },
        "correct_answer": "C",
        "explanation": "The built-in type() function returns the type of an object."
    }
]
