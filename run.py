"""
KinGuard: Alexa+ & Ring Cognitive Care Ambient Protocol.
Amazon Developer Hackathon (Build, Ship, Shape 2026)
Primary Track: Alexa+ (MCP Server & Agent Skill)
Mini Challenges: AWS Builder (Bedrock & SNS) & Open Source
"""

import os
import sys
import uvicorn

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    print("==================================================================")
    print("  KinGuard: Alexa+ & Ring Cognitive Care Ambient Protocol")
    print("  Amazon Developer Hackathon (Build, Ship, Shape 2026)")
    print("==================================================================")
    print("  [x] Alexa+ MCP Streamable HTTP / SSE: http://127.0.0.1:8080/mcp")
    print("  [x] Interactive Web Simulator:        http://127.0.0.1:8080/")
    print("  [x] Amazon Bedrock Cognitive Engine:  ONLINE (Claude 3.5 Sonnet)")
    print("  [x] Amazon SNS Caregiver Bridge:      ACTIVE")
    print("==================================================================")
    uvicorn.run("simulator.simulator_server:app", host="127.0.0.1", port=8080, reload=False)
