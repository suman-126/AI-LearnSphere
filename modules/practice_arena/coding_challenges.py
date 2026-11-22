# ==========================================
# AI LEARNSPHERE - PYTHON CODING CHALLENGES
# ==========================================

CODING_CHALLENGES = [

    {
        "id": 1,
        "title": "Sum of Two Numbers",
        "difficulty": "Beginner",
        "topic": "Python Basics",
        "description": (
            "Write a Python function that accepts two numbers "
            "and returns their sum."
        ),
        "example_input": "add_numbers(5, 3)",
        "example_output": "8",
        "expected_concepts": [
            "Function definition",
            "Parameters",
            "Return statement",
            "Addition"
        ]
    },

    {
        "id": 2,
        "title": "Check Even or Odd",
        "difficulty": "Beginner",
        "topic": "Conditional Statements",
        "description": (
            "Write a Python function that accepts an integer "
            "and returns 'Even' if it is divisible by 2, "
            "otherwise returns 'Odd'."
        ),
        "example_input": "check_number(7)",
        "example_output": "'Odd'",
        "expected_concepts": [
            "Function definition",
            "Conditional statements",
            "Modulo operator",
            "Return statement"
        ]
    },

    {
        "id": 3,
        "title": "Find the Largest Number",
        "difficulty": "Beginner",
        "topic": "Conditional Statements",
        "description": (
            "Write a Python function that accepts three numbers "
            "and returns the largest number."
        ),
        "example_input": "find_largest(10, 25, 15)",
        "example_output": "25",
        "expected_concepts": [
            "Functions",
            "Conditional statements",
            "Comparison operators"
        ]
    },

    {
        "id": 4,
        "title": "Reverse a String",
        "difficulty": "Intermediate",
        "topic": "Strings",
        "description": (
            "Write a Python function that accepts a string "
            "and returns the string in reverse order."
        ),
        "example_input": "reverse_string('python')",
        "example_output": "'nohtyp'",
        "expected_concepts": [
            "String manipulation",
            "String slicing",
            "Functions",
            "Return statement"
        ]
    },

    {
        "id": 5,
        "title": "Count Vowels",
        "difficulty": "Intermediate",
        "topic": "Loops and Strings",
        "description": (
            "Write a Python function that counts and returns "
            "the number of vowels in a given string. "
            "Consider a, e, i, o and u in both uppercase "
            "and lowercase."
        ),
        "example_input": "count_vowels('Education')",
        "example_output": "5",
        "expected_concepts": [
            "Loops",
            "Strings",
            "Conditional statements",
            "String methods"
        ]
    },

    {
        "id": 6,
        "title": "Remove Duplicates",
        "difficulty": "Intermediate",
        "topic": "Lists",
        "description": (
            "Write a Python function that accepts a list "
            "and returns a new list containing only unique "
            "elements, preserving their original order."
        ),
        "example_input": "remove_duplicates([1, 2, 2, 3, 1])",
        "example_output": "[1, 2, 3]",
        "expected_concepts": [
            "Lists",
            "Loops",
            "Membership operators",
            "List operations"
        ]
    },

    {
        "id": 7,
        "title": "Check Palindrome",
        "difficulty": "Intermediate",
        "topic": "Strings",
        "description": (
            "Write a Python function that checks whether "
            "a string is a palindrome. Ignore letter case."
        ),
        "example_input": "is_palindrome('Level')",
        "example_output": "True",
        "expected_concepts": [
            "Strings",
            "String methods",
            "String comparison",
            "Functions"
        ]
    },

    {
        "id": 8,
        "title": "Find the Second Largest",
        "difficulty": "Advanced",
        "topic": "Lists and Logic",
        "description": (
            "Write a Python function that returns the second "
            "largest distinct number in a list. "
            "Return None if fewer than two distinct numbers exist."
        ),
        "example_input": "second_largest([10, 5, 20, 8, 20])",
        "example_output": "10",
        "expected_concepts": [
            "Lists",
            "Loops",
            "Comparison logic",
            "Duplicate handling",
            "Edge cases"
        ]
    }

]


def get_coding_challenges(difficulty=None):
    """Return all coding challenges or filter by difficulty."""

    if difficulty is None:
        return CODING_CHALLENGES.copy()

    return [
        challenge.copy()
        for challenge in CODING_CHALLENGES
        if challenge["difficulty"] == difficulty
    ]


def get_coding_challenge_by_id(challenge_id):
    """Return a coding challenge using its ID."""

    for challenge in CODING_CHALLENGES:

        if challenge["id"] == challenge_id:
            return challenge.copy()

    return None
