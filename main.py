import requests
import json
from bs4 import BeautifulSoup

def process_word_data(word, html_content):
    """
    Processes the HTML content from the API response, extracts word definitions,
    and returns a structured dictionary.

    Args:
        word (str): The original word that was queried.
        html_content (str): The HTML string from the API response.

    Returns:
        dict: A dictionary containing the processed word information.
              Format:
             {
                "word": "word one",
                "success": true,
                "description": "word one description"
                "similar_words": [
                {
                    "word": "similar word one",
                    "success": true,
                    "description": "similar word one description"
                 }
                ]
            }
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    definitions = []
    current_word = None
    current_description = []
    
    # Helper function to clear description
    def clear_description():
      nonlocal current_description
      current_description = []

    for element in soup.find_all(['dt', 'dd', 'br']):
        if element.name == 'dt':
            if current_word:
                definitions.append({
                "word": current_word.strip(),
                "success": (current_word.strip() == word),
                "description":  " ".join(current_description).strip(),
                })
                clear_description()

            current_word = element.text.split(' ')[0].strip()
            
        elif element.name == 'dd':
             current_description.append(element.text.strip())
        
    #Append last item
    if current_word:
       definitions.append({
                "word": current_word.strip(),
                "success": (current_word.strip() == word),
                "description": " ".join(current_description).strip(),
                })
        
    
    # Structure the output
    result = {
        "word": word,
        "success": any(d["success"] for d in definitions),
        "similar_words": []
    }
    
    
    for definition in definitions:
      if definition["word"] == word:
        result["description"] = definition["description"]
      else:
           result["similar_words"].append({
            "word": definition["word"],
            "success": True,
            "description": definition["description"]
           })
    
    if not result["similar_words"]:
       result["similar_words"] = None
        
    return result

def get_word_information(word):
    """Fetches information for a given word from the API."""
    url = "http://www.fjalori.shkenca.org/text.php"
    payload = {"eingabe": word}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.text
    else:
        return None


def main():
    words_to_check = ["Buke", "Tavoline", "Majmun", "Vrapoj"]
    all_word_data = []

    for word in words_to_check:
      html_content = get_word_information(word)
      if html_content:
          word_data = process_word_data(word, html_content)
          all_word_data.append(word_data)

    with open("words.json", "w", encoding="utf-8") as f:
        json.dump(all_word_data, f, indent=2, ensure_ascii=False)
    
    print("Data written to words.json")


if __name__ == "__main__":
    main()