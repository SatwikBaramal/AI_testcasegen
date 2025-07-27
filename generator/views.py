from django.shortcuts import render
from django.http import JsonResponse
from .openAI_api import generate_test_cases

def home(request):
    """Display the input form for entering requirements"""
    return render(request, 'generator/input_form.html')

def generate_testcases(request):
    """Generate test cases based on user requirements"""
    if request.method == "POST":
        requirement = request.POST.get("requirement")
        
        if not requirement:
            return render(request, 'generator/input_form.html', {
                'error': 'Please enter a requirement.'
            })
        
        # Generate test cases using the API
        testcases = generate_test_cases(requirement)
        
        # Store in session for JSON endpoints
        request.session['testcases'] = testcases
        request.session['requirement'] = requirement
        
        return render(request, 'generator/result.html', {
            'requirement': requirement,
            'testcases': testcases
        })
    
    # If GET request, redirect to home
    return render(request, 'generator/input_form.html')

def result(request):
    """Display stored test cases from session"""
    testcases = request.session.get('testcases', [])
    requirement = request.session.get('requirement', '')
    
    if not testcases:
        return render(request, 'generator/input_form.html', {
            'error': 'No test cases found. Please generate test cases first.'
        })
    
    return render(request, 'generator/result.html', {
        'testcases': testcases, 
        'requirement': requirement
    })
        
def test_cases_json(request):
    """Return all test cases as JSON"""
    if 'testcases' in request.session:
        return JsonResponse(request.session['testcases'], safe=False)
    else:
        return JsonResponse({"error": "No test cases found in session"}, status=404)

def test_case_json(request, case_id):
    """Return a specific test case as JSON"""
    if 'testcases' in request.session:
        testcases = request.session['testcases']
        for case in testcases:
            if case.get('id') == int(case_id):
                return JsonResponse(case)
        return JsonResponse({"error": f"Test case with ID {case_id} not found"}, status=404)
    else:
        return JsonResponse({"error": "No test cases found in session"}, status=404)