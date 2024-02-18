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
        # Use <span> for tags instead of [[]]
        tag_span = f'<span id="{tag}">{tag}</span>'
        items = ']], [['.join(row[1:])
        # Adjust items to be wrapped in <span> as well, if needed
        table_str += f'|-\n| {tag_span} || [[{items}]]\n'
    table_str += '|}'
    return table_str


def main():
    scripts_directory = 'resources/scripts'
    output_file = 'output/associated_tags.csv'
    wiki_table_file = 'output/completed_output.txt'  # Changed to the final output file name
    translation_file = 'resources/translate.txt'

    translations = load_translations(translation_file)
    tag_items = find_tags_and_items(scripts_directory)
    translated_tag_items = translate_item_names(tag_items, translations)
    write_associations_to_csv(translated_tag_items, output_file)

    # Generate the wiki table string
    wiki_table_str = csv_to_wikitable(output_file)

    # Prepend the header text
    header_text = """'''Warning: Everything below has been programmatically generated - any changes made will be lost on the next update!'''
If you would like to generate this file please use the github repo found [https://github.com/CalvyPZ/PZ-scripts-to-item-tag here].
All item names have been modified for readability and linkability.

Project Zomboid uses tags to define what can and cant be used for specific recipes. The following table shows what items count towards a specific tag.

==Tags==
"""
    # Write the header and the table to the final output file
    with open(wiki_table_file, 'w', encoding='utf-8') as f:
        f.write(header_text + wiki_table_str)

    print(f"Completed output with sorted tags and header has been written to {wiki_table_file}")


if __name__ == "__main__":
    main()