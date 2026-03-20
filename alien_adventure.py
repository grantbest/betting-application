import random
import time

class AlienMath:
    def __init__(self, difficulty: int = 1):
        self.difficulty = difficulty
    def generate_problem(self) -> str:
        if self.difficulty == 1:
            num1 = random.randint(1, 4)
            num2 = random.randint(1, 4)
            return f'{num1}(5) + {num2}(5) = ?', num1 + num2
        else:
            num1 = random.randint(1, 5)
            num2 = random.randint(1, 5)
            return f'{num1}(6) * {num2}(6) = ?', num1 * num2

class AdventureEngine:
    def __init__(self, storyline):
        self.storyline = storyline
        self.current_position = 0
    def get_current_scene(self):
        return self.storyline[self.current_position]
    def progress(self):
        if self.current_position < len(self.storyline) - 1:
            self.current_position += 1
            return True
        return False

def play_game():
    print("🛸 WELCOME TO THE ALIEN MATH ADVENTURE 🛸")
    print("-----------------------------------------")
    
    story = [
        "You wake up on a strange planet. A friendly alien approaches.",
        "The alien shows you a holographic terminal. It requires a code.",
        "The code is hidden behind an ancient math puzzle!",
        "You solve the puzzle and the spaceship doors open. You are safe!"
    ]
    
    engine = AdventureEngine(story)
    math_engine = AlienMath(difficulty=1)
    
    while True:
        current_scene = engine.get_current_scene()
        print(f"\n🎬 {current_scene}")
        
        if "math puzzle" in current_scene:
            print("\n🧠 PUZZLE TIME!")
            problem, answer = math_engine.generate_problem()
            print(f"Solve this alien equation: {problem}")
            
            try:
                # Using a fixed answer if input is hard in this CLI env
                user_input = int(input("Your Answer: "))
                if user_input == answer:
                    print("✅ CORRECT! The terminal glows green.")
                else:
                    print(f"❌ WRONG! The answer was {answer}. The ground shakes...")
                    continue
            except EOFError:
                print(f"Skipping input in automated env. Answer was {answer}.")
            except ValueError:
                print("Please enter a number!")
                continue
        
        time.sleep(1)
        if not engine.progress():
            print("\n🎉 CONGRATULATIONS! You completed the adventure.")
            break

if __name__ == "__main__":
    play_game()
