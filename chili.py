#!/usr/bin/env python3

import requests
import json
import os
import sys
import shutil
import textwrap
from datetime import datetime
import readline
import signal

# API Keys - Replace these with your actual API keys
OPENROUTER_API_KEY = ""
OPENAI_API_KEY = ""

# Add this line to allow users to set their initial credit balance
INITIAL_CREDITS = 10.00  # Default value, can be changed by the user

# API endpoints
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_BALANCE_URL = "https://openrouter.ai/api/v1/auth/key"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

# Available models
OPENROUTER_MODELS = {
    '1': "openai/gpt-3.5-turbo",
    '2': "openai/gpt-4",
    '3': "anthropic/claude-2",
    '4': "google/palm-2-chat-bison",
    '5': "meta-llama/llama-2-70b-chat"
}

OPENAI_MODELS = {
    '1': "gpt-3.5-turbo",
    '2': "gpt-4"
}

# Profiles
PROFILES = {
    '1': {
        'name': 'Linux Expert',
        'model': 'openai/gpt-4',
        'system_message': "You are an expert in Linux. Your job is to teach Linux commands. Reply concisely and accurately."
    },
    '2': {
        'name': 'Python Programmer',
        'model': 'openai/gpt-4',
        'system_message': "You are a Python programming expert. Provide code examples and explanations for Python-related questions."
    },
    # Add more profiles as needed
}

# Command mappings
COMMANDS = {
    'help': ['help', '-h'],
    'exit': ['exit', '-e'],
    'clear': ['clear', '-c'],
    'new': ['new', '-n'],
    'change': ['change', '-m'],  # 'm' for model
    'usage': ['usage', '-u'],
    'balance': ['balance', '-b'],
    'save': ['save', '-s'],
    'fork': ['fork', '-f'],
    'return': ['return', '-r']
}

# Usage tracking
OPENROUTER_USAGE = 0

# Global variable for terminal width
TERMINAL_WIDTH = shutil.get_terminal_size().columns - 4

def handle_resize(signum, frame):
    global TERMINAL_WIDTH
    TERMINAL_WIDTH = shutil.get_terminal_size().columns - 4

def clear_screen():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

def print_bordered(text, width=None):
    if width is None:
        width = TERMINAL_WIDTH
    print("  ┌" + "─" * (width - 2) + "┐")
    for line in text.split('\n'):
        print(f"  │ {line:<{width-4}} │")
    print("  └" + "─" * (width - 2) + "┘")

def print_wrapped(text, width=None):
    if width is None:
        width = TERMINAL_WIDTH
    for line in text.split('\n'):
        wrapped = textwrap.wrap(line, width=width-4)
        for wrapped_line in wrapped:
            print(f"  {wrapped_line}")

def get_available_models():
    models = {}
    if OPENROUTER_API_KEY != "":
        models.update({str(i): f"OpenRouter: {model}" for i, model in enumerate(OPENROUTER_MODELS.values(), 1)})
    if OPENAI_API_KEY != "":
        start = len(models) + 1
        models.update({str(i): f"OpenAI: {model}" for i, model in enumerate(OPENAI_MODELS.values(), start)})
    return models

def select_model_and_profile(available_models):
    while True:
        print("\n  ┌" + "─" * (TERMINAL_WIDTH - 2) + "┐")
        print("  │ Available models and profiles:".ljust(TERMINAL_WIDTH + 1) + "│")
        for key, model in available_models.items():
            print(f"  │ {key}. {model}".ljust(TERMINAL_WIDTH + 1) + "│")
        print("  │".ljust(TERMINAL_WIDTH + 1) + "│")
        for key, profile in PROFILES.items():
            print(f"  │ P{key}. {profile['name']} ({profile['model']})".ljust(TERMINAL_WIDTH + 1) + "│")
        print("  └" + "─" * (TERMINAL_WIDTH - 2) + "┘")
        choice = input("  Select a model or profile (enter the number or P+number for profile): ")
        if choice in available_models:
            return available_models[choice], None
        elif choice.startswith('P') and choice[1:] in PROFILES:
            profile = PROFILES[choice[1:]]
            return profile['model'], profile['system_message']
        print("  Invalid choice. Please try again.")

def send_message(messages, model, available_models):
    global OPENROUTER_USAGE
    if ": " in model:
        provider, model_name = model.split(": ")
    else:
        provider = "OpenRouter" if model.startswith("openai/") else "OpenAI"
        model_name = model

    api_key = OPENROUTER_API_KEY if provider == "OpenRouter" else OPENAI_API_KEY
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": messages
    }
    url = OPENROUTER_CHAT_URL if provider == "OpenRouter" else OPENAI_CHAT_URL
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        # Update usage for OpenRouter only
        if provider == "OpenRouter":
            OPENROUTER_USAGE += response_data['usage']['total_tokens'] * 0.000001  # Assuming $0.000001 per token
        return content
    else:
        return f"Error: {response.status_code} - {response.text}"

