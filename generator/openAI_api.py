import os
import requests
from dotenv import load_dotenv
import json

# Load the .env file
load_dotenv()

# Get the GitHub token
github_token = os.getenv("GITHUB_TOKEN")


# Main function to generate test cases
def generate_test_cases(requirement):
    # Check if GitHub token exists
    if not github_token:
        return [
            {
                "id": 1,
                "title": "Configuration Error",
                "description": "GITHUB_TOKEN not found in environment variables. Please add it to your .env file.",
                "input": "N/A",
                "expected_output": "N/A",
                "priority": "High",
                "type": "Error",
                "selenium_code": "# No Selenium code available - GitHub token missing",
                "pytest_code": "# No Pytest code available - GitHub token missing",
            }
        ]

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }

    # ...existing code...
    data = {
        "model": "gpt-4.1",
        "messages": [
            {
                "role": "user",
                "content": f"""
You are a software test engineer. Generate exactly 5 test cases in valid JSON format (array of objects) for the following requirement:
\"\"\"{requirement}\"\"\"

For each test case, include:
- title
- description
- input
- expected_output
- priority
- type
- pytest_code: Pytest code for the test
- robot_code: Robot Framework code for the test
- manual_steps: a clear, step-by-step guide for a human tester to perform the test manually (as a string, use bullet points or numbered steps).

Return ONLY a JSON array with this exact structure:
[
  {{
    "id": 1,
    "title": "Test case title",
    "description": "Test case description",
    "input": "Input data or conditions",
    "expected_output": "Expected result",
    "priority": "High/Medium/Low",
    "type": "Functional/UI/Integration",
    "pytest_code": "# Pytest code ...",
    "robot_code": "*** Test Cases ***\nRobot Framework code ...",
    "manual_steps": "1. Open the app\n2. Enter valid credentials\n3. Click Login\n4. Verify dashboard is shown"
  }}
]

Make sure the code is properly escaped for JSON and includes realistic test scenarios and manual steps.
""",
            }
        ],
        "temperature": 0.7,
        "max_tokens": 6000,
    }

    try:
        # GitHub Models API endpoint
        response = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            headers=headers,
            json=data,
            timeout=60,  # Increased timeout for GitHub Models
        )

        # Debugging logs
        print("\nSTATUS CODE:", response.status_code)
        print("RESPONSE HEADERS:", dict(response.headers))

        if response.status_code != 200:
            error_msg = f"Request failed with status {response.status_code}"
            try:
                error_details = response.json()
                print("ERROR DETAILS:", error_details)
                if "error" in error_details:
                    if isinstance(error_details["error"], dict):
                        error_msg = error_details["error"].get("message", error_msg)
                    else:
                        error_msg = str(error_details["error"])
                elif "message" in error_details:
                    error_msg = error_details["message"]
            except Exception as parse_error:
                print(f"Could not parse error response: {parse_error}")
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"

            return [
                {
                    "id": 1,
                    "title": "GitHub Models API Error",
                    "description": error_msg,
                    "input": "N/A",
                    "expected_output": "N/A",
                    "priority": "High",
                    "type": "Error",
                    "selenium_code": "# API Error - No code available",
                    "pytest_code": "# API Error - No code available",
                }
            ]

        # Extract model output
        try:
            response_data = response.json()
            print("FULL RESPONSE:", json.dumps(response_data, indent=2))

            content = response_data["choices"][0]["message"]["content"].strip()
            print("MODEL OUTPUT:\n", content)

            # Clean content (remove markdown if present)
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            # Parse JSON
            test_cases = json.loads(content)

            # Validate that it's a list
            if not isinstance(test_cases, list):
                raise ValueError("Response is not a JSON array")

            # Validate and ensure all fields are present
            validated_cases = []
            for i, case in enumerate(test_cases):
                if not isinstance(case, dict):
                    print(f"Warning: Test case {i} is not a dictionary, skipping...")
                    continue

                validated_case = {
                    "id": case.get("id", i + 1),
                    "title": case.get("title", f"Test Case {i + 1}"),
                    "description": case.get("description", "No description provided"),
                    "input": case.get("input", "Not specified"),
                    "expected_output": case.get("expected_output", "Not specified"),
                    "priority": case.get("priority", "Medium"),
                    "type": case.get("type", "Functional"),
                    "pytest_code": case.get("pytest_code", "# No Pytest code provided"),
                    "robot_code": case.get(
                        "robot_code", "# No Robot Framework code provided"
                    ),
                    "manual_steps": case.get(
                        "manual_steps", "No manual steps provided"
                    ),
                }
                validated_cases.append(validated_case)

            if not validated_cases:
                return [
                    {
                        "id": 1,
                        "title": "No Valid Test Cases",
                        "description": "No valid test cases were generated by the model",
                        "input": "N/A",
                        "expected_output": "N/A",
                        "priority": "High",
                        "type": "Error",
                        "selenium_code": "# No valid test cases generated",
                        "pytest_code": "# No valid test cases generated",
                    }
                ]

            print(f"Successfully generated {len(validated_cases)} test cases")
            return validated_cases

        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw content: {content[:500]}...")
            return [
                {
                    "id": 1,
                    "title": "JSON Parse Error",
                    "description": f"Could not parse API response as JSON: {str(e)}",
                    "input": "N/A",
                    "expected_output": "N/A",
                    "priority": "High",
                    "type": "Error",
                    "selenium_code": "# Parse Error - No code available",
                    "pytest_code": "# Parse Error - No code available",
                }
            ]
        except KeyError as e:
            print(f"Response structure error: {e}")
            return [
                {
                    "id": 1,
                    "title": "Response Structure Error",
                    "description": f"Unexpected response structure: {str(e)}",
                    "input": "N/A",
                    "expected_output": "N/A",
                    "priority": "High",
                    "type": "Error",
                    "selenium_code": "# Structure Error - No code available",
                    "pytest_code": "# Structure Error - No code available",
                }
            ]

    except requests.exceptions.Timeout:
        return [
            {
                "id": 1,
                "title": "Timeout Error",
                "description": "Request to GitHub Models API timed out after 60 seconds",
                "input": "N/A",
                "expected_output": "N/A",
                "priority": "High",
                "type": "Error",
                "selenium_code": "# Timeout Error - No code available",
                "pytest_code": "# Timeout Error - No code available",
            }
        ]
    except requests.exceptions.ConnectionError:
        return [
            {
                "id": 1,
                "title": "Connection Error",
                "description": "Could not connect to GitHub Models API. Check your internet connection.",
                "input": "N/A",
                "expected_output": "N/A",
                "priority": "High",
                "type": "Error",
                "selenium_code": "# Connection Error - No code available",
                "pytest_code": "# Connection Error - No code available",
            }
        ]
    except Exception as e:
        print(f"Unexpected Exception: {e}")
        return [
            {
                "id": 1,
                "title": "Unexpected Error",
                "description": f"An unexpected error occurred: {str(e)}",
                "input": "N/A",
                "expected_output": "N/A",
                "priority": "High",
                "type": "Error",
                "selenium_code": "# Unexpected Error - No code available",
                "pytest_code": "# Unexpected Error - No code available",
            }
        ]
