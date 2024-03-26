import os
import csv


def find_tags_and_items(directory):
    tag_items = {}  # Dictionary to store tags and their associated items
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if line.strip().startswith('/*') or line.strip().endswith('*/'):
                    continue  # Skip comment lines
                if "Tags =" in line:
                    tags_part = line.split('Tags =')[1].strip().rstrip(',')
                    tags = tags_part.split(';')
                    # Find the associated item
                    item_name = None
                    for j in range(i, -1, -1):  # Scan upwards to find "item"
                        if lines[j].strip().startswith("item"):
                            item_name = lines[j].split()[1]  # Assume "item name"
                            break
                    if item_name:
                        for tag in tags:
                            if tag:  # Ensure the tag is not empty
                                tag = tag.strip()
                                if tag not in tag_items:
                                    tag_items[tag] = set()
                                tag_items[tag].add(item_name)

    # Convert sets to sorted lists
    for tag in tag_items:
        tag_items[tag] = sorted(tag_items[tag])

    return tag_items

def find_food_types(directory):
    food_type_items = {}  # Dictionary to store food types and their associated items
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if line.strip().startswith('/*') or line.strip().endswith('*/'):
                    continue  # Skip comment lines
                if "FoodType =" in line:
                    food_type_part = line.split('FoodType =')[1].strip().rstrip(',')
                    food_type = food_type_part.strip()
                    # Find the associated item
                    item_name = None
                    for j in range(i, -1, -1):  # Scan upwards to find "item"
                        if lines[j].strip().startswith("item"):
                            item_name = lines[j].split()[1]  # Assume "item name"
                            break
                    if item_name and food_type:
                        if food_type not in food_type_items:
                            food_type_items[food_type] = set()
                        food_type_items[food_type].add(item_name)

    # Convert sets to sorted lists
    for food_type in food_type_items:
        food_type_items[food_type] = sorted(food_type_items[food_type])

    return food_type_items


def write_associations_to_csv(tag_items, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure the output directory exists
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        for tag, items in tag_items.items():
            csvwriter.writerow([tag] + items)


def load_translations(translation_file):
    translations = {
        'CannedPineappleOpen': 'Opened Canned Pineapple'  # Direct translation for specific case
    }
    with open(translation_file, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:  # Ensure the line contains a translation mapping
                parts = line.strip().split(' = ')
                if len(parts) == 2:
                    key, value_with_quotes = parts
                    item_name = key.split('.')[-1]  # Get the item name after the last dot
                    # Check if specific translation is already provided
                    if item_name not in translations:
                        # Find the last quotation mark and exclude everything after it
                        last_quote_index = value_with_quotes.rfind('"')
                        if last_quote_index != -1:
                            translated_name = value_with_quotes[1:last_quote_index]  # Exclude the first and last quotes
                            translations[item_name] = translated_name
    return translations


def translate_item_names(tag_items, translations):
    translated_tag_items = {}
    failed_translations = []  # Keep track of items that failed to translate

    for tag, items in tag_items.items():
        translated_items = []
        for item in items:
            if item in translations:
                translated_items.append(translations[item])
            else:
                failed_translations.append(item)
                print(f"Failed to translate '{item}'. Reason: No translation found.")
        translated_tag_items[tag] = translated_items

    if failed_translations:
        print("Some item names could not be translated. Please check the translation file.")

    return translated_tag_items


def csv_to_wikitable(input_csv_path):
    # Initialize the table with headers
    table_str = '{| class="wikitable theme-blue"\n|-\n! Tag !! Items\n'

    # Prepare to sort tags alphabetically
    tag_items_sorted = []
    with open(input_csv_path, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            tag_items_sorted.append(row)

    # Sort by tag (first column)
    tag_items_sorted.sort(key=lambda x: x[0])

    for row in tag_items_sorted:
        tag = row[0]
        # Modify the tag formatting as per the new requirement
        tag_formatted = f'<span id="tag-{tag}">[[#{tag}|{tag}]]</span>'
        items = ']], [['.join(row[1:])
        table_str += f'|-\n| {tag_formatted} || [[{items}]]\n'
    table_str += '|}'
    return table_str


def main():
    # Define file paths
    scripts_directory = 'resources/scripts'
    output_file_tags = 'output/associated_tags.csv'
    output_file_food_types = 'output/FoodType.csv'  # Output file for food types CSV
    wiki_table_file_tags = 'output/completed_output_tags.txt'  # Final output file name for tags
    wiki_table_file_food_types = 'output/completed_output_food_types.txt'  # Final output file name for food types
    translation_file = 'resources/translate.txt'

    # Load translations
    translations = load_translations(translation_file)

    # --- Process Tags ---
    tag_items = find_tags_and_items(scripts_directory)
    translated_tag_items = translate_item_names(tag_items, translations)
    write_associations_to_csv(translated_tag_items, output_file_tags)

    # Generate the wiki table string for tags and write to the output file
    wiki_table_str_tags = csv_to_wikitable(output_file_tags)
    header_text_tags = """'''Warning: Everything below has been programmatically generated - any changes made will be lost on the next update!'''
If you would like to generate this file please use the github repo found [https://github.com/CalvyPZ/PZ-scripts-to-item-tag here].
All item names have been modified for readability and linkability.

Project Zomboid uses tags to define what can and can't be used for specific recipes. The following table shows what items count towards a specific tag.

==Tags==
"""
    with open(wiki_table_file_tags, 'w', encoding='utf-8') as f:
        f.write(header_text_tags + wiki_table_str_tags)
    print(f"Completed output with sorted tags and header has been written to {wiki_table_file_tags}")

    # --- Process Food Types ---
    food_types = find_food_types(scripts_directory)
    translated_food_types = translate_item_names(food_types, translations)
    write_associations_to_csv(translated_food_types, output_file_food_types)

    # Generate the wiki table string for food types and write to the output file
    wiki_table_str_food_types = csv_to_wikitable(output_file_food_types)
    header_text_food_types = """'''Warning: Everything below has been programmatically generated - any changes made will be lost on the next update!'''
If you would like to generate this file please use the github repo found [https://github.com/CalvyPZ/PZ-scripts-to-item-tag here].
All item names have been modified for readability and linkability.

Project Zomboid uses food types to define food items. The following table shows the food types assigned to specific items.

==Food Types==
"""
    with open(wiki_table_file_food_types, 'w', encoding='utf-8') as f:
        f.write(header_text_food_types + wiki_table_str_food_types)


    print(f"Completed output with sorted food types and header has been written to {wiki_table_file_food_types}")

if __name__ == "__main__":
    main()