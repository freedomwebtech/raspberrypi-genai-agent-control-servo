from langchain.agents import initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from adafruit_servokit import ServoKit
from time import sleep
import re

# Initialize PCA9685 for servo control
kit = ServoKit(channels=16)

@tool
def control_servo(command: str) -> str:
    """
    Moves the servo based on AI decision. AI can decide to move the servo 
    to a specific angle (0-180) or within a range multiple times.

    Examples:
    - "Move servo from 0 to 180 five times."
    - "Move between 50 and 100."
    - "Go to 90 degrees."

    Args:
        command (str): The user command describing the movement.

    Returns:
        str: A message indicating what action was performed.
    """
    try:
        # Check for range movement with repeat count (e.g., "Move from 80 to 30 ten times")
        match_range = re.search(r"(\d+)\s*to\s*(\d+)\s*(\d*)", command, re.IGNORECASE)

        if match_range:
            start_angle, end_angle = int(match_range.group(1)), int(match_range.group(2))
            repeat_count = int(match_range.group(3)) if match_range.group(3).isdigit() else 1  # Ensure it's a number
            
            if 0 <= start_angle <= 180 and 0 <= end_angle <= 180 and repeat_count > 0:
                for _ in range(repeat_count):  # Move back and forth as AI decides
                    for angle in range(start_angle, end_angle + 1, 5):
                        kit.servo[0].angle = angle
                        sleep(0.05)
                    for angle in range(end_angle, start_angle - 1, -5):
                        kit.servo[0].angle = angle
                        sleep(0.05)
                return f"? Servo moved from {start_angle}° to {end_angle}° {repeat_count} times."
        
        # Extract single angle command (e.g., "Move to 90 degrees")
        match_single = re.search(r"(\d+)", command)
        if match_single:
            angle = int(match_single.group(1))
            if 0 <= angle <= 180:
                kit.servo[0].angle = angle
                return f"? Servo moved to {angle} degrees."
        
        return "? AI could not determine a valid angle or range."

    except ValueError:
        return "? Invalid input! AI needs a valid number."

# AI Model Initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=""  # Provide your Google API key
)

# Initialize AI Agent with Servo Tool
agent = initialize_agent(
    tools=[control_servo],  # AI decides when to call control_servo
    llm=llm,
    agent_type="OPENAI_FUNCTIONS",
    verbose=True  # Enable debugging
)

# AI Servo Chatbot Loop
print("\n?? AI Servo Chatbot Started! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit", "stop"]:
        print("?? Goodbye!")
        break

    # AI agent decides whether to call control_servo
    response = agent.run(user_input)
    
    print(f"?? AI: {response}")


