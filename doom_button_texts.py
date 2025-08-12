#!/usr/bin/env python3
"""Collection of authentic 90s DOOM button texts for the launcher."""

# Evil 90s DOOM button text options
DOOM_BUTTON_TEXTS = [
    "*** UNLEASH HELL ***",
    ">> RIP AND TEAR <<",
    "=== DEMONS AWAIT ===",
    ">>> ENTER THE FRAY <<<",
    "*** SHOTGUN LOADED ***",
    "=== HELL ON EARTH ===",
    ">> DOOM AWAITS <<",
    "*** KILL THEM ALL ***",
    "=== MARINE READY ===",
    ">>> BLAST DEMONS <<<",
    "*** CHAINSAW TIME ***",
    "=== MARS NEEDS YOU ===",
    ">> HELL'S ARMY <<",
    "*** DOUBLE BARREL ***",
    "=== PHOBOS CALLS ===",
    ">>> DEIMOS RISING <<<",
    "*** CYBERDEMON ***",
    "=== SPIDER DEMON ===",
    ">> BARON OF HELL <<",
    "*** CACODEMON ***"
]

# Classic DOOM level names that could be used
DOOM_LEVEL_TEXTS = [
    "E1M1: HANGAR",
    "E1M2: NUCLEAR PLANT", 
    "E1M3: TOXIN REFINERY",
    "E1M4: COMMAND CONTROL",
    "E1M5: PHOBOS LAB",
    "E1M6: CENTRAL PROCESSING",
    "E1M7: COMPUTER STATION",
    "E1M8: PHOBOS ANOMALY",
    "E1M9: MILITARY BASE"
]

# 90s style warning messages
DOOM_WARNINGS = [
    "WARNING: DEMONS DETECTED",
    "ALERT: HELL BREACH IMMINENT", 
    "CAUTION: MARINE DEPLOYMENT",
    "DANGER: SHOTGUN REQUIRED",
    "NOTICE: CHAINSAW RECOMMENDED"
]

def get_random_doom_text():
    """Get a random evil DOOM button text."""
    import random
    return random.choice(DOOM_BUTTON_TEXTS)

def get_doom_level_text():
    """Get a random DOOM level reference."""
    import random
    return random.choice(DOOM_LEVEL_TEXTS)

def get_doom_warning():
    """Get a random DOOM warning message."""
    import random
    return random.choice(DOOM_WARNINGS)

if __name__ == '__main__':
    print("💀 AUTHENTIC 90s DOOM BUTTON TEXTS 💀")
    print("=" * 40)
    print("\n🔥 Evil Button Texts:")
    for i, text in enumerate(DOOM_BUTTON_TEXTS[:10], 1):
        print(f"  {i:2d}. {text}")
    
    print(f"\n... and {len(DOOM_BUTTON_TEXTS) - 10} more!")
    
    print("\n🎮 Level References:")
    for text in DOOM_LEVEL_TEXTS[:5]:
        print(f"     {text}")
    
    print("\n⚠️  Warning Messages:")
    for text in DOOM_WARNINGS:
        print(f"     {text}")
    
    print(f"\n🎲 Random selection: {get_random_doom_text()}")