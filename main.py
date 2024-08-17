import telebot
import random
import threading
import time
from collections import defaultdict, deque
import spacy

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '7426761999:AAEED3SDrwC8pGh-x6wVbjLmgqsocMGfilU'
bot = telebot.TeleBot(bot_token)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class SmertButt:
    def __init__(self):
        self.memory = defaultdict(list)
        self.recent_conversations = deque(maxlen=5)  # Store recent conversations
        self.load_initial_knowledge()

    def load_initial_knowledge(self):
        try:
            with open('data.txt', 'r', encoding='utf-8') as file:
                text = file.read()
                sentences = text.split('\n')
                for sentence in sentences:
                    if sentence.strip():
                        self.learn(sentence.strip())
            print("Initial knowledge loaded successfully.")
        except FileNotFoundError:
            print("data.txt not found. Starting with an empty brain.")

    def save_knowledge(self, message):
        with open('data.txt', 'a', encoding='utf-8') as file:
            file.write(message + '\n')

    def learn(self, message):
        doc = nlp(message)
        for token in doc:
            if token.pos_ in {'NOUN', 'PROPN'}:  # Focus on nouns and proper nouns
                self.memory[token.text.lower()].append(token.head.text.lower())
        self.recent_conversations.append(message)

    def generate(self, seed, length=10):
        if seed not in self.memory:
            return "I'm still learning, senpai!"
        result = [seed]
        for _ in range(length - 1):
            if not self.memory[seed]:
                break
            seed = random.choice(self.memory[seed])
            result.append(seed)
        return ' '.join(result)

    def respond_to_patterns(self, message):
        doc = nlp(message)
        entities = [ent.text for ent in doc.ents]
        if entities:
            return f"Noticed these entities: {', '.join(entities)}"
        for word in message.split():
            if word.lower() in self.memory:
                return self.generate(word.lower())
        return None

    def build_useful_response(self):
        if len(self.recent_conversations) < 2:
            return "Tell me more about what you're thinking."

        recent_messages = list(self.recent_conversations)[-2:]
        return " ".join(recent_messages)

smert_butt = SmertButt()

@bot.message_handler(commands=['say'])
def handle_say(message):
    command_text = message.text.split(maxsplit=1)
    if len(command_text) < 2:
        bot.reply_to(message, "You gotta tell me what word to use, senpai!")
        return
    
    seed_word = command_text[1].lower()
    response = smert_butt.generate(seed_word)
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    smert_butt.learn(message.text)
    smert_butt.save_knowledge(message.text)

    response = smert_butt.respond_to_patterns(message.text)
    if response:
        bot.send_message(message.chat.id, response)
    else:
        if random.random() < 0.1:  # 10% chance to respond automatically
            if random.random() < 0.5:  # 50% chance to use a more useful response
                response = smert_butt.build_useful_response()
            else:
                seed = random.choice(message.text.split())
                response = smert_butt.generate(seed.lower())
            bot.send_message(message.chat.id, response)

# Background thread to send messages periodically
def periodic_message():
    while True:
        time.sleep(1)  # Wait 10 minutes
        # Choose a random chat and send a message if it has enough data
        if smert_butt.memory:
            chat_id = -1002108265780  # Replace with your actual chat ID or make it dynamic
            if random.random() < 0.5:  # 50% chance to use a more useful response
                response = smert_butt.build_useful_response()
            else:
                seed = random.choice(list(smert_butt.memory.keys()))
                response = smert_butt.generate(seed)
            bot.send_message(chat_id, response)

# Start the periodic message thread
thread = threading.Thread(target=periodic_message)
thread.start()

# Start polling for messages
bot.polling()
