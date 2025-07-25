import os
import requests
from dotenv import load_dotenv
import json

# Load the .env file
load_dotenv()

# Get the Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Main function to generate test cases
def generate_test_cases(requirement):
    # Check if API key exists
    if not api_key:
        return [{
            "id": 1,
            "title": "Configuration Error",
            "description": "GROQ_API_KEY not found in environment variables. Please add it to your .env file.",
            "input": "N/A",
            "expected_output": "N/A",
            "priority": "High",
            "type": "Error",
            "selenium_code": "# No Selenium code available - API key missing",
            "pytest_code": "# No Pytest code available - API key missing"
        }]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "user",
                "content": f"""
You are a software test engineer. Generate exactly 5 test cases in valid JSON format (array of objects) for the following requirement:

\"\"\"{requirement}\"\"\"

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
    "selenium_code": "# Selenium WebDriver test code\\nfrom selenium import webdriver\\nfrom selenium.webdriver.common.by import By\\nfrom selenium.webdriver.support.ui import WebDriverWait\\nfrom selenium.webdriver.support import expected_conditions as EC\\n\\ndef test_example():\\n    driver = webdriver.Chrome()\\n    try:\\n        driver.get('https://example.com')\\n        # Add test steps here\\n        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'example-id')))\\n        element.click()\\n        assert 'Expected' in driver.page_source\\n    finally:\\n        driver.quit()",
    "pytest_code": "# Pytest test code\\nimport pytest\\n\\ndef test_example():\\n    # Add test logic here\\n    result = perform_test_function()\\n    assert result is not None\\n    assert result == 'expected_value'"
  }}
]

Do not include markdown formatting or explanations.
"""
            }
        ],
        "temperature": 0.3,
        "max_tokens": 6000
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",  #api endpoint POST request
            headers=headers,
            json=data,
            timeout=30
        )

        # Debugging logs
        print("\nSTATUS CODE:", response.status_code)

        if response.status_code != 200:
            error_msg = f"Request failed with status {response.status_code}"
            try:
                error_details = response.json()
                if 'error' in error_details:
                    error_msg = error_details['error'].get('message', error_msg)
            except:
                pass
            
            return [{
                "id": 1,
                "title": "API Error",
                "description": error_msg,
                "input": "N/A",
                "expected_output": "N/A",
                "priority": "High",
                "type": "Error",
                "selenium_code": "# API Error - No code available",
                "pytest_code": "# API Error - No code available"
            }]

        # Extract model output
        try:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"].strip()
            print("MODEL OUTPUT:\n", content)

            # Clean content (remove markdown if present)
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            # Parse JSON
            test_cases = json.loads(content)
            
            # Validate and ensure all fields are present
            validated_cases = []
            for i, case in enumerate(test_cases):
                validated_case = {
                    "id": case.get("id", i + 1),
                    "title": case.get("title", f"Test Case {i + 1}"),
                    "description": case.get("description", "No description provided"),
                    "input": case.get("input", "Not specified"),
                    "expected_output": case.get("expected_output", "Not specified"),
                    "priority": case.get("priority", "Medium"),
                    "type": case.get("type", "Functional"),
                    "selenium_code": case.get("selenium_code", "# No Selenium code provided"),
                    "pytest_code": case.get("pytest_code", "# No Pytest code provided")
                }
                validated_cases.append(validated_case)
            
            print(f"Successfully generated {len(validated_cases)} test cases")
            return validated_cases

        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            return [{
                "id": 1,
                "title": "JSON Parse Error",
                "description": f"Could not parse API response: {str(e)}",
                "input": "N/A",
                "expected_output": "N/A",
                "priority": "High",
                "type": "Error",
                "selenium_code": "# Parse Error - No code available",
                "pytest_code": "# Parse Error - No code available"
            }]

    except requests.exceptions.Timeout:
        return [{
            "id": 1,
            "title": "Timeout Error",
            "description": "Request timed out",
            "input": "N/A",
            "expected_output": "N/A",
            "priority": "High",
            "type": "Error",
            "selenium_code": "# Timeout Error - No code available",
            "pytest_code": "# Timeout Error - No code available"
        }]
    except Exception as e:
        print(f"Exception: {e}")
        return [{
            "id": 1,
            "title": "Request Exception",
            "description": str(e),
            "input": "N/A",
            "expected_output": "N/A",
            "priority": "High",
            "type": "Error",
            "selenium_code": "# Error - No code available",
            "pytest_code": "# Error - No code available"
        }]