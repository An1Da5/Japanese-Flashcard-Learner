# Library imports
import json
import random
import tkinter

"""
Japanese vocabulary flashcard learning app.

Provides two quiz modes (multiple choice and pair matching) with
difficulty progression, backed by a JSON word list. Includes both a
terminal interface and a tkinter GUI.
"""

class Word:

    """Represents a single vocabulary entry with its Hiragana, romanised form, English translation, and difficulty level."""

    def __init__(self, inHiragana, inRomanised, inEnglish, inDifficulty):

        """Store the four fields that make up one vocabulary word."""

        self.Hiragana = inHiragana
        self.Romanised = inRomanised
        self.English = inEnglish
        self.Difficulty = inDifficulty

    def getHiragana(self):

        """Return this word's Hiragana form."""

        return self.Hiragana
    
    def getRomanised(self):

        """Return this word's Romanised (romaji) form."""
        
        return self.Romanised
    
    def getEnglish(self):

        """Return this word's English translation."""

        return self.English
    
    def getDifficulty(self):

        """Return this word's difficulty level as an integer."""

        return self.Difficulty

class Library:

    """Loads and stores the full collection of Word objects from a JSON file, and provides difficulty-based filtering."""

    def __init__(self):

        """Initialise an empty word list, ready to be populated by loadJSON."""

        self.Words = []

    def loadJSON(self, filepath):

        """Read the given JSON file and populate self.Words with Word objects built from its contents."""

        with open(filepath, "r", encoding="UTF-8") as file:
            wordList = json.load(file)
            for i in range(len(wordList)):
                hira = list(wordList[i].values())[0]
                roma = list(wordList[i].values())[1]
                eng = list(wordList[i].values())[2]
                diff = list(wordList[i].values())[3]
                self.Words.append(Word(hira, roma, eng, diff))

    def filterDifficulty(self, currentDiff):

        """Return a list of Words whose difficulty is at or below currentDiff."""

        currentWords = []
        for word in self.Words:
            if word.getDifficulty() <= currentDiff:
                currentWords.append(word)
        return currentWords

class Difficulty:

    """Tracks the player's current difficulty level and correct-answer streak, unlocking harder difficulties as the streak grows."""

    def __init__(self):

        """Start at difficulty 1 with 0 correct answer streak."""

        self.CurrentDiff = 1
        self.StreakCount = 0

    def getCurrentDiff(self):

        """Return the currently unlocked difficulty level."""

        return self.CurrentDiff

    def setCurrentDiff(self):

        """Increase the difficulty by 1 if the streak has reached 5 and the max difficulty hasn't been reached, resetting the streak."""

        if self.CurrentDiff < 3 and self.StreakCount == 5:
            self.CurrentDiff += 1
            self.StreakCount = 0

    def setStreakCount(self, correct):

        """Increment the streak on a correct answer, or reset it to 0 on an incorrect one."""

        if correct:
            self.StreakCount += 1
        else:
            self.StreakCount = 0

