from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
from django.conf import settings

# Import your DSP logic from the new utils file
from .utils import calculate_vitals 

# Configure your Google API key
# Best practice is to put this in settings.py, but this works for testing
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", "AIzaSyBoHlm6jAu-9iopS_PE08SDPz7uxCCrEX0")
genai.configure(api_key=GEMINI_API_KEY)

@csrf_exempt 
def process_sensor_data(request):
    if request.method == 'POST':
        try:
            # 1. Parse the incoming JSON batch from the ESP32
            payload = json.loads(request.body)
            ir_batch = payload.get('ir_batch', [])
            red_batch = payload.get('red_batch', [])

            # Validation: Ensure we have enough data (at least 1 second of data at 100Hz)
            if len(ir_batch) < 100 or len(red_batch) < 100:
                return JsonResponse({"error": "Need at least 100 data points for accurate DSP"}, status=400)

            # 2. Process the raw signals using your utils function
            bpm, spo2 = calculate_vitals(ir_batch, red_batch)

            # 3. Handle poor readings (e.g., finger moved or wasn't on the sensor)
            if bpm == 0 or spo2 < 50:
                 return JsonResponse({
                     "status": "error",
                     "message": "Poor signal quality. Please hold finger still."
                 })

            # 4. Gemini Interpretation
            prompt = f"""
            You are an AI assisting with a health monitoring system. 
            The sensor has just recorded a Heart Rate of {bpm} BPM and an SpO2 level of {spo2}%. 
            Provide a brief, 2-sentence interpretation of these vitals. State if they are in normal ranges.
            Disclaimer: Remind the user you are an AI, not a doctor.
            """
            
            # Initialize the model and generate content
            model = genai.GenerativeModel("gemini-2.5-flash") # 1.5-flash is currently the standard stable model
            response = model.generate_content(prompt)
            interpretation = response.text.strip()

            # 5. Return the calculated data
            return JsonResponse({
                "status": "success",
                "calculated_bpm": bpm,
                "calculated_spo2": spo2,
                "ai_interpretation": interpretation
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Only POST allowed"}, status=405)