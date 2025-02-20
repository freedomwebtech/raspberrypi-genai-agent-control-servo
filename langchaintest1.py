from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from adafruit_servokit import ServoKit
from time import sleep
import re

# Initialize PCA9685 for servo control
kit = ServoKit(channels=16)

def control_servo(angle_input):
    """ Moves the servo based on user input or AI command. """
    try:
        # Check for range movement (e.g., "30 to 180")
        match_range = re.search(r"(\d+)\s*to\s*(\d+)", angle_input)
        
        if match_range:
            start_angle, end_angle = int(match_range.group(1)), int(match_range.group(2))
            if 0 <= start_angle <= 180 and 0 <= end_angle <= 180:
                for _ in range(2):  # Repeat movement twice
                    for angle in range(start_angle, end_angle + 1, 5):  # Move in steps of 5
                        kit.servo[0].angle = angle
                        sleep(0.05)
                    for angle in range(end_angle, start_angle - 1, -5):
                        kit.servo[0].angle = angle
                        sleep(0.05)
                return f"✅ Servo moved from {start_angle}° to {end_angle}° twice."
            else:
                return "⚠️ Invalid angle range! Use values between 0 and 180."
        
        # Extract single angle from input
        match = re.search(r"(\d+)", angle_input)
        if match:
            angle = int(match.group(1))
            if 0 <= angle <= 180:
                kit.servo[0].angle = angle
                return f"✅ Servo moved to {angle} degrees."
            else:
                return "⚠️ Invalid angle! Please enter a value between 0 and 180."
        
        return "❌ Could not determine a valid angle. Try saying 'Move servo to 90 degrees'."
    
    except ValueError:
        return "❌ Invalid input! Please enter a number."

# AI Model Initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="AIzaSyA5cBPIyHwJ7dfIgIo2eOJf5XwJVoIYde0"  # Provide your Google API key
)

# Define tools for AI agent
tools = [
    Tool(
        name="ServoControl",
        func=control_servo,
        description="Moves the servo motor. Provide an angle (0-180) or a range (e.g., '30 to 180')."
    )
]

# Initialize AI Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="ZERO_SHOT_REACT_DESCRIPTION",
    verbose=False  # Set to True for debugging
)

# Continuous chatbot interaction
print("\n🤖 AI Servo Chatbot Started! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() in ["exit", "quit", "stop"]:
        print("👋 Goodbye!")
        break

    # Check for numeric input and move the servo
    if re.search(r"\d+", user_input):  
        response = control_servo(user_input)
    else:
        response = agent.run(user_input)  # AI handles general queries
    
    print(f"🤖 AI: {response}")