class MultipleQuiz:

    """Handles the logic for a multiple-choice quiz: picking questions, building options, and checking answers. Contains no display code."""

    def __init__(self, inDifficulty, inLibrary, inDirection):

        """Store references to the shared Difficulty and Library objects and the chosen prompt direction ('e' or 'j')."""

        self.Difficulty = inDifficulty
        self.WordOptions = inLibrary
        self.Direction = inDirection
        self.CurrentWord = None
        self.Input = ""
        self.Score = 0
        self.Count = 0

    def getQuestion(self):

        """Pick a random word (within the current difficulty) as the question, and three distinct distractor words. Returns the distractors."""

        distractors = []
        currentDiff = self.Difficulty.getCurrentDiff()
        wordOptions = self.WordOptions.filterDifficulty(currentDiff)
        self.CurrentWord = random.choice(wordOptions)
        selectWord = random.choice(wordOptions)
        while len(distractors) < 3:
            if selectWord == self.CurrentWord or selectWord in distractors:
                selectWord = random.choice(wordOptions)
            else:
                distractors.append(selectWord)
                selectWord = random.choice(wordOptions)
        return distractors

    def displayQuestion(self, distractors):

        """Terminal version: build the prompt and options text, print them, collect and store the user's validated input, and return the options."""

        prompt = None
        option = None
        options = distractors.copy()
        if self.Direction == "e":
            prompt = self.CurrentWord.getEnglish()
            option = Word.getHiragana
        elif self.Direction == "j":
            prompt = self.CurrentWord.getHiragana()
            option = Word.getEnglish
        print(f"Current Difficulty: {self.Difficulty.getCurrentDiff()}")
        print(prompt)
        options.append(self.CurrentWord)
        options = [option(x) for x in options]
        random.shuffle(options)
        self.Input = errorHandling(f"1: {options[0]} 2: {options[1]} 3: {options[2]} 4: {options[3]} q: Quit ")
        return options

    def displayQuestionGUI(self, distractors):

        """GUI version: build the prompt and options text without printing or collecting input. Returns (prompt, options)."""

        prompt = None
        option = None
        options = distractors.copy()
        if self.Direction == "e":
            prompt = self.CurrentWord.getEnglish()
            option = Word.getHiragana
        elif self.Direction == "j":
            prompt = self.CurrentWord.getHiragana()
            option = Word.getEnglish
        options.append(self.CurrentWord)
        options = [option(x) for x in options]
        random.shuffle(options)
        return prompt, options

    def checkAnswer(self, options):

        """Terminal version: compare self.Input against the correct option, update score/streak/difficulty, and print the result."""

        if self.Direction == "e":
            prompt = self.CurrentWord.getHiragana()
        elif self.Direction == "j":
            prompt = self.CurrentWord.getEnglish()
        if self.Input == "q":
            return True
        answer = options[int(self.Input) - 1]
        if answer == prompt:
            print("Correct!")
            self.Difficulty.setStreakCount(True)
            self.Score += 1
            self.Count += 1
        else:
            print(f'Incorrect! The correct answer was "{prompt}"!')
            self.Difficulty.setStreakCount(False)
            self.Count += 1
        self.Difficulty.setCurrentDiff()
        return False

    def checkAnswerGUI(self, selection):

        """GUI version: compare the given selection against the correct option, update score/streak/difficulty, and return (correct, correctAnswer) without printing."""

        if self.Direction == "e":
            prompt = self.CurrentWord.getHiragana()
        elif self.Direction == "j":
            prompt = self.CurrentWord.getEnglish()
        if selection == prompt:
            self.Difficulty.setStreakCount(True)
            self.Score += 1
            self.Count += 1
        else:
            self.Difficulty.setStreakCount(False)
            self.Count += 1
        self.Difficulty.setCurrentDiff()
        return (selection == prompt), prompt

    def getScore(self):

        """Return a formatted string showing score, question count, and percentage."""

        if self.Count == 0:
            return f"Score: 0/0 ~ 0%"
        else:
            return f"Score: {self.Score}/{self.Count} ~ {self.Score / self.Count * 100}%"

