from groq import Groq
import os
import json
from dotenv import load_dotenv
load_dotenv()

# Initialize Groq client (100% FREE tier)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def generate_concall_summary(text):
    """
    Generate structured summary using Groq's LLaMA 3 70B (FREE tier)
    
    Returns:
        (success: bool, result: dict or error_message: str)
    """
    if not text or len(text.strip()) < 50:
        return False, "Transcript text is empty or too short for analysis"

    prompt = f"""Analyze this earnings call transcript and extract insights in strict JSON format.

RULES:
- Use ONLY information explicitly stated in the transcript
- If something is not mentioned, write "Not mentioned"
- NEVER guess, infer, or hallucinate numbers/information
- Be concise and specific
- Return ONLY valid JSON with these exact field names

Extract these sections:
1. managementTone: one word - optimistic/cautious/neutral/pessimistic
2. confidenceLevel: one word - high/medium/low
3. keyPositives: array of 3-5 concise bullet points
4. keyConcerns: array of 3-5 concise bullet points  
5. forwardGuidance: object with revenue, margin, capex fields (strings)
6. capacityUtilization: string describing trends (or "Not mentioned")
7. growthInitiatives: array of 2-3 initiatives (or empty array)

Transcript:
{text}

Return ONLY valid JSON. No other text, no markdown, no explanations."""

    raw_response = ""
    try:
        # Groq API call - FREE tier (LLaMA 3 70B)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Respond ONLY with valid JSON. No other text, no markdown, no explanations."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",  # Free powerful model
            temperature=0.2,  # Lower = more deterministic = fewer hallucinations
            max_tokens=1200,
        )
        
        raw_response = chat_completion.choices[0].message.content
        if raw_response is None:
            return False, "API returned empty content"
        raw_response = raw_response.strip()
        
        # Clean potential markdown wrappers
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:].strip()
        if raw_response.startswith("```"):
            raw_response = raw_response[3:].strip()
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3].strip()
        
        # Parse JSON
        summary = json.loads(raw_response)
        
        # Ensure all required fields exist with safe defaults
        required_fields = [
            'managementTone', 'confidenceLevel', 'keyPositives', 
            'keyConcerns', 'forwardGuidance', 'capacityUtilization', 'growthInitiatives'
        ]
        
        for field in required_fields:
            if field not in summary:
                if field in ['keyPositives', 'keyConcerns', 'growthInitiatives']:
                    summary[field] = []
                else:
                    summary[field] = "Not mentioned"
        
        # Ensure forwardGuidance is an object with required subfields
        if not isinstance(summary['forwardGuidance'], dict):
            summary['forwardGuidance'] = {
                'revenue': str(summary['forwardGuidance']) if summary['forwardGuidance'] else 'Not mentioned',
                'margin': 'Not mentioned',
                'capex': 'Not mentioned'
            }
        else:
            for subfield in ['revenue', 'margin', 'capex']:
                if subfield not in summary['forwardGuidance']:
                    summary['forwardGuidance'][subfield] = 'Not mentioned'
        
        return True, summary
    
    except json.JSONDecodeError as e:
        # Return raw response for debugging
        response_preview = raw_response[:300] if raw_response else "(empty response)"
        return False, f"JSON parsing failed. Raw response: {response_preview}..."
    except Exception as e:
        return False, f"Processing error: {str(e)}"

def format_summary_for_display(summary):
    """
    Convert raw summary dict to user-friendly display format
    
    Returns:
        dict with display-ready values
    """
    # Handle forwardGuidance safely
    fg = summary.get('forwardGuidance', {})
    if not isinstance(fg, dict):
        fg = {'revenue': 'Not mentioned', 'margin': 'Not mentioned', 'capex': 'Not mentioned'}
    
    return {
        'Tone': summary.get('managementTone', 'Not mentioned').capitalize(),
        'Confidence': summary.get('confidenceLevel', 'Not mentioned').capitalize(),
        'Key Positives': summary.get('keyPositives', []) if isinstance(summary.get('keyPositives'), list) else [],
        'Key Concerns': summary.get('keyConcerns', []) if isinstance(summary.get('keyConcerns'), list) else [],
        'Revenue Guidance': fg.get('revenue', 'Not mentioned'),
        'Margin Guidance': fg.get('margin', 'Not mentioned'),
        'Capex Guidance': fg.get('capex', 'Not mentioned'),
        'Capacity Utilization': summary.get('capacityUtilization', 'Not mentioned'),
        'Growth Initiatives': summary.get('growthInitiatives', []) if isinstance(summary.get('growthInitiatives'), list) else []
    }