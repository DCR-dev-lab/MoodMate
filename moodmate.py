import json
from datetime import datetime, timedelta
from random import sample, choice
import time
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
import sys
from typing import List, Dict, Optional, Tuple
import csv

# ======================
# 🎨 UI Configuration
# ======================
COLORS = {
    "header": "\033[95m",   # Magenta for main headers
    "menu": "\033[94m",     # Blue for menu options
    "input": "\033[96m",    # Cyan for input prompts
    "warning": "\033[93m",  # Yellow for warnings/cancellations
    "success": "\033[92m",  # Green for success messages
    "reset": "\033[0m"      # Reset to default
}

BANNER = f"""
{COLORS['header']}
╔════════════════════════════╗
║           MOODMATE         ║
║     Your Emotional Guide   ║
╚════════════════════════════╝
{COLORS['reset']}
"""

EMOJI_MAP = {
    "happy": "😊", "tired": "😴", "bored": "😐",
    "anxious": "😟", "motivated": "💪", "sad": "😢",
    "stressed": "😤", "overwhelmed": "😵", "confused": "🤔",
    "inspired": "💡"
}

ENCOURAGING_REACTIONS = {
    "happy": "Keep the good vibes rolling! 🌈",
    "sad": "Sending you a virtual hug 🤗. It's okay to feel this way.",
    "anxious": "Breathe in... breathe out. You’re doing great 💖. Take it one moment at a time.",
    "motivated": "Go get 'em, tiger! 🐯 The world awaits your brilliance!",
    "bored": "Let’s spark some curiosity 🔍! There's a whole world to explore.",
    "tired": "Rest is productive too 😌. Recharge yourself, you deserve it.",
    "stressed": "Take a deep breath. You're stronger than you think! 💪",
    "overwhelmed": "One step at a time. Break it down, you got this! ✨",
    "confused": "It's okay to not know everything. Let's find some clarity together! 🧭",
    "inspired": "Oh, the possibilities! Chase that amazing idea! 🌟"
}

# ======================
# 📦 Data Configuration
# ======================
LOG_FILE = "moodmate_log.json"
BACKUP_FILE = "moodmate_backup.json"
MAX_LOG_ENTRIES = 1000  # Prevent log file from growing indefinitely
EXPORT_FOLDER = "moodmate_exports"