class MultipleGUI:

    """Tkinter display layer for the multiple-choice quiz. Builds and updates widgets, delegating all quiz logic to a MultipleQuiz instance."""
    
    def __init__(self, inDifficulty, inLibrary, inDirection, inRoot):

        """Build the quiz window's widgets (difficulty display, prompt, options, quit/hint buttons) on the shared root window and show the first question."""

        self.Difficulty = inDifficulty
        self.WordOptions = inLibrary
        self.Direction = inDirection
        self.Quiz = MultipleQuiz(self.Difficulty, self.WordOptions, self.Direction)
        self.Root = inRoot
        self.Font = ("Courier New", 18)
        self.DifficultyDisplay = tkinter.Label(self.Root, text=f"Current Difficulty: {self.Difficulty.getCurrentDiff()}", font=self.Font)
        self.DifficultyDisplay.pack()
        self.Question = tkinter.Label(self.Root, text="", font=self.Font)
        self.Question.pack()
        self.BottomRow = tkinter.Frame(self.Root)
        self.Options = [tkinter.Button(self.Root, text="", font=self.Font), tkinter.Button(self.Root, text="", font=self.Font), tkinter.Button(self.Root, text="", font=self.Font), tkinter.Button(self.BottomRow, text="", font=self.Font)]
        for i in range(3):
            self.Options[i].pack()
        self.Quit = tkinter.Button(self.BottomRow, text="Quit", font=self.Font, width=12, command=lambda: self.endQuiz())
        self.Quit.pack(side="left")
        if self.Direction == "j":
            self.Hint = tkinter.Button(self.BottomRow, text="Hint", font=self.Font, width=12, command=lambda: self.showHint())
            self.Hint.pack(side="right")
            self.Options[3].pack(side="left", fill="x", padx=100)
        else:
            self.Spacer = tkinter.Button(self.BottomRow, text="Quit", font=self.Font, width=12, fg="#f0f0f0", disabledforeground="#f0f0f0", bg="#f0f0f0", activebackground="#f0f0f0", relief="flat", borderwidth=0, highlightthickness=0)
            self.Spacer.pack(side="right")
            self.Options[3].pack(side="left", fill="x", padx=100)
        self.BottomRow.pack()
        self.Correct = tkinter.Label(self.Root, text="", font=self.Font)
        self.Correct.pack()
        self.showQuestion()

    def showQuestion(self):

        """Fetch a new question from self.Quiz and update the prompt/option widgets to display it."""

        distractors = self.Quiz.getQuestion()
        prompt, options = self.Quiz.displayQuestionGUI(distractors)
        self.Question.config(text=prompt)
        for i in range(4):
            self.Options[i].config(text=options[i], command=lambda opt=options[i]: self.checkAnswer(opt))
        if self.Direction == "j":
            self.Hint.config(text="Hint")
        
    def showHint(self):

        """Reveal the current word's romanised reading on the hint button."""

        self.Hint.config(text=self.Quiz.CurrentWord.getRomanised())

    def checkAnswer(self, selection):

        """Check the clicked option via self.Quiz, update the result/difficulty labels, and load the next question."""

        correct, prompt = self.Quiz.checkAnswerGUI(selection)
        if correct:
            self.Correct.config(text="Correct!")
        else:
            self.Correct.config(text=f'Incorrect! The correct answer was "{prompt}"!')
        self.DifficultyDisplay.config(text=f"Current Difficulty: {self.Difficulty.getCurrentDiff()}")
        self.showQuestion()

    def endQuiz(self):

        """Destroy the quiz widgets and display the final score with a button to return to the menu."""

        self.DifficultyDisplay.config(text=self.Quiz.getScore())
        self.Question.destroy()
        for i in range(3):
            self.Options[i].destroy()
        self.ReturnButton = tkinter.Button(self.Root, text="Return to Menu", font=self.Font, command=lambda: self.returnToMenu())
        self.ReturnButton.pack()
        self.Correct.destroy()
        self.BottomRow.destroy()

    def returnToMenu(self):

        """Destroy the score screen's widgets and rebuild the main menu."""

        self.DifficultyDisplay.destroy()
        self.ReturnButton.destroy()
        buildMenu(self.Difficulty, self.WordOptions, self.Root)

class MatchingQuiz:

    """Handles the logic for the pair-matching quiz: picking a round's words and scoring matches. Contains no display code."""

    def __init__(self, inDifficulty, inLibrary):

        """Store references to the shared Difficulty and Library objects."""

        self.Difficulty = inDifficulty
        self.WordOptions = inLibrary
        self.CurrentWords = []
        self.japanese = []
        self.Input = ""
        self.Score = 0
        self.Count = 0

    def getQuestion(self):

        """Pick four distinct words (within the current difficulty) for a new matching round, stored in self.CurrentWords."""

        self.CurrentWords = []
        currentDiff = self.Difficulty.getCurrentDiff()
        wordOptions = self.WordOptions.filterDifficulty(currentDiff)
        selectWord = random.choice(wordOptions)
        while len(self.CurrentWords) < 4:
            if selectWord in self.CurrentWords:
                selectWord = random.choice(wordOptions)
            else:
                self.CurrentWords.append(selectWord)
                selectWord = random.choice(wordOptions)

    def displayQuestion(self):

        """Print the English words alongside a shuffled, numbered list of Hiragana words."""

        english = [engWords.getEnglish() for engWords in self.CurrentWords]
        self.japanese = [japWords.getHiragana() for japWords in self.CurrentWords]
        random.shuffle(self.japanese)
        for i in range(len(english)):
            print(f"{english[i]} | {i + 1}: {self.japanese[i]}")

    def checkAnswer(self, i):

        """Terminal version: ask which Hiragana number matches CurrentWords[i]'s English word, check it, update score/streak/difficulty, and print the result."""

        self.Input = errorHandling(f'Which Japanese word matches the English word "{self.CurrentWords[i].getEnglish()}"? Enter a corresponding number or q to quit. ')
        if self.Input == "q":
            return True
        answer = int(self.Input)
        if self.CurrentWords[i].getHiragana() == self.japanese[answer - 1]:
            print("Correct!")
            self.Difficulty.setStreakCount(True)
            self.Score += 1
            self.Count += 1
        else:
            print(f'Incorrect! The correct answer was "{self.CurrentWords[i].getHiragana()}"!')
            self.Difficulty.setStreakCount(False)
            self.Count += 1
        self.Difficulty.setCurrentDiff()
        return False

    def checkAnswerGUI(self, correct):

        """GUI version: update score/streak/difficulty based on whether the clicked pair was correct."""

        if correct:
            self.Difficulty.setStreakCount(True)
            self.Score += 1
            self.Count += 1
        else:
            self.Difficulty.setStreakCount(False)
            self.Count += 1
        self.Difficulty.setCurrentDiff()

    def getScore(self):
        if self.Count == 0:
            return f"Score: 0/0 ~ 0%"
        else:
            return f"Score: {self.Score}/{self.Count} ~ {self.Score / self.Count * 100}%"

