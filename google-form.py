from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
from transformers import pipeline

# Ask user for the topic
topic = input("Enter the topic for AI-generated answers: ")

# AI Model (Hugging Face - Free Alternative to OpenAI API)
ai_model = pipeline("text-generation", model="distilgpt2")
form_url = input("🔗 Enter Google Form URL: ")


# Setup WebDriver
driver = webdriver.Chrome()

#Google Form URL
driver.get(form_url)

def generate_ai_response(question, topic):
    """Generate AI response based on a given topic."""
    prompt = f"Answer this question briefly about {topic}: {question}"
    response = ai_model(prompt, max_length=50, truncation=True, do_sample=True)

    # Extract and clean generated text
    generated_text = response[0]['generated_text'].strip()
    if "Answer this question" in generated_text:
        generated_text = generated_text.split(":", 1)[-1].strip()

    return generated_text

time.sleep(3)  # Wait for the page to load

while True:  # Loop until "Submit" is found
    # Extract all question elements
    question_elements = driver.find_elements(By.XPATH, '//div[@role="heading"]')
    questions = [q.text.strip() for q in question_elements if q.text.strip()]

    print("Detected Questions:", questions)

    # Identify different input field types
    input_fields = driver.find_elements(By.XPATH, '//input[@type="text"] | //textarea')
    radio_groups = driver.find_elements(By.XPATH, '//div[@role="radiogroup"]')
    checkbox_groups = driver.find_elements(By.XPATH, '//div[@role="group"]')

    # Map questions to their respective input fields
    question_map = []
    for q_element in question_elements:
        text_field = q_element.find_elements(By.XPATH, './following::input[@type="text"] | ./following::textarea')
        radio_group = q_element.find_elements(By.XPATH, './following::div[@role="radiogroup"]')
        checkbox_group = q_element.find_elements(By.XPATH, './following::div[@role="group"]')

        question_map.append({
            "question": q_element.text.strip(),
            "text_field": text_field[0] if text_field else None,
            "radio_group": radio_group[0] if radio_group else None,
            "checkbox_group": checkbox_group[0] if checkbox_group else None
        })

    print("🔍 Question Map:", question_map)

    # Fill the form dynamically
    for q_info in question_map:
        question_text = q_info["question"]
        ai_response = generate_ai_response(question_text, topic)
        print(f"📝 Processing Question: {question_text}")

        # Handle text inputs
        if q_info["text_field"]:
            print(f"✏️ Filling text field: {ai_response}")
            q_info["text_field"].send_keys(ai_response)
            time.sleep(1)

        # Handle radio buttons (Single Choice)
        elif q_info["radio_group"]:
            options = q_info["radio_group"].find_elements(By.XPATH, './/div[@role="radio"]')
            if options:
                random_choice = random.choice(options)  # Pick a random option
                print(f"🔘 Selecting radio option: {random_choice.text}")
                random_choice.click()
                time.sleep(1)

        # Handle checkboxes (Multiple Choice)
        elif q_info["checkbox_group"]:
            options = q_info["checkbox_group"].find_elements(By.XPATH, './/div[@role="checkbox"]')
            if options:
                num_choices = random.randint(1, len(options))  # Select 1 or more checkboxes
                selected_options = random.sample(options, num_choices)

                for checkbox in selected_options:
                    print(f"Selecting checkbox option: {checkbox.text}")
                    checkbox.click()
                    time.sleep(1)

    # Check if "Next" or "Submit" is available
    try:
        next_button = driver.find_element(By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]')
        print("Clicking Next Button")
        next_button.click()
        time.sleep(3)  # Wait for the next page to load
    except:
        try:
            submit_button = driver.find_element(By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]')
            print("Clicking Submit Button")
            submit_button.click()
            print("Form submitted successfully!")
            break  # Exit the loop after submitting
        except:
            print("No Next or Submit button found. Exiting.")
            break

# Close Browser
time.sleep(3)
driver.quit()