# Enhanced Mood Dictionary with categorized tasks
MOOD_TASKS = {
    "happy": {
        "energize": [
            "Go for a brisk walk outdoors and enjoy the weather, perhaps discovering a new path.",
            "Listen to your favorite upbeat music and sing along loudly, feeling the rhythm.",
            "Plan a fun, low-key activity for later today or this week, like a movie night or picnic.",
            "Do a quick burst of physical activity like dancing, jumping jacks, or a short jog.",
            "Engage in a favorite sport or physical game.",
            "Take on a new small challenge that excites you.",
            "Spend time in natural sunlight.",
            "Organize a playlist of songs that make you feel good."
        ],
        "connect": [
            "Call or text a friend or family member just to say hello and share positive news.",
            "Send a thoughtful message to someone you appreciate, expressing your gratitude.",
            "Share a positive update or a funny anecdote with a loved one.",
            "Offer a small, genuine compliment to someone you interact with today.",
            "Plan a virtual coffee break with a distant friend.",
            "Help a neighbor with a small task.",
            "Write a thank-you note to someone who made your day.",
            "Join a social club or group that aligns with your interests."
        ],
        "create_and_grow": [
            "Start a new small creative project you've been wanting to try, like a sketch or a craft.",
            "Brainstorm new ideas for a personal goal, hobby, or even a community initiative.",
            "Learn a new interesting fact or skill online, like a simple magic trick or a basic coding command.",
            "Organize an area of your space that brings you joy, making it more aesthetically pleasing.",
            "Work on a passion project that aligns with your interests.",
            "Explore a new app or tool that enhances productivity or creativity.",
            "Read an inspiring biography or success story.",
            "Set a new personal best in a hobby or activity."
        ]
    },
    "tired": {
        "recharge_mind": [
            "Take a short, restful power nap (20-30 minutes) in a quiet, dark room.",
            "Listen to a calming audiobook or a gentle, non-demanding podcast.",
            "Do a quick guided meditation for relaxation, focusing on your breath.",
            "Close your eyes and practice deep breathing for a few minutes, counting your breaths.",
            "Rest your eyes by looking out a window at something distant.",
            "Avoid screen time for 15-30 minutes.",
            "Practice mindful breathing exercises.",
            "Do a brief body scan to identify tension."
        ],
        "restore_body": [
            "Drink a full glass of water and rest in a comfortable position.",
            "Do some gentle stretching or light, restorative yoga poses.",
            "Take a warm, comforting shower or bath with soothing scents.",
            "Prepare a simple, nutritious snack like fruit or nuts.",
            "Give yourself a gentle hand or foot massage.",
            "Lie down with your legs elevated against a wall.",
            "Apply a soothing eye mask.",
            "Wear comfortable, loose clothing."
        ],
        "light_engagement": [
            "Do light reading from a non-demanding book or magazine, or browse a light article online.",
            "Look at calming images or watch a slow-paced nature video on mute.",
            "Sit quietly and observe your surroundings without judgment or analysis.",
            "Listen to instrumental or ambient music that promotes relaxation.",
            "Do a very simple, repetitive task like folding laundry or tidying a drawer.",
            "Journal a few unedited thoughts or feelings.",
            "Sit outside and listen to the sounds of nature.",
            "Watch clouds or observe simple natural patterns."
        ]
    },
    "bored": {
        "stimulate_mind": [
            "Explore a random topic on Wikipedia or an educational website like Khan Academy.",
            "Watch an educational YouTube video or a short documentary on a new subject.",
            "Try a new online puzzle game or brain teaser, like Sudoku or a logic puzzle.",
            "Learn a few new words in a language you're interested in using a flashcard app.",
            "Research a niche topic you've always wondered about.",
            "Listen to a podcast about an unusual subject.",
            "Do a quick online course on a skill you'd like to learn.",
            "Read a compelling non-fiction article or essay."
        ],
        "engage_creativity": [
            "Doodle, sketch, or color in a coloring book, experimenting with colors.",
            "Write a short journal entry about anything that comes to mind, a dream, or a hypothetical scenario.",
            "Organize a digital folder or clean up your desktop files, making it more efficient.",
            "Plan a hypothetical trip or event, researching destinations, activities, and budget.",
            "Start a collection of interesting facts or quotes.",
            "Design a simple graphic or logo for a fictional company.",
            "Try a simple craft project like origami or making a paper airplane.",
            "Brainstorm ideas for a fictional story or character."
        ],
        "explore_new": [
            "Discover a new music artist or genre you've never listened to before, and create a playlist.",
            "Browse an online store for interesting new products or ideas (no pressure to buy anything).",
            "Try a simple new recipe or mix a new non-alcoholic drink or smoothie.",
            "Walk a different route than usual if you go outside, observing new details.",
            "Explore a virtual museum or art gallery online.",
            "Do an online quiz about a random, fun topic.",
            "Try a new physical activity for a short period, like juggling or stretching differently.",
            "Browse through a cookbook for inspiration."
        ]
    },
    "anxious": {
        "grounding": [
            "Focus on your breath: inhale slowly for 4, hold for 4, exhale for 6, repeating several times.",
            "Use the '5-4-3-2-1' technique: name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.",
            "Hold an ice cube in your hand until it melts, focusing on the cold sensation.",
            "Press your feet firmly into the ground and notice the sensation, feeling connected to the earth.",
            "Splash cold water on your face or wrists to reset your system.",
            "Gently massage your temples or neck.",
            "Focus on a repetitive action, like snapping your fingers.",
            "Identify and name objects of a specific color around you."
        ],
        "soothe": [
            "Listen to calming nature sounds (rain, ocean waves) or soft, instrumental music.",
            "Drink a warm cup of herbal tea slowly and mindfully, noticing its warmth and flavor.",
            "Take a slow, gentle walk in a quiet area, paying attention to your steps.",
            "Light a calming scented candle or use an essential oil diffuser with lavender.",
            "Wrap yourself in a cozy blanket and feel its comfort.",
            "Do a guided meditation focused on releasing tension.",
            "Practice mindful eating with a small snack, noticing textures and flavors.",
            "Look at comforting pictures or photos."
        ],
        "process": [
            "Write down all your worries and thoughts in a journal, then close it and put it away.",
            "Talk to a trusted friend or family member about how you're feeling, without seeking solutions.",
            "Do a quick, repetitive task like tidying a small area of your room or desk.",
            "Allow yourself to feel the emotion without judgment, reminding yourself that it will pass.",
            "Visualize a safe and peaceful place in your mind.",
            "Challenge one anxious thought and find evidence against it.",
            "Do a simple, distracting puzzle or word game.",
            "Listen to a podcast that diverts your attention."
        ]
    },
    "motivated": {
        "productivity_boost": [
            "Start the most important task on your list, even if it's just for 15 minutes to build momentum.",
            "Break down a large project into its absolute smallest, actionable steps, and tackle one.",
            "Organize your workspace for optimal efficiency, decluttering distractions.",
            "Review your goals and select one to make immediate, tangible progress on.",
            "Block out specific time slots for focused work.",
            "Use the Pomodoro technique to maintain focus.",
            "Complete a quick, easy task to build confidence.",
            "Set a challenging but achievable deadline for a small task."
        ],
        "plan_and_strategize": [
            "Create a detailed plan for an upcoming assignment or project, outlining all stages.",
            "Set new, challenging but achievable goals for yourself for the next week or month.",
            "Research advanced topics related to your interests or academic field.",
            "Update your resume or professional portfolio with your latest achievements.",
            "Create a visual timeline for a long-term goal.",
            "Brainstorm potential challenges and proactive solutions.",
            "Review successful strategies you've used in the past.",
            "Outline key steps for a new skill acquisition."
        ],
        "skill_development": [
            "Learn a new complex concept by breaking it down and explaining it aloud to yourself.",
            "Practice a specific skill you want to improve, setting a clear objective.",
            "Watch an in-depth tutorial or webinar to enhance your knowledge in a specific area.",
            "Seek out resources (books, articles, experts) to deepen your understanding of a topic.",
            "Take a short online course related to your field.",
            "Apply a new technique you've learned in your work.",
            "Teach a concept to someone else to solidify your understanding.",
            "Engage in deliberate practice for a specific skill."
        ]
    },
    "sad": {
        "comfort_and_care": [
            "Listen to calm, soothing music that brings you peace and allows for quiet reflection.",
            "Wrap yourself in a cozy blanket and allow yourself to simply rest and feel the emotions.",
            "Prepare a warm, favorite comforting meal or bake something simple and aromatic.",
            "Watch an uplifting or heartwarming movie or show that offers a sense of solace.",
            "Drink a warm beverage like hot chocolate or herbal tea.",
            "Light a comforting candle and enjoy its glow.",
            "Take a warm bath with Epsom salts.",
            "Wear your most comfortable clothes."
        ],
        "gentle_connection": [
            "Call or text a trusted loved one for a supportive chat, even if it's just to listen.",
            "Spend time with a pet, enjoying their unconditional affection and calming presence.",
            "Look at old photos that bring back happy memories and cherished connections.",
            "Do a small, kind act for yourself, like enjoying a favorite snack or a small treat.",
            "Send a loving text to someone you care about.",
            "Have a comforting conversation with someone who understands.",
            "Spend time in a quiet, familiar place with someone you trust.",
            "Watch an old comfort movie with a loved one."
        ],
        "creative_release": [
            "Write a positive diary entry, focusing on good memories, things you're grateful for, or future hopes.",
            "Draw, paint, or doodle freely, without pressure for perfection or specific outcome.",
            "Listen to a guided meditation focused on self-compassion and acceptance.",
            "Take a break from social media to avoid comparisons or overwhelming content.",
            "Listen to music that allows you to process your emotions.",
            "Journal about your feelings without censoring yourself.",
            "Write a short, reflective poem or piece of prose.",
            "Engage in a simple craft like knitting or coloring."
        ]
    },
    "stressed": {
        "physical_release": [
            "Go for a brisk walk or jog outdoors to clear your head and burn off excess energy.",
            "Squeeze a stress ball or clench and release your fists several times.",
            "Do some quick stretches or light exercise like push-ups or squats.",
            "Put on some energetic music and dance it out for a few minutes.",
            "Do some vigorous cleaning or organizing to channel energy.",
            "Take a few minutes to jump rope or do jumping jacks.",
            "Engage in a short burst of cardio.",
            "Do a series of progressive muscle relaxations."
        ],
        "mental_unload": [
            "Write down all your worries and concerns on a 'brain dump' list to get them out of your head.",
            "Prioritize your tasks and identify the single most critical one to focus on.",
            "Take 5 minutes to plan out the next hour of your day, making it manageable.",
            "Practice a quick mindfulness exercise for 2-3 minutes, focusing on sounds or sights.",
            "Do a quick review of your schedule to identify and eliminate any unnecessary commitments.",
            "Break down a daunting task into tiny, manageable steps.",
            "Use the 'two-minute rule' for quick tasks.",
            "Visualize success in a difficult situation."
        ],
        "mini_break": [
            "Step away from your work area and look out a window, observing the outside world.",
            "Listen to a short, calming audio track or a favorite song.",
            "Have a healthy snack and a full glass of water, focusing on hydrating.",
            "Do a few deep belly breaths to activate your parasympathetic nervous system.",
            "Look at something beautiful or pleasant for a few moments, like a plant or artwork.",
            "Do a quick crossword puzzle or sudoku.",
            "Stand up and stretch for 5 minutes.",
            "Walk to another room and back."
        ]
    },
    "overwhelmed": {
        "simplify": [
            "Write down absolutely everything on your mind, then categorize or group similar items.",
            "Choose only the top 1-3 most important tasks to focus on right now, deferring others.",
            "Break down a large, daunting task into its absolute smallest, actionable steps.",
            "Eliminate anything from your list that isn't truly essential or urgent, or postpone it.",
            "Create an 'ignore list' for things you actively choose not to worry about for now.",
            "Automate any repetitive tasks if possible.",
            "Cancel or reschedule non-essential commitments.",
            "Focus on completing just one small thing."
        ],
        "structure": [
            "Create a very detailed, step-by-step plan for just one specific task.",
            "Set a timer for 15-20 minutes and work on one thing without distractions, then take a break.",
            "Organize a small physical or digital workspace area to bring a sense of order.",
            "Review your calendar and reschedule any non-urgent commitments to free up mental space.",
            "Use a project management tool or app to visually organize your tasks.",
            "Create a 'done' list to see your progress.",
            "Color-code your tasks or notes for better visual organization.",
            "Set a clear start and end time for your work."
        ],
        "seek_support": [
            "Talk to a mentor, supervisor, or trusted friend about your workload and feelings.",
            "Ask a friend or colleague for help with a specific task, explaining what you need.",
            "Communicate your boundaries or needs to others clearly and kindly.",
            "Take a quick break to connect with someone for emotional support and a different perspective.",
            "Delegate tasks if you have the option.",
            "Consider professional support if feelings persist.",
            "Look for online resources or communities for similar experiences.",
            "Share your workload concerns with a peer."
        ]
    },
    "confused": {
        "clarify_information": [
            "Re-read the instructions or material slowly, focusing on each sentence and key terms.",
            "Look up unfamiliar terms or concepts immediately using a reliable dictionary or search engine.",
            "Break the confusing problem down into smaller, simpler components to understand each piece.",
            "Try to explain the concept aloud to yourself as if teaching someone else, identifying gaps in understanding.",
            "Highlight or underline key phrases in the confusing text.",
            "Draw a diagram or flowchart to visualize the information.",
            "Summarize the information in your own words.",
            "Search for different explanations or analogies online."
        ],
        "seek_external_help": [
            "Ask a specific, well-articulated question to a teacher, peer, or online forum.",
            "Review examples or case studies related to the confusing topic to see application.",
            "Watch an explanatory video or tutorial on the subject from a different source.",
            "Consult a different textbook or resource for an alternative explanation or perspective.",
            "Schedule a short meeting with an expert or peer for clarification.",
            "Collaborate with a classmate on the confusing material.",
            "Use a Q&A platform to pose your specific question.",
            "Find a study group to discuss the topic."
        ],
        "mental_reset": [
            "Take a short break (5-10 minutes) to clear your mind completely before returning.",
            "Do a quick, unrelated mental exercise like a simple puzzle or brain teaser.",
            "Drink water and do some light physical stretches to refresh your body and mind.",
            "Return to the problem with fresh eyes after stepping away, often seeing new insights.",
            "Listen to calming music that doesn't distract you.",
            "Close your eyes and breathe deeply for a minute.",
            "Change your study location for a fresh perspective.",
            "Do something completely different for 15 minutes."
        ]
    },
    "inspired": {
        "capture_and_develop": [
            "Immediately write down all your thoughts and ideas, no matter how wild or unformed.",
            "Create a mind map or concept web to connect different aspects of your inspiration visually.",
            "Record a voice memo describing your ideas in detail, allowing for free flow.",
            "Sketch out rough visuals or diagrams if the inspiration is visual, capturing the essence.",
            "Start a dedicated 'inspiration' journal or digital note file.",
            "Collect images or sounds that resonate with your idea.",
            "Freewrite about the implications of your inspiration.",
            "Create a mood board for the idea."
        ],
        "take_action": [
            "Start a small, actionable step towards realizing your inspired idea, like basic research or an outline.",
            "Conduct preliminary research on components needed to bring your idea to life.",
            "Share your idea with someone who can offer constructive feedback or excitement.",
            "Block out dedicated time in your schedule to work on this new inspiration.",
            "Create a simple prototype or mock-up.",
            "Identify the first three steps to move forward.",
            "Set a mini-deadline for the initial phase.",
            "Reach out to someone who could help you develop the idea."
        ],
        "nurture_flow": [
            "Listen to music that enhances your creative flow or concentration.",
            "Visit a place that stimulates your imagination (e.g., museum, park, unique store, art exhibition).",
            "Read about others who have pursued similar inspirations or creative paths.",
            "Keep an 'inspiration' journal where you regularly collect new ideas and observations.",
            "Engage in freeform brainstorming sessions.",
            "Allow for periods of unstructured thinking.",
            "Surround yourself with aesthetically pleasing or stimulating objects.",
            "Take a nature walk to observe patterns and details."
        ]
    }
}