class MatchingGUI:

    """Tkinter display layer for the pair-matching quiz. Builds a grid of clickable tiles and delegates match-checking to a MatchingQuiz instance."""

    def __init__(self, inDifficulty, inLibrary, inRoot):

        """Set up a matched-pairs-tracking state and build the first round of tiles on the shared root window."""

        self.Difficulty = inDifficulty
        self.WordOptions = inLibrary
        self.Quiz = MatchingQuiz(self.Difficulty, self.WordOptions)
        self.Root = inRoot
        self.Font = ("Courier New", 18)
        self.FirstClick = None
        self.FirstButton = None
        self.MatchedPairs = 0
        self.Words = []
        self.generateRound()
        self.Correct = tkinter.Label(self.Root, text="", font=self.Font)
        self.Correct.grid(row=4, column=0, columnspan=2)
        self.Quit = tkinter.Button(self.Root, text="Quit", font=self.Font, command=lambda: self.endQuiz())
        self.Quit.grid(row=5, column=0, columnspan=2)

    def generateRound(self):

        """Fetch four new words, build a shuffled grid of 8 Hiragana/English tiles, and display them as buttons."""

        self.MatchedPairs = 0
        self.Quiz.getQuestion()
        self.Buttons = []
        self.Words = [(words.getEnglish(), words) for words in self.Quiz.CurrentWords]
        self.Words.extend([(words.getHiragana(), words) for words in self.Quiz.CurrentWords])
        random.shuffle(self.Words)
        for i in range(8):
            row = i // 2
            column = i % 2
            button = tkinter.Button(self.Root, text=self.Words[i][0], font=self.Font, command=lambda current=i: self.checkAnswer(self.Words[current][1], self.Buttons[current]))
            button.grid(row=row, column=column)
            self.Buttons.append(button)

    def checkAnswer(self, word, button):

        """Handle a tile click: store the first selection, or compare it against the second and update score/visuals accordingly. Starts a new round once all pairs are matched."""

        if self.FirstClick is None:
            self.FirstClick = word
            self.FirstButton = button
            button.config(bg="#d9d9d9")
        else:
            if self.FirstClick == word:
                self.Correct.config(text="Correct!")
                self.Quiz.checkAnswerGUI(True)
                self.FirstButton.destroy()
                button.destroy()
                self.MatchedPairs += 1
            else:
                self.Correct.config(text="Incorrect! Try another pair!")
                self.Quiz.checkAnswerGUI(False)
                self.FirstButton.config(bg="#f0f0f0")
                button.config(bg="#f0f0f0")
            if self.MatchedPairs == 4:
                self.generateRound()
            self.FirstClick = None
            self.FirstButton = None

    def endQuiz(self):

        """Destroy the remaining tiles and controls, and display the final score with a button to return to the menu."""

        for button in self.Buttons:
            button.destroy()
        self.Correct.destroy()
        self.Quit.destroy()
        self.ScoreDisplay = tkinter.Label(self.Root, text=self.Quiz.getScore(), font=self.Font)
        self.ScoreDisplay.grid(row=0, column=0, columnspan=2)
        self.ReturnButton = tkinter.Button(self.Root, text="Return to Menu", font=self.Font, command=lambda: self.returnToMenu())
        self.ReturnButton.grid(row=1, column=0, columnspan=2)

    def returnToMenu(self):

        """Destroy the score screen's widgets and rebuild the main menu."""
    
        self.ScoreDisplay.destroy()
        self.ReturnButton.destroy()
        buildMenu(self.Difficulty, self.WordOptions, self.Root)

