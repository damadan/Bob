import argparse, sys
from .agent import build_agent

def main():
    p = argparse.ArgumentParser(description="AEC Agent CLI")
    p.add_argument("--prompt", default="Сделай смету из resource://project/demo/files/spec.pdf и отдай PDF")
    args = p.parse_args()
    agent = build_agent()
    print(agent.run(args.prompt))

if __name__ == "__main__":
    main()
