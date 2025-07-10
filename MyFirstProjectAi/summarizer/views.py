import os
import google.generativeai as genai
from dotenv import load_dotenv # To load environment variables from .env

# Import necessary things from Django REST Framework
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status # For HTTP status codes

# --- Configuration ---
# Load environment variables from .env file (should be in MyFirstProjectAi/ folder)
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_model = None # Initialize to None

if GEMINI_API_KEY:  # Check if the Python variable GEMINI_API_KEY has a value
    try:
        # Attempt to configure the Gemini library with the API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # If configuration is successful, initialize the model
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') # Or your preferred Gemini model
        
        print("Gemini API configured successfully.")
    except Exception as e:
        # If any error occurs during configuration or model initialization
        print(f"ERROR: Could not configure Gemini API: {e}")
        # In a real app, you'd log this error and potentially prevent app startup
        # or have the API endpoint return an appropriate error.
else:
    # This block executes if the Python variable GEMINI_API_KEY is None or an empty string
    print("ERROR: GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
    # API will likely fail if key is not set.
    # gemini_model remains None (or its initial value before this block)

    # --- Helper Function for AI Interaction ---
def get_ai_response(text_input, task_prompt_template):
    """
    Sends a prompt to the Gemini API and returns the text response.
    task_prompt_template should be a string with a placeholder {text_input}.
    """
    if not gemini_model: # Check if the model was initialized
        print("ERROR: Gemini model not initialized (likely API key issue).")
        return "Error: AI Model not initialized. Check API key configuration."

    # Construct the full prompt by inserting the user's text into the template
    prompt = task_prompt_template.format(text_input=text_input)
    
    try:
        # Send the prompt to the Gemini model and get the response
        response = gemini_model.generate_content(prompt)
        
        # It's good practice to check if the response has parts and text
        if response.parts:
            # If there are parts, access the text content of the response
            return response.text
        else:
            # This can happen if content is blocked by safety filters, or other rare issues.
            # Log the feedback for debugging purposes.
            print(f"AI response was empty or blocked. Feedback: {response.prompt_feedback}")
            return "Error: AI model did not return a valid response. This could be due to safety filters or other issues."
    except Exception as e:
        # Catch any other exceptions that might occur during the API call
        print(f"Error calling Gemini API: {e}")
        return f"Error: Could not get response from AI model: {e}"
    
# --- API Endpoint View ---
@api_view(['POST']) # This decorator ensures the view only accepts POST requests
                    # and provides DRF's request/response objects.
def process_text_view(request):
    """
    API endpoint to receive text, get summary and keywords from Gemini,
    and return them.
    """
    # 1. Check if the Gemini model was initialized successfully earlier
    if not gemini_model:
        return Response(
            {"error": "AI Service not available. Please check server configuration."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE # Service Unavailable
        )

    # 2. Access the input text from the request body
    #    request.data is DRF's way of accessing parsed request body (e.g., JSON)
    input_text = request.data.get('text', None)

    # 3. Validate the input_text
    if not input_text: # Checks if 'text' key was missing or its value was None/empty
        return Response({"error": "No text provided in the request body."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not isinstance(input_text, str) or not input_text.strip(): # More specific checks
        return Response({"error": "Text must be a non-empty string."}, status=status.HTTP_400_BAD_REQUEST)

    # ... (the rest of the function: calling get_ai_response, constructing final response) ...

      # --- THIS IS THE NEXT PART ---
    # --- Part D: Call get_ai_response for Summarization ---
    # (You should experiment with and refine this prompt template!)
    summary_prompt_template = (
    "Summarize the following text concisely, focusing on the main points and key takeaways. "
    "The summary should be easy to understand. Here is the text:\n\n"
    "--- TEXT BEGINS ---\n"
    "{text_input}\n"  # Placeholder for the actual text
    "--- TEXT ENDS ---\n\n"
    "Provide only the concise summary below:\n"
)
    # Call our helper function with the user's input text and the summary prompt template
    summary = get_ai_response(input_text, summary_prompt_template)


    # --- Part E: Call get_ai_response for Keyword Extraction ---
    # (You should experiment with and refine this prompt template!)
    keywords_prompt_template = (
    "From the following text, extract the 5 to 7 most important and relevant keywords or key phrases. "
    "Return these keywords strictly as a comma-separated list, with no other introductory text or formatting. Here is the text:\n\n"
    "--- TEXT BEGINS ---\n"
    "{text_input}\n"  # Placeholder for the actual text
    "--- TEXT ENDS ---\n\n"
    "KEYWORDS (comma-separated list only):"
)
    # Call our helper function again, this time with the keyword prompt template
    keywords_str = get_ai_response(input_text, keywords_prompt_template)

    # MyFirstProjectAi/summarizer/views.py
# ... (all the code you just pasted) ...

    # --- Part F: Process the keywords string into a list ---
    # Basic parsing of keywords (you might want to refine this further)
    # Ensure keywords_str is a string and not an error message before splitting
    if isinstance(keywords_str, str) and "Error:" not in keywords_str:
        # Split the string by commas, then strip whitespace from each keyword,
        # and filter out any empty strings that might result from extra commas.
        keywords_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
    else:
        keywords_list = [] # Default to an empty list if keywords_str is an error or not a string
        # If keywords_str itself is an error message from get_ai_response,
        # we might want to log it or handle it more explicitly.
        # For now, an empty list means keyword extraction might have failed.
        if isinstance(keywords_str, str) and "Error:" in keywords_str:
            print(f"Debug: Keyword extraction returned an error: {keywords_str}")


    # --- Part G: Check if AI calls resulted in errors and construct final response ---
    # Check if either the summary or the keyword extraction (indicated by keywords_str)
    # resulted in an error message from our get_ai_response function.
    summary_had_error = isinstance(summary, str) and "Error:" in summary
    keywords_had_error = isinstance(keywords_str, str) and "Error:" in keywords_str
    
    if summary_had_error or keywords_had_error:
        # If there was an error in either AI call, return a 500 Internal Server Error.
        # We send back whatever results we got (which might include the error messages themselves)
        # to help with debugging on the client-side or for logging.
        error_payload = {
            "error_detail": "One or more AI processing tasks failed."
        }
        if summary_had_error:
            error_payload["summary_error"] = summary # This will be the error string from get_ai_response
        else:
            error_payload["summary_result"] = summary # This will be the (presumably successful) summary

        if keywords_had_error:
            error_payload["keywords_error"] = keywords_str # Error string
        else:
            # If keywords didn't have an error string, but keywords_list is empty,
            # it means either AI returned empty or parsing failed subtly.
            # For simplicity, we send keywords_list (which would be empty or parsed)
            error_payload["keywords_result"] = keywords_list

        return Response(error_payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # If both AI calls were successful (no "Error:" in their returned strings):
    return Response({
        "summary": summary,         # The summary string from Gemini
        "keywords": keywords_list   # The list of keyword strings
    }, status=status.HTTP_200_OK)   # OK

# End of the process_text_view function