# ======================
# 🛠️ Core Classes
# ======================
class MoodLogger:
    """Handles all mood logging operations, ensuring file integrity and data management."""

    def __init__(self, log_file: str = LOG_FILE):
        self.log_file = log_file
        self._ensure_files()

    def _ensure_files(self) -> None:
        """Ensures the log file and export folder exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(EXPORT_FOLDER):
            os.makedirs(EXPORT_FOLDER)

    def log_mood(self, mood: str, task: str, note: Optional[str] = None) -> None:
        """Records a new mood entry with a timestamp, mood, task, and optional note."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "mood": mood,
            "task": task,
            "note": note,
            "completed": False # New field to track if the task was completed
        }
        
        with open(self.log_file, 'r+') as f:
            logs = json.load(f)
            logs.append(entry)
            
            # Keep log file from growing indefinitely
            if len(logs) > MAX_LOG_ENTRIES:
                logs = logs[-MAX_LOG_ENTRIES:]
            
            f.seek(0) # Rewind to the beginning of the file
            json.dump(logs, f, indent=2)
            f.truncate() # Remove remaining part
        
        print(f"\n{COLORS['success']}✅ Awesome! Your mood and task have been recorded.{COLORS['reset']}")

    def quick_log(self, mood: str) -> None:
        """Quickly logs a mood with a randomly selected task."""
        if mood not in MOOD_TASKS:
            print(f"{COLORS['warning']}⚠️ Hmm, I don't recognize that mood. Please try again.{COLORS['reset']}")
            return
        
        all_tasks = []
        for category in MOOD_TASKS[mood].values():
            all_tasks.extend(category)
        
        if not all_tasks:
            print(f"{COLORS['warning']}⚠️ No tasks found for '{mood}'. Let's pick something else.{COLORS['reset']}")
            return
        
        random_task = choice(all_tasks)
        self.log_mood(mood, random_task)
        print(f"\n✨ Mood captured! {mood.capitalize()} {EMOJI_MAP.get(mood, '')} | 🌟 Task: {random_task}")

    def get_recent_moods(self, days: int = 7) -> List[Dict]:
        """Retrieves mood entries from the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        return [
            entry for entry in logs
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff
        ]
    
    def get_all_logs(self) -> List[Dict]:
        """Retrieves all mood log entries."""
        with open(self.log_file, 'r') as f:
            return json.load(f)

    def get_mood_stats(self) -> Dict:
        """Calculates and returns statistics about logged moods."""
        logs = self.get_all_logs()
        
        stats = {
            "total": len(logs),
            "by_mood": defaultdict(int),
            "by_day": defaultdict(int),
            "completion_rate": 0,
            "notes_count": 0
        }
        
        completed = 0
        for entry in logs:
            stats["by_mood"][entry["mood"]] += 1
            date = datetime.fromisoformat(entry["timestamp"]).date()
            stats["by_day"][date] += 1
            if entry.get("completed", False):
                completed += 1
            if entry.get("note"):
                stats["notes_count"] += 1
        
        if logs:
            stats["completion_rate"] = (completed / len(logs)) * 100
        
        return stats
    
    def edit_entry(self, index: int, **changes) -> bool:
        """Edits a specific log entry by its index."""
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f)
                if 0 <= index < len(logs):
                    logs[index].update(changes)
                    f.seek(0)
                    json.dump(logs, f, indent=2)
                    f.truncate()
                    return True
                return False # Index out of bounds
        except Exception as e:
            print(f"{COLORS['warning']}⚠️ Error updating entry: {e}{COLORS['reset']}")
            return False

    def delete_entry(self, index: int) -> bool:
        """Deletes a specific log entry by its index."""
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f)
                if 0 <= index < len(logs):
                    deleted_entry = logs.pop(index)
                    f.seek(0)
                    json.dump(logs, f, indent=2)
                    f.truncate()
                    print(f"{COLORS['success']}🗑️ Deleted: {deleted_entry['mood'].title()} on {datetime.fromisoformat(deleted_entry['timestamp']).strftime('%Y-%m-%d %H:%M')}{COLORS['reset']}")
                    return True
                return False # Index out of bounds
        except Exception as e:
            print(f"{COLORS['warning']}⚠️ Error deleting entry: {e}{COLORS['reset']}")
            return False

    def mark_all_pending_as_completed(self) -> int:
        """Marks all currently pending tasks as completed."""
        updated_count = 0
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f)
                for entry in logs:
                    if not entry.get("completed", False):
                        entry["completed"] = True
                        updated_count += 1
                f.seek(0)
                json.dump(logs, f, indent=2)
                f.truncate()
            return updated_count
        except Exception as e:
            print(f"{COLORS['warning']}⚠️ Error marking all tasks completed: {e}{COLORS['reset']}")
            return 0


    def export_data(self, format: str = "json") -> str:
        """Exports all logged data to a JSON or CSV file."""
        logs = self.get_all_logs()
        
        if not logs:
            raise Exception("No data to export!")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(EXPORT_FOLDER, f"moodmate_export_{timestamp}.{format}")
        
        if format == "csv":
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
        else: # default to json
            with open(filename, 'w') as f:
                json.dump(logs, f, indent=2)
        
        return filename

class PomodoroTimer:
    """Manages Pomodoro timer sessions with visual feedback and notifications."""
    
    def __init__(self):
        self.work_sessions = 0 # To track completed sessions

    def run(self, work_min: int, break_min: int, cycles: int = 1) -> None:
        """Runs the Pomodoro timer for the specified work, break, and cycles."""
        if work_min <= 0 or break_min <= 0 or cycles <= 0:
            print(f"{COLORS['warning']}⚠️ Timer values must be positive. Please try again.{COLORS['reset']}")
            return

        try:
            for cycle in range(1, cycles + 1):
                print(f"\n{COLORS['header']}🍅 Cycle {cycle}/{cycles}{COLORS['reset']}")
                
                self._run_phase("FOCUS", work_min, "⏳", "success")
                self.work_sessions += 1 # Increment work sessions after each focus block

                if cycle < cycles: # Don't break after the last cycle
                    self._run_phase("BREAK", break_min, "☕", "menu")
                    
                    # Suggest a quick stretch every 2 cycles
                    if self.work_sessions % 2 == 0:
                        print(f"\n{COLORS['input']}💡 Quick tip: Take a moment to stretch and rest your eyes before the next cycle!{COLORS['reset']}")

            print(f"\n{COLORS['success']}🎉 All Pomodoro cycles complete! Great work!{COLORS['reset']}")
        except KeyboardInterrupt:
            print(f"\n{COLORS['warning']}Timer interrupted. You can resume anytime!{COLORS['reset']}")
        except Exception as e:
            print(f"{COLORS['warning']}⚠️ An error occurred with the timer: {e}{COLORS['reset']}")

    def _run_phase(self, name: str, minutes: int, icon: str, color_key: str) -> None:
        """Helper to run a single work or break phase."""
        color_code = COLORS.get(color_key, COLORS['reset'])
        print(f"\n{color_code}{icon} {name} time for {minutes} minutes...{COLORS['reset']}")
        self._countdown(minutes * 60)
        print(f"{color_code}✅ Done! Take a break or log your progress 🌟{COLORS['reset']}") # Changed this line
        self._notify(f"{name} time over!", f"MoodMate: {name} is done!")

    def _countdown(self, seconds: int) -> None:
        """Displays a real-time countdown."""
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            print(f"{mins:02d}:{secs:02d}", end="\r")
            time.sleep(1)
        print("00:00", end="\r") # Ensure it ends at 00:00

    def _notify(self, title: str, message: str) -> None:
        """Plays a sound and attempts a desktop notification."""
        # Play a simple beep sound
        if os.name == 'nt': # For Windows
            os.system("echo \a")
        elif sys.platform == 'darwin': # For macOS
            os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
        # For Linux, `notify-send` could be used, but requires installation on some systems
        # else:
        #     os.system(f'notify-send "{title}" "{message}"')


class MoodAnalyzer:
    """Provides tools for analyzing and visualizing mood data."""
    
    def generate_weekly_summary(logs: List[Dict]) -> str:
        """Generates a text summary of the week's mood and task activity."""
        if not logs:
            return f"{COLORS['warning']}No entries in the last 7 days to summarize.{COLORS['reset']}"
        
        mood_counts = defaultdict(int)
        completed_tasks = 0
        total_tasks = 0
        notes_snippets = []
        
        for entry in logs:
            mood_counts[entry["mood"]] += 1
            total_tasks += 1
            if entry.get("completed", False):
                completed_tasks += 1
            if entry.get("note"):
                notes_snippets.append(entry["note"])
        
        summary_lines = [f"{COLORS['header']}--- 📅 Your Weekly Mood & Activity Summary ---{COLORS['reset']}", ""]
        summary_lines.append(f"🧮 Total entries: {len(logs)}") # Added emoji
        
        if mood_counts:
            summary_lines.append(f"\n{COLORS['menu']}Your Most Frequent Moods:{COLORS['reset']}")
            for mood, count in sorted(mood_counts.items(), key=lambda item: item[1], reverse=True):
                summary_lines.append(f"- {mood.title()} {EMOJI_MAP.get(mood, '')}: {count} times") # Added emoji
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            summary_lines.append(f"\n{COLORS['menu']}✅ Task Completion:{COLORS['reset']}") # Added emoji
            summary_lines.append(f"You completed {completed_tasks} out of {total_tasks} tasks ({completion_rate:.1f}%).")
        
        if notes_snippets:
            summary_lines.append(f"\n{COLORS['menu']}💭 A Glimpse into Your Thoughts (Recent Notes):{COLORS['reset']}") # Added emoji
            for i, note in enumerate(notes_snippets[-3:], 1): # Show up to 3 most recent notes
                summary_lines.append(f"{i}. {note[:70]}{'...' if len(note) > 70 else ''}")
        
        summary_lines.append(f"\n{COLORS['success']}Keep up the great work understanding yourself!{COLORS['reset']}")
        
        return "\n".join(summary_lines)


class MoodMateApp:
    """The main application class for MoodMate, handling user interaction and integrating all features."""
    
    def __init__(self):
        self.logger = MoodLogger()
        self.timer = PomodoroTimer()
        self.analyzer = MoodAnalyzer()
    
    def _clear_screen(self) -> None:
        """Clears the terminal screen for a cleaner interface."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def suggest_tasks(self, mood: str, category: Optional[str] = None) -> List[str]:
        """Provides task suggestions based on mood and optional category."""
        if mood not in MOOD_TASKS:
            return [] # Should not happen if mood selection is validated
        
        if category and category in MOOD_TASKS[mood]:
            # Return specific tasks from the chosen category, up to 5 random ones
            return sample(MOOD_TASKS[mood][category], min(5, len(MOOD_TASKS[mood][category])))
        
        # If no specific category or category invalid, pull from all categories for the mood
        all_tasks = []
        for cat_tasks_list in MOOD_TASKS[mood].values():
            all_tasks.extend(cat_tasks_list)
        return sample(all_tasks, min(5, len(all_tasks))) # Return up to 5 random tasks

    def run(self) -> None:
        """Starts the MoodMate application and runs the main menu loop."""
        try:
            while True:
                self._clear_screen()
                print(BANNER)
                print(f"{COLORS['header']}✨ MoodMate Menu ✨{COLORS['reset']}") # Updated main menu text
                print(f"[1] {COLORS['menu']}Record My Mood & Activity{COLORS['reset']}")
                print(f"[2] {COLORS['menu']}Quick Mood Check{COLORS['reset']}")
                print(f"[3] {COLORS['menu']}View My Mood Stats{COLORS['reset']}")
                print(f"[4] {COLORS['menu']}Start a Productivity Timer (Pomodoro){COLORS['reset']}")
                print(f"[5] {COLORS['menu']}Manage My Entries (Edit/Delete/Complete){COLORS['reset']}")
                print(f"[6] {COLORS['menu']}Data Tools (Backup/Export){COLORS['reset']}")
                print(f"[7] {COLORS['menu']}Get My Weekly Summary{COLORS['reset']}")
                print(f"[0] {COLORS['warning']}Exit MoodMate{COLORS['reset']}")
                
                choice = input(f"\n{COLORS['input']}👉 What would you like to do? (1-9): {COLORS['reset']}").strip()
                
                if choice == "1":
                    self._log_mood_flow()
                elif choice == "2":
                    self._quick_log_flow()
                elif choice == "3":
                    self._view_stats()
                elif choice == "4":
                    self._run_pomodoro()
                elif choice == "5":
                    self._manage_entries_flow()
                elif choice == "6":
                    self._data_management_flow()
                elif choice == "7":
                    self._weekly_summary_flow()
                elif choice == "0":
                    if self._confirm_exit():
                        print(f"\n{COLORS['success']}👋 Thanks for using MoodMate! Have a wonderful day!{COLORS['reset']}")
                        break
                else:
                    print(f"{COLORS['warning']}⚠️ Oops! That's not a valid option. Please choose a number from 1 to 9.{COLORS['reset']}")
                    time.sleep(1.5) # Give user time to read the message
        
        except KeyboardInterrupt:
            print(f"\n{COLORS['warning']}👋 MoodMate session ended by user. Come back anytime!{COLORS['reset']}")
        except Exception as e:
            print(f"\n{COLORS['warning']}⚠️ An unexpected error occurred: {e}. Please restart MoodMate or contact support.{COLORS['reset']}")
            time.sleep(3) # Keep error message on screen longer

    def _confirm_exit(self) -> bool:
        """Asks the user for confirmation before exiting the application."""
        print(f"\n{COLORS['warning']}--- Exiting MoodMate ---{COLORS['reset']}")
        confirm = input(f"{COLORS['input']}Are you sure you want to exit? All your data is saved automatically. (Y/N): {COLORS['reset']}").lower()
        return confirm == 'y'

    def _log_mood_flow(self) -> None:
        """Guides the user through logging their mood and selecting a suggested task."""
        self._clear_screen()
        print(f"{COLORS['header']}--- 📝 Log Your Mood & Activity ---{COLORS['reset']}")
        
        # Mood Selection
        print(f"\n{COLORS['menu']}How are you feeling right now?{COLORS['reset']}")
        moods = list(MOOD_TASKS.keys())
        for i, mood_name in enumerate(moods, 1):
            print(f"[{i}] {mood_name.title()} {EMOJI_MAP.get(mood_name, '')}") # Added emoji
        print(f"[0] {COLORS['warning']}Cancel{COLORS['reset']}")

        selected_mood = None
        while selected_mood is None:
            mood_choice_str = input(f"{COLORS['input']}👉 Choose a mood (1-{len(moods)}): {COLORS['reset']}").strip()
            if mood_choice_str == "0":
                print(f"{COLORS['warning']}✖ Mood logging cancelled.{COLORS['reset']}")
                return
            try:
                mood_idx = int(mood_choice_str) - 1
                if 0 <= mood_idx < len(moods):
                    selected_mood = moods[mood_idx]
                else:
                    print(f"{COLORS['warning']}⚠️ Please enter a number between 1 and {len(moods)}.{COLORS['reset']}")
            except ValueError:
                print(f"{COLORS['warning']}⚠️ That's not a number. Please try again.{COLORS['reset']}")

        # Task Category Selection (if multiple categories exist for the mood)
        categories = list(MOOD_TASKS[selected_mood].keys())
        tasks_to_suggest: List[str] = []

        if len(categories) > 1:
            print(f"\n{COLORS['menu']}Great! For a {selected_mood.title()} mood, what kind of activity are you looking for?{COLORS['reset']}")
            for i, cat in enumerate(categories, 1):
                print(f"[{i}] {cat.replace('_', ' ').title()}")
            print(f"[{len(categories) + 1}] Random Suggestion (any category)")
            print(f"[0] {COLORS['warning']}Cancel{COLORS['reset']}")

            chosen_category_tasks = None
            while chosen_category_tasks is None:
                category_choice_str = input(f"{COLORS['input']}👉 Choose a category (1-{len(categories) + 1}): {COLORS['reset']}").strip()
                if category_choice_str == "0":
                    print(f"{COLORS['warning']}✖ Mood logging cancelled.{COLORS['reset']}")
                    return
                try:
                    category_choice_int = int(category_choice_str)
                    if 1 <= category_choice_int <= len(categories):
                        selected_category_name = categories[category_choice_int - 1]
                        tasks_to_suggest = self.suggest_tasks(selected_mood, selected_category_name)
                        chosen_category_tasks = True
                    elif category_choice_int == len(categories) + 1:
                        tasks_to_suggest = self.suggest_tasks(selected_mood) # Get random from all categories
                        chosen_category_tasks = True
                    else:
                        print(f"{COLORS['warning']}⚠️ Please choose a number between 1 and {len(categories) + 1}.{COLORS['reset']}")
                except ValueError:
                    print(f"{COLORS['warning']}⚠️ That's not a number. Please try again.{COLORS['reset']}")
        else:
            # If only one category, or no specific category chosen, get tasks from all
            tasks_to_suggest = self.suggest_tasks(selected_mood)
        
        if not tasks_to_suggest:
            print(f"{COLORS['warning']}⚠️ No activity suggestions available for your choice. Returning to main menu.{COLORS['reset']}")
            time.sleep(2)
            return

        # Task Selection
        print(f"\n💡 Here are some ideas for your {selected_mood.title()} {EMOJI_MAP.get(selected_mood, '')} mood:") # Updated task suggestion text
        for i, task_item in enumerate(tasks_to_suggest, 1):
            print(f"[{i}] {task_item}")
        print(f"[0] {COLORS['warning']}Cancel{COLORS['reset']}")

        final_task = None
        while final_task is None:
            task_choice_str = input(f"{COLORS['input']}👉 Choose a task (1-{len(tasks_to_suggest)}) or 0 to cancel: {COLORS['reset']}").strip()
            if task_choice_str == "0":
                print(f"{COLORS['warning']}✖ Mood logging cancelled.{COLORS['reset']}")
                return
            try:
                task_idx = int(task_choice_str) - 1
                if 0 <= task_idx < len(tasks_to_suggest):
                    final_task = tasks_to_suggest[task_idx]
                else:
                    print(f"{COLORS['warning']}⚠️ Please enter a number between 1 and {len(tasks_to_suggest)}.{COLORS['reset']}")
            except ValueError:
                print(f"{COLORS['warning']}⚠️ That's not a number. Please try again.{COLORS['reset']}")

        # Note Entry
        note = input(f"{COLORS['input']}✍️ Add a quick note (optional, press Enter to skip): {COLORS['reset']}").strip()
        if len(note) > 200: # Limit note length for display
            note = note[:200] + "..."
        
        # Log the mood
        self.logger.log_mood(selected_mood, final_task, note if note else None)
        print(f"\n💬 {ENCOURAGING_REACTIONS.get(selected_mood, 'Logged with love 💚')}") # Added encouraging reaction

        # Offer Pomodoro based on keywords
        pomodoro_keywords = [
            "brainstorm", "work on", "plan", "organize", "learn", "research",
            "write", "create", "practice", "develop", "study", "focus",
            "project", "assignment", "revise", "group study", "teach", "coding"
        ]
        
        if any(keyword in final_task.lower() for keyword in pomodoro_keywords):
            pomodoro_confirm = input(f"\n{COLORS['menu']}✨ This looks like a great task for focused work! Would you like to start a Pomodoro session now? (y/n): {COLORS['reset']}").lower()
            if pomodoro_confirm == 'y':
                self._run_pomodoro()
        
        input(f"\n{COLORS['input']}Press Enter to return to the main menu...{COLORS['reset']}")

    def _quick_log_flow(self) -> None:
        """Allows for quick mood logging without detailed task selection."""
        self._clear_screen()
        print(f"{COLORS['header']}--- ⚡ Quick Mood Check ---{COLORS['reset']}")
        
        print(f"\n{COLORS['menu']}How are you feeling right now? Just pick one!{COLORS['reset']}")
        moods = list(MOOD_TASKS.keys())
        for i, mood_name in enumerate(moods, 1):
            print(f"[{i}] {mood_name.title()} {EMOJI_MAP.get(mood_name, '')}") # Added emoji
        print(f"[0] {COLORS['warning']}Cancel{COLORS['reset']}")

        selected_mood_quick = None
        while selected_mood_quick is None:
            choice = input(f"{COLORS['input']}👉 Choose a mood (1-{len(moods)}): {COLORS['reset']}").strip()
            if choice == "0":
                print(f"{COLORS['warning']}✖ Quick log cancelled.{COLORS['reset']}")
                return
            try:
                mood_idx = int(choice) - 1
                if 0 <= mood_idx < len(moods):
                    selected_mood_quick = moods[mood_idx]
                    self.logger.quick_log(selected_mood_quick)
                    print(f"\n💬 {ENCOURAGING_REACTIONS.get(selected_mood_quick, 'Logged with love 💚')}") # Added encouraging reaction
                else:
                    print(f"{COLORS['warning']}⚠️ Please enter a number between 1 and {len(moods)}.{COLORS['reset']}")
            except ValueError:
                print(f"{COLORS['warning']}⚠️ That's not a number. Please try again.{COLORS['reset']}")
        
        input(f"\n{COLORS['input']}Press Enter to return to the main menu...{COLORS['reset']}")

    def _view_stats(self) -> None:
        """Displays overall mood statistics."""
        self._clear_screen()
        print(f"{COLORS['header']}--- 📊 Your Mood Statistics ---{COLORS['reset']}")
        
        stats = self.logger.get_mood_stats()
        
        if stats["total"] == 0:
            print(f"{COLORS['warning']}⚠️ No entries yet! Log some moods to see your stats here.{COLORS['reset']}")
            input(f"\n{COLORS['input']}Press Enter to continue...{COLORS['reset']}")
            return

        print(f"\n{COLORS['menu']}Overall Summary:{COLORS['reset']}")
        print(f"Total entries logged: {stats['total']}")
        print(f"Tasks marked as completed: {stats['completion_rate']:.1f}%")
        print(f"Entries with a personal note: {stats['notes_count']}")
        
        if stats['by_mood']:
            print(f"\n{COLORS['menu']}Your Mood Frequency:{COLORS['reset']}")
            for mood, count in sorted(stats['by_mood'].items(), key=lambda x: x[1], reverse=True):
                print(f"- {mood.title()} {EMOJI_MAP.get(mood, '')}: {count} times") # Added emoji
        
        if stats['by_day']:
            print(f"\n{COLORS['menu']}Recent Logging Activity (Last 7 Days):{COLORS['reset']}")
            # Sort by date descending and show top 7
            recent_days = sorted([ (date, count) for date, count in stats['by_day'].items() if (datetime.now().date() - date).days <= 7 ], key=lambda x: x[0], reverse=True)
            if recent_days:
                for date, count in recent_days:
                    print(f"- {date.strftime('%b %d, %Y')}: {count} entries")
            else:
                print("No entries in the last 7 days.")
        
        input(f"\n{COLORS['input']}Press Enter to return to the main menu...{COLORS['reset']}")


    def _run_pomodoro(self) -> None:
        """Handles the Pomodoro timer setup and execution."""
        self._clear_screen()
        print(f"{COLORS['header']}--- 🍅 Productivity Timer (Pomodoro) ---{COLORS['reset']}")
        
        try:
            work = int(input(f"{COLORS['input']}Set your FOCUS time (minutes, default 25): {COLORS['reset']}") or 25)
            break_dur = int(input(f"{COLORS['input']}Set your SHORT BREAK time (minutes, default 5): {COLORS['reset']}") or 5)
            cycles = int(input(f"{COLORS['input']}How many cycles do you want? (default 4): {COLORS['reset']}") or 4)
            
            print(f"\n{COLORS['success']}✓ Starting {cycles} cycles: {work} min FOCUS | {break_dur} min BREAK{COLORS['reset']}")
            self.timer.run(work, break_dur, cycles)
        except ValueError:
            print(f"{COLORS['warning']}⚠️ Invalid input detected. Starting with default settings (25 min work, 5 min break, 4 cycles).{COLORS['reset']}")
            self.timer.run(25, 5, 4)
        
        input(f"\n{COLORS['input']}Press Enter to return to the main menu...{COLORS['reset']}")

    def _manage_entries_flow(self) -> None:
        """Provides options to view, edit, delete, or mark entries as complete."""
        self._clear_screen()
        print(f"{COLORS['header']}--- ✏️ Manage Your Mood Entries ---{COLORS['reset']}")
        
        logs = self.logger.get_all_logs()
        if not logs:
            print(f"{COLORS['warning']}⚠️ You don't have any entries yet! Log some moods first.{COLORS['reset']}")
            input(f"\n{COLORS['input']}Press Enter to continue...{COLORS['reset']}")
            return

        # Display all entries with reverse numbering for user-friendliness (recent first)
        self._display_all_entries(logs)

        print(f"\n{COLORS['menu']}What would you like to do?{COLORS['reset']}")
        print(f"[1] {COLORS['menu']}Edit an entry{COLORS['reset']}")
        print(f"[2] {COLORS['menu']}Mark a task as Completed{COLORS['reset']}")
        print(f"[3] {COLORS['menu']}Delete an entry{COLORS['reset']}")
        print(f"[4] {COLORS['menu']}Mark ALL pending tasks as Completed{COLORS['reset']}") # New option
        print(f"[0] {COLORS['warning']}Back to Main Menu{COLORS['reset']}")
        
        while True:
            choice = input(f"{COLORS['input']}👉 Choose an option (1-4, or 0 to go back): {COLORS['reset']}").strip()
            if choice == "0":
                print(f"{COLORS['warning']}✖ Returning to main menu.{COLORS['reset']}")
                return
            
            try:
                action_choice = int(choice)
                if not (1 <= action_choice <= 4): # Updated range
                    print(f"{COLORS['warning']}⚠️ Invalid option. Please choose a number from 1 to 4.{COLORS['reset']}")
                    continue

                if action_choice == 2:  # Mark a single task as completed
                    pending_tasks = [entry for entry in logs if not entry.get("completed", False)]
                    if not pending_tasks:
                        print(f"{COLORS['success']}🎉 All your tasks are completed! Great job!{COLORS['reset']}")
                        input(f"\n{COLORS['input']}Press Enter to continue...{COLORS['reset']}")
                        break

                    self._display_pending_tasks(pending_tasks)
                    
                    task_num_str = input(f"{COLORS['input']}Enter the NUMBER of the task you completed (or 0 to cancel): {COLORS['reset']}").strip()
                    if task_num_str == "0":
                        print(f"{COLORS['warning']}✖ Operation cancelled.{COLORS['reset']}")
                        break

                    task_idx_in_pending = int(task_num_str) - 1

                    if 0 <= task_idx_in_pending < len(pending_tasks):
                        # Find the actual index in the full logs list
                        selected_pending_entry = pending_tasks[task_idx_in_pending]
                        actual_index = logs.index(selected_pending_entry) # Get original index
                        
                        if self.logger.edit_entry(actual_index, completed=True):
                            print(f"{COLORS['success']}✅ Task '{selected_pending_entry['task']}' marked as completed!{COLORS['reset']}")
                        else:
                            print(f"{COLORS['warning']}⚠️ Could not mark task as completed.{COLORS['reset']}")
                    else:
                        print(f"{COLORS['warning']}⚠️ Invalid task number. Please try again.{COLORS['reset']}")
                    
                    input(f"\n{COLORS['input']}Press Enter to continue...{COLORS['reset']}")
                    break # Exit loop after marking task

                elif action_choice == 4: # Mark ALL pending tasks as completed
                    confirm_all = input(f"{COLORS['warning']}Are you sure you want to mark ALL pending tasks as completed? (Y/N): {COLORS['reset']}").lower()
                    if confirm_all == 'y':
                        updated_count = self.logger.mark_all_pending_as_completed()
                        if updated_count > 0:
                            print(f"{COLORS['success']}✅ Successfully marked {updated_count} task(s) as completed! Keep up the great work!{COLORS['reset']}")
                        else:
                            print(f"{COLORS['menu']}No pending tasks to mark as completed.{COLORS['reset']}")
                    else:
                        print(f"{COLORS['menu']}Operation cancelled. No tasks were marked.{COLORS['reset']}")
                    input(f"\n{COLORS['input']}Press Enter to continue...{COLORS['reset']}")
                    break # Exit loop after marking all tasks
                
                else: # For Edit or Delete, prompt for index from full list
                    entry_num_str = input(f"{COLORS['input']}Enter the NUMBER of the entry you want to modify (from the full list above): {COLORS['reset']}").strip()
                    entry_index_from_bottom = int(entry_num_str) - 1 # User sees 1-indexed, newest first
                    
                    # Convert user's reverse index to actual list index (0-indexed, oldest first)
                    actual_index = len(logs) - 1 - entry_index_from_bottom

                    if not (0 <= actual_index < len(logs)):
                        print(f"{COLORS['warning']}⚠️ That entry number doesn't exist. Please check the list.{COLORS['reset']}")
                        continue

                    if action_choice == 1: # Edit
                        self._edit_single_entry(actual_index, logs)
                    elif action_choice == 3: # Delete
                        confirm_delete = input(f"{COLORS['warning']}Are you sure you want to delete entry {entry_num_str}? This cannot be undone. (Y/N): {COLORS['reset']}").lower()
                        if confirm_delete == 'y':
                            if self.logger.delete_entry(actual_index):
                                # After deletion, reload logs to reflect changes for display
                                logs = self.logger.get_all_logs()
                                if logs: # Only redisplay if there are still logs
                                    self._display_all_entries(logs)
                            else:
                                print(f"{COLORS['warning']}⚠️ Could not delete entry.{COLORS['reset']}")
                        else:
                            print(f"{COLORS['menu']}Deletion cancelled.{COLORS['reset']}")
                    break # Exit loop after successful action or cancellation
            except ValueError:
                print(f"{COLORS['warning']}⚠️ Please enter a valid number.{COLORS['reset']}")
            except IndexError:
                print(f"{COLORS['warning']}⚠️ An internal error occurred with indexing. Please restart MoodMate.{COLORS['reset']}")

        input(f"\n{COLORS['input']}Press Enter to return to the main menu...{COLORS['reset']}")

    def _display_all_entries(self, logs: List[Dict], count: int = 10) -> None:
        """Helper to display a limited number of recent entries for management."""
        if not logs:
            print(f"{COLORS['warning']}No entries to display.{COLORS['reset']}")
            return

        print(f"\n{COLORS['menu']}--- Your Recent Entries (newest first) ---{COLORS['reset']}")
        display_logs = logs[-count:] # Show only the last 'count' entries
        
        for i, entry in enumerate(reversed(display_logs)): # Display in reverse order (newest first)
            # original_index = len(logs) - 1 - i # Calculate original index from reversed list
            display_num = i + 1 # User sees 1-indexed count
            date_time = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
            status = "✅ Done" if entry.get("completed", False) else "⏳ Pending"
            
            print(f"\n{COLORS['success']}[{display_num}]{COLORS['reset']} {date_time} | {entry['mood'].title()} Mood")
            print(f"   Task: {entry['task']}")
            print(f"   Status: {status}")
            if entry.get("note"):
                print(f"   Note: {entry['note'][:70]}{'...' if len(entry['note']) > 70 else ''}")
        print(f"\n{COLORS['menu']}Showing the last {len(display_logs)} entries.{COLORS['reset']}")
        if len(logs) > len(display_logs):
             print(f"{COLORS['input']}   (Total entries: {len(logs)}. Scroll up for more past entries in history.)")

    def _display_pending_tasks(self, pending_tasks: List[Dict]) -> None:
        """Displays only the tasks that are not yet marked as completed."""
        print(f"\n{COLORS['menu']}--- Your Unfinished Tasks ---{COLORS['reset']}")
        if not pending_tasks:
            print(f"{COLORS['success']}🎉 All tasks are currently completed! Nothing pending.{COLORS['reset']}")
            return

        for i, entry in enumerate(pending_tasks, 1):
            date_time = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
            print(f"{COLORS['warning']}[{i}]{COLORS['reset']} {date_time} | {entry['mood'].title()} Mood: {entry['task']}")
            if entry.get("note"):
                print(f"   Note: {entry['note'][:70]}{'...' if len(entry['note']) > 70 else ''}")
        print("\n")


    def _edit_single_entry(self, actual_index: int, logs: List[Dict]) -> None:
        """Facilitates editing a single log entry."""
        entry_to_edit = logs[actual_index]
        print(f"\n{COLORS['menu']}--- Editing Entry #{len(logs) - actual_index} ---{COLORS['reset']}")
        print(f"Current Mood: {entry_to_edit['mood'].title()}")
        print(f"Current Task: {entry_to_edit['task']}")
        print(f"Current Note: {entry_to_edit.get('note', 'No note')}")
        print(f"Current Status: {'Completed' if entry_to_edit.get('completed', False) else 'Pending'}")

        changes = {}
        
        new_mood_prompt = input(f"{COLORS['input']}Change Mood? (Enter new mood, or press Enter to keep '{entry_to_edit['mood'].title()}'): {COLORS['reset']}").strip().lower()
        if new_mood_prompt and new_mood_prompt in MOOD_TASKS:
            changes["mood"] = new_mood_prompt
        elif new_mood_prompt: # If they typed something but it's not a valid mood
            print(f"{COLORS['warning']}⚠️ Invalid mood entered. Keeping original mood.{COLORS['reset']}")

        new_task_prompt = input(f"{COLORS['input']}Change Task? (Enter new task description, or press Enter to keep current): {COLORS['reset']}").strip()
        if new_task_prompt:
            changes["task"] = new_task_prompt
        
        new_note_prompt = input(f"{COLORS['input']}Change Note? (Enter new note, or type 'REMOVE' to clear, press Enter to keep current): {COLORS['reset']}").strip()
        if new_note_prompt.lower() == 'remove':
            changes["note"] = None
        elif new_note_prompt:
            changes["note"] = new_note_prompt
        
        status_change = input(f"{COLORS['input']}Mark as completed? (Y/N, current is {'Completed' if entry_to_edit.get('completed', False) else 'Pending'}): {COLORS['reset']}").lower()
        if status_change == 'y':
            changes["completed"] = True
        elif status_change == 'n':
            changes["completed"] = False

        if changes:
            if self.logger.edit_entry(actual_index, **changes):
                print(f"{COLORS['success']}✅ Entry updated successfully!{COLORS['reset']}")
            else:
                print(f"{COLORS['warning']}⚠️ Failed to update entry.{COLORS['reset']}")
        else:
            print(f"{COLORS['menu']}No changes were made to the entry.{COLORS['reset']}")


    def _data_management_flow(self) -> None:
        """Handles options for backing up, restoring, and exporting data."""
        self._clear_screen()
        print(f"{COLORS['header']}--- 🗄️ Data Tools ---{COLORS['reset']}")
        
        print(f"\n{COLORS['menu']}What would you like to do with your data?{COLORS['reset']}")
        print(f"[1] {COLORS['menu']}Backup My Data{COLORS['reset']}")
        print(f"[2] {COLORS['menu']}Restore Data from Backup (Careful!){COLORS['reset']}")
        print(f"[3] {COLORS['menu']}Export My Data (to JSON/CSV file){COLORS['reset']}")
        print(f"[0] {COLORS['warning']}Back to Main Menu{COLORS['reset']}")
        
        choice = input(f"{COLORS['input']}👉 Choose an option (1-3): {COLORS['reset']}").strip()
        
        if choice == "1":
            try:
                # Read from current log file and write to backup
                with open(LOG_FILE, 'r') as src, open(BACKUP_FILE, 'w') as dest:
                    json.dump(json.load(src), dest, indent=2)
                print(f"{COLORS['success']}✅ Data backed up successfully to '{BACKUP_FILE}'!{COLORS['reset']}")
            except FileNotFoundError:
                print(f"{COLORS['warning']}⚠️ No data to backup. Log some moods first!{COLORS['reset']}")
            except Exception as e:
                print(f"{COLORS['warning']}⚠️ Backup failed: {e}.{COLORS['reset']}")
        
        elif choice == "2":
            if os.path.exists(BACKUP_FILE):
                print(f"{COLORS['warning']}--- Restore Warning ---{COLORS['reset']}")
                print(f"{COLORS['warning']}⚠️ Restoring will OVERWRITE your current MoodMate data with the backup!{COLORS['reset']}")
                confirm = input(f"{COLORS['input']}Are you absolutely sure you want to restore? (Y/N): {COLORS['reset']}").lower()
                if confirm == 'y':
                    try:
                        # Read from backup and write to current log file
                        with open(BACKUP_FILE, 'r') as src, open(LOG_FILE, 'w') as dest:
                            json.dump(json.load(src), dest, indent=2)
                        print(f"{COLORS['success']}✅ Data restored successfully from backup!{COLORS['reset']}")
                    except Exception as e:
                        print(f"{COLORS['warning']}⚠️ Restore failed: {e}. The backup file might be corrupted.{COLORS['reset']}")
                else:
                    print(f"{COLORS['menu']}Restore cancelled.{COLORS['reset']}")
            else:
                print(f"{COLORS['warning']}⚠️ No backup file found at '{BACKUP_FILE}'. Please create a backup first.{COLORS['reset']}")
        
        elif choice == "3":
            print(f"\n{COLORS['menu']}Choose your export format:{COLORS['reset']}")
            print(f"[1] {COLORS['menu']}JSON (recommended for data sharing/re-import){COLORS['reset']}")
            print(f"[2] {COLORS['menu']}CSV (great for spreadsheets like Excel){COLORS['reset']}")
            
            format_choice = input(f"{COLORS['input']}👉 Choose format (1-2): {COLORS['reset']}").strip()
            format_type = "json" # Default
            if format_choice == "2":
                format_type = "csv"
            elif format_choice != "1":
                print(f"{COLORS['warning']}⚠️ Invalid choice. Exporting as JSON by default.{COLORS['reset']}")

            try:
                export_path = self.logger.export_data(format_type)
                print(f"{COLORS['success']}✅ Data exported successfully to: '{export_path}'{COLORS['reset']}")
            except Exception as e:
                print(f"{COLORS['warning']}⚠️ Export failed: {e}. Make sure you have entries logged.{COLORS['reset']}")
        
        elif choice == "0":
            print(f"{COLORS['warning']}✖ Returning to main menu.{COLORS['reset']}")
            return
        else:
            print(f"{COLORS['warning']}⚠️ Invalid option. Please choose 1, 2, or 3.{COLORS['reset']}")
        
        input(f"\n{COLORS['input']}Press Enter to continue...{COLORS['reset']}")

    def _weekly_summary_flow(self) -> None:
        """Generates and displays a summary of the past 7 days."""
        self._clear_screen()
        print(f"{COLORS['header']}--- 📊 Your Past 7 Days at a Glance ---{COLORS['reset']}")
        logs_last_7_days = self.logger.get_recent_moods(7)
        summary = self.analyzer.generate_weekly_summary(logs_last_7_days)
        print(summary)
        
        input(f"\n{COLORS['input']}Press Enter to return to the main menu...{COLORS['reset']}")

# ======================
# ▶️ App Execution
# ======================
if __name__ == "__main__":
    app = MoodMateApp()
    app.run()
