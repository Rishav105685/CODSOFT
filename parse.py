import fitz as PyMuPDF
import json
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer

# Initialize WordNet lemmatizer
lemmatizer = WordNetLemmatizer()

# Function to clean and lemmatize text
def clean_up_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    tokens = nltk.word_tokenize(text.lower())  # Tokenize and lowercase
    tokens = [lemmatizer.lemmatize(token) for token in tokens]  # Lemmatize
    return ' '.join(tokens)

# Function to check if an intent already exists
def intent_exists(intents, tag, patterns):
    for intent in intents:
        if intent['tag'] == tag and any(pattern in intent['patterns'] for pattern in patterns):
            return True
    return False

# Function to parse PDF and extract intents from meaningful sections
def parse_pdf_and_extract_intents(pdf_file, intents_json_file):
    try:
        with open(intents_json_file, 'r') as file:
            intents = json.load(file)  # Load existing intents
    except FileNotFoundError:
        intents = []  # Initialize as empty list if file doesn't exist
    except json.JSONDecodeError:
        intents = []  # Initialize as empty list if file is empty or corrupted

    # Initialize empty lists for new intents
    new_intents = []

    # Parse PDF
    pdf_document = PyMuPDF.open(pdf_file)

    # Iterate through pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("dict")['blocks']

        for block in blocks:
            if block['type'] == 0:  # Text block
                lines = block['lines']
                for line in lines:
                    if line['spans']:
                        text = line['spans'][0]['text'].strip()
                        if len(text) > 20:  # Example condition for meaningful content
                            # Clean and tokenize line
                            cleaned_line = clean_up_text(text)

                            # Create intent
                            tag = f'heading_{page_num}_{lines.index(line)}'  # Unique tag for each heading
                            patterns = [text]
                            responses = ["Example response for " + text[:50]]  # Example response based on content
                            context = ["Page " + str(page_num + 1)]  # Optional context information

                            # Check if intent already exists
                            if not intent_exists(intents, tag, patterns):
                                new_intents.append({"tag": tag, "patterns": patterns, "responses": responses, "context": context})

    # Add new intents to existing intents
    intents.extend(new_intents)

    # Save to intents2.json
    with open(intents_json_file, 'w') as file:
        json.dump(intents, file, indent=4)

    print(f"Extracted {len(new_intents)} new intents. Saved to intents2.json.")

# Example usage
if __name__ == "__main__":
    pdf_file = 'path.pdf'  # Replace with your PDF file path
    intents_json_file = 'intents2.json'  # Existing intents file
    parse_pdf_and_extract_intents(pdf_file, intents_json_file)