def errorHandling(message):

    """Repeatedly prompt with message until the user enters 'q' or a valid integer from 1-4, then return that value."""

    flag = True
    answer = ""
    while flag:
        answer = input(message).lower()
        if answer == "q":
            return answer
        try:
            answer = int(answer)
            if answer > 0 and answer < 5:
                return answer
            else:
                print("You didn't enter a number between 1 and 4!")
        except ValueError:
            print("You didn't enter a number (or q)!")

def main():

    """Run the terminal version of the app: a text menu looping between multiple choice, pair matching, and exit."""

    flag = False
    quit = False
    valid = False
    select = 0
    words = Library()
    words.loadJSON("Words.json") # Can also add full path name
    difficulty = Difficulty()
    direction = ""

    while flag == False:
        try:
            select = int(input("""Welcome to the Japanese flashcard learner! Please select from the following options:
    1: Multiple Choice
    2: Pair Matching
    3: Exit """))
        except ValueError:
            print("You didn't enter a number! Please enter a corresponding number.")
        
        if select == 1:
            valid = False
            while valid == False:
                if direction != "e" and direction != "j":
                    direction = input("Do you want to to be given the word in English (e) or Japanese (j)? ").lower()
                else:
                    valid = True

            # Set variables
            quiz = MultipleQuiz(difficulty, words, direction)
            quit = False

            while quit == False:
                distractors = quiz.getQuestion()
                options = quiz.displayQuestion(distractors)
                quit = quiz.checkAnswer(options)
            print(quiz.getScore())
        elif select == 2:
            # Set variables
            quiz = MatchingQuiz(difficulty, words)
            quit = False

            while quit == False:
                quiz.getQuestion()
                quiz.displayQuestion()
                for i in range(4):
                    quit = quiz.checkAnswer(i)
                    if quit:
                        break
            print(quiz.getScore())
        elif select == 3:
            flag = True

    print("さようなら (sayonara)!")

def mainGUI():

    """Launch the GUI version of the app: create the shared window and build the main menu."""

    difficulty = Difficulty()
    words = Library()
    words.loadJSON("Words.json") # Can also add full path name
    root = tkinter.Tk()
    buildMenu(difficulty, words, root)
    root.mainloop()

def buildMenu(difficulty, words, root):

    """Build and display the main menu screen (mode selection) on the given window."""

    menuWidgets = []
    font = ("Courier New", 18)
    baseDisplay = tkinter.Label(root, text="Welcome to the Japanese flashcard learner! Please select from the following options:", font=font)
    menuWidgets.append(baseDisplay)
    baseDisplay.pack()
    options = [tkinter.Button(root, text="1: Multiple Choice", font=font, command=lambda: showDirection(menuWidgets, difficulty, words, root)), tkinter.Button(root, text="2: Pair Matching", font=font, command=lambda: launch(MatchingGUI, menuWidgets, difficulty, words, root))]
    for i in range(2):
        menuWidgets.append(options[i])
        options[i].pack()

def showDirection(menuWidgets, difficulty, words, root):

    """Replace the menu with a screen letting the user choose the multiple-choice prompt direction."""

    for widget in menuWidgets:
        widget.destroy()
    display = tkinter.Label(root, text="Which language would you like the term to be given in?", font=("Courier New", 18))
    menuWidgets.append(display)
    display.pack()
    options = [tkinter.Button(root, text="English", font=("Courier New", 18), command=lambda: launch(MultipleGUI, menuWidgets, difficulty, words, "e", root)), tkinter.Button(root, text="Japanese", font=("Courier New", 18), command=lambda: launch(MultipleGUI, menuWidgets, difficulty, words, "j", root))]
    for i in range(2):
        menuWidgets.append(options[i])
        options[i].pack()

def launch(guiClass, menuWidgets, *args):

    """Destroy the given screen's widgets and construct guiClass with the given arguments, launching the next screen."""

    for widget in menuWidgets:
        widget.destroy()
    guiClass(*args)

if __name__ == "__main__":

    """Comment out the version you are not using (terminal or GUI)."""

    # main()
    mainGUI()