def check_credits():
    openrouter_usage = None
    if OPENROUTER_API_KEY != "":
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(OPENROUTER_BALANCE_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'usage' in data['data']:
                openrouter_usage = data['data']['usage']
    return {
        "openrouter": openrouter_usage or OPENROUTER_USAGE
    }

def get_balance(initial_credits, model):
    usage = check_credits()
    if model.startswith("OpenRouter:"):
        balance = initial_credits - usage["openrouter"]
        return f"${balance:.2f}"
    else:
        return "OpenAI does not provide balance information via the API."

def print_help():
    help_message = "Available commands:\n"
    for cmd, aliases in COMMANDS.items():
        help_message += f"- '{aliases[0]}' or '{aliases[1]}': {cmd.capitalize()}\n"
    help_message = help_message.strip()
    print_bordered(help_message)

def save_conversation(conversation, model):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(f"Conversation using model: {model}\n")
        f.write(f"Saved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for message in conversation:
            role = message['role'].capitalize()
            content = message['content']
            f.write(f"{role}: {content}\n")
    return filename

def print_conversation_structure(conversation_stack, current_conversation):
    print("Conversation structure:")
    for i, fork in enumerate(conversation_stack):
        print(f"  Fork {i+1}: {len(fork)} messages")
    print(f"  Current: {len(current_conversation)} messages")

def main():
    signal.signal(signal.SIGWINCH, handle_resize)
    clear_screen()
    welcome_message = (
        "Welcome to CHILI.PY. Copyright (c) (2024) Steven Kettell.\n"
        "This is free software: you can redistribute and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.\n"
        "Type 'help' or '-h' to see available commands."
    )
    print_bordered(welcome_message)

    available_models = get_available_models()
    if not available_models:
        print_bordered("No valid API keys found. Please add your API key(s) to the script.")
        return

    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "":
        usage = check_credits()
        if usage["openrouter"] is not None:
            balance = INITIAL_CREDITS - usage["openrouter"]
            print_bordered(f"Your current OpenRouter balance: ${balance:.2f}")
        else:
            print_bordered("Unable to fetch OpenRouter credit usage")

    model, system_message = select_model_and_profile(available_models)
    print_bordered(f"Selected model: {model}")
    if system_message:
        print_bordered(f"Selected profile: {system_message}")
        conversation = [{"role": "system", "content": system_message}]
    else:
        conversation = []

    conversation_stack = []

    while True:
        print(f"\n  {'You:'.ljust(TERMINAL_WIDTH)}")
        user_input = input("  ")
        if user_input.lower() in COMMANDS['change']:
            model, system_message = select_model_and_profile(available_models)
            print_bordered(f"Model changed to: {model}")
            if system_message:
                print_bordered(f"Selected profile: {system_message}")
                conversation = [{"role": "system", "content": system_message}]
            else:
                conversation = []
        elif user_input.lower() in COMMANDS['exit']:
            print_bordered("Goodbye!")
            break
        elif user_input.lower() in COMMANDS['help']:
            print_help()
        elif user_input.lower() in COMMANDS['clear']:
            clear_screen()
        elif user_input.lower() in COMMANDS['new']:
            conversation = []
            conversation_stack = []
            clear_screen()
            print_bordered("Starting a new conversation.")
        elif user_input.lower() in COMMANDS['usage']:
            if model.startswith("OpenRouter:"):
                usage = check_credits()
                print_bordered(f"Your current OpenRouter credit usage: ${usage['openrouter']:.2f}")
            else:
                print_bordered("OpenAI does not provide usage figures via the API.")
        elif user_input.lower() in COMMANDS['balance']:
            if model.startswith("OpenRouter:"):
                balance = get_balance(INITIAL_CREDITS, model)
                print_bordered(f"Your current OpenRouter balance: {balance}")
            else:
                print_bordered("OpenAI does not provide balance information via the API.")
        elif user_input.lower() in COMMANDS['save']:
            if conversation:
                filename = save_conversation(conversation, model)
                print_bordered(f"Conversation saved to {filename}")
            else:
                print_bordered("No conversation to save.")
        elif user_input.lower() in COMMANDS['fork']:
            conversation_stack.append(conversation.copy())
            print_bordered("Conversation forked. You can return to this point later.")
            print_conversation_structure(conversation_stack, conversation)
        elif user_input.lower() in COMMANDS['return']:
            if conversation_stack:
                conversation = conversation_stack.pop()
                print_bordered("Returned to previous fork point.")
                print_conversation_structure(conversation_stack, conversation)
            else:
                print_bordered("No previous fork point to return to.")
        else:
            conversation.append({"role": "user", "content": user_input})
            response = send_message(conversation, model, available_models)
            print("\n  AI:")
            print_wrapped(response)
            conversation.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

