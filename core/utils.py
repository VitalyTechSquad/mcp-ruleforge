import json
import os
import re

def _parse_md_content(content):
    """Parses raw markdown content into a dictionary."""
    print("[DEBUG] _parse_md_content: Starting to parse content.")
    rules = {}
    current_section = None
    section_content = ""

    for line in content.splitlines():
        print(f"[DEBUG]  - Processing line: {repr(line)}")
        # Check for a section header (e.g., # aiPrompt, ## find)
        header_match = re.match(r'^#+\s+(.+)', line)
        if header_match:
            print(f"[DEBUG]    -> Matched header.")
            # If we were in a section, save its content before starting a new one
            if current_section and section_content:
                print(f"[DEBUG]    -> Saving previous section '{current_section}'.")
                rules[current_section] = section_content.strip()

            current_section = header_match.group(1).strip()
            section_content = ""
            print(f"[DEBUG]    -> Started new section '{current_section}'.")
        elif current_section:
            # Append the line to the current section's content
            section_content += line + "\n"

    # Save the last section's content
    if current_section and section_content:
        print(f"[DEBUG]  - Saving final section '{current_section}'.")
        rules[current_section] = section_content.strip()

    print(f"[DEBUG] _parse_md_content: Raw parsed rules before list processing: {rules}")

    # Post-process sections that should be lists
    for key in ['ignorePaths', 'find', 'symbols']:
        if key in rules and isinstance(rules[key], str):
            # Split by lines, filter out empty ones, and remove markdown list markers
            list_items = [re.sub(r'^\s*-\s*', '', item).strip() for item in rules[key].splitlines() if item.strip()]
            
            # For find/symbols, which are lists of objects, we need more structure.
            # Let's assume a simple format for now: each line is a string.
            # A better implementation would parse yaml-like objects.
            if key in ['find', 'symbols']:
                processed_items = []
                for item in list_items:
                    # Assuming format "label: description" or "label:: description"
                    match = re.match(r'([^:]+):{1,2}\s*(.*)', item)
                    if match:
                        label, desc = match.groups()
                        processed_items.append({"label": label.strip(), "description": desc.strip()})
                    else:
                        processed_items.append({"description": item})
                rules[key] = processed_items
            else: # ignorePaths
                 rules[key] = list_items

    print(f"[DEBUG] _parse_md_content: Final parsed rules: {rules}")
    return rules


def _format_md_content(data):
    """Formats a dictionary into a markdown string."""
    content = ""
    if 'aiPrompt' in data:
        content += f"# aiPrompt\n{data['aiPrompt']}\n\n"

    if 'ignorePaths' in data and data['ignorePaths']:
        content += "# ignorePaths\n"
        for item in data['ignorePaths']:
            content += f"- {item}\n"
        content += "\n"

    # For find and symbols, we format them back from the dict structure.
    if 'find' in data and data['find']:
        content += "# find\n"
        for item in data['find']:
            if "label" in item:
                content += f"- {item['label']}: {item.get('description', '')}\n"
            else:
                content += f"- {item.get('description', '')}\n"

        content += "\n"

    if 'symbols' in data and data['symbols']:
        content += "# symbols\n"
        for item in data['symbols']:
            if "label" in item:
                content += f"- {item['label']}: {item.get('description', '')}\n"
            else:
                content += f"- {item.get('description', '')}\n"
        content += "\n"
        
    return content

def load_mdc_file(file_path):
    """Loads a template file and returns a dict with frontmatter and content."""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract YAML frontmatter if present
            frontmatter_pattern = re.compile(r'^\s*---\s*$\n(.*?)\n^\s*---\s*$\n?(.*)', re.DOTALL | re.MULTILINE)
            match = frontmatter_pattern.match(content)
            
            if match:
                frontmatter_text = match.group(1).strip()
                content_text = match.group(2).strip()
                return {
                    'frontmatter': frontmatter_text,
                    'content': content_text
                }
            else:
                # No frontmatter found, return just content
                return {
                    'frontmatter': None,
                    'content': content.strip()
                }
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def save_mdc_file(file_path, data):
    """Saves content to a file. Can handle strings or dicts with frontmatter."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(data, dict) and 'frontmatter' in data:
                # Write with frontmatter
                if data['frontmatter']:
                    f.write('---\n')
                    f.write(data['frontmatter'])
                    f.write('\n---\n\n')
                f.write(data.get('content', ''))
            else:
                # Treat as plain string
                f.write(str(data))
        return True
    except IOError as e:
        print(f"Error writing to {file_path}: {e}")
        return False

def load_json_file(file_path):
    """Loads a JSON file and returns its content."""
    if not os.path.exists(file_path):
        # print(f"Error: File not found at {file_path}") # Decide if utils should print or raise
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def save_json_file(file_path, data):
    """Saves data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except IOError as e:
        print(f"Error writing JSON to {file_path}: {e}")
        return False
    except TypeError as e:
        print(f"Error: Data for {file_path} is not JSON serializable: {e}")
        return False

def merge_rules(base_rules, custom_rules_data):
    """Merges base rules with custom rules. 
       Custom rules can override base rules at the top level (ignorePaths, aiPrompt)
       or append to lists (find, symbols).
    """
    if not custom_rules_data:
        return base_rules

    merged = base_rules.copy()

    # Top-level string overrides
    for key in ["aiPrompt"]:
        if key in custom_rules_data:
            merged[key] = custom_rules_data[key]

    # List appends/overrides for ignorePaths, find, symbols
    # For find and symbols, we might want to append new items and potentially update existing ones
    # if an item in custom_rules has a matching "label" or unique identifier.
    # For simplicity now, we'll append unique items for `find` and `symbols` 
    # and replace `ignorePaths`.

    if "ignorePaths" in custom_rules_data:
        # Overwrite ignorePaths if specified in custom, otherwise keep base
        merged["ignorePaths"] = custom_rules_data["ignorePaths"]
    
    # For 'find' and 'symbols', append new items. 
    # A more sophisticated merge could update items if they have a unique identifier.
    for key in ["find", "symbols"]:
        if key in custom_rules_data and isinstance(custom_rules_data[key], list):
            if key not in merged or not isinstance(merged[key], list):
                merged[key] = [] # Initialize if not present or not a list in base
            
            # Simple append of all custom items. 
            # For a more robust solution, you might want to avoid duplicates based on a specific field within the dicts.
            for item in custom_rules_data[key]:
                merged[key].append(item)
                
    # Handle other potential custom rule structures as needed.
    # For example, if custom_rules_data has other top-level keys not in base_rules.
    for key, value in custom_rules_data.items():
        if key not in merged: # Add new keys from custom_rules
             merged[key] = value

    return merged 