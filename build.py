import re
import os

def main():
    print("Starting build...")
    
    # 1. Read Layout
    try:
        with open('_layouts/default.html', 'r', encoding='utf-8') as f:
            layout = f.read()
    except FileNotFoundError:
        print("Error: _layouts/default.html not found.")
        return

    # 2. Prepare Content Accumulator
    content_html = ""

    # 3. Define Includes Order
    includes = [
        "navbar.html",
        "hero.html",
        "meditation.html",
        "spiritual_itinerary.html",
        "program.html",
        "logistics.html",
        "timeline.html",
        "features_iaccarino.html",
        "video_100presepi.html",
        "history.html",
        "jubilee_calendar.html",
        "guide_chapters.html",
        "study_guide.html",
        "footer.html"
    ]

    # 4. Helper to parse YAML
    def parse_yaml(file_path):
        events = []
        current_event = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
            return []

        for line in lines:
            line = line.strip()
            if not line:
                if current_event:
                    events.append(current_event)
                    current_event = {}
                continue
            
            if line.startswith("- date:"):
                if current_event:
                    events.append(current_event)
                    current_event = {}
                parts = line.split(":", 1)
                if len(parts) > 1:
                    current_event['date'] = parts[1].strip().strip('"')
            elif ":" in line and not line.startswith("#"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    key = parts[0].strip()
                    val = parts[1].strip().strip('"')
                    current_event[key] = val
                
        if current_event:
            events.append(current_event)
        return events

    # 5. Process Includes
    for inc_name in includes:
        path = os.path.join('_includes', inc_name)
        if not os.path.exists(path):
            print(f"Warning: Include {inc_name} not found.")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            inc_content = f.read()
        
        # Handle Calendar Special Case
        if inc_name == "jubilee_calendar.html":
            events = parse_yaml('_data/jubilee_events.yml')
            
            loop_start_marker = "{% for event in site.data.jubilee_events %}"
            loop_end_marker = "{% endfor %}"
            
            if loop_start_marker in inc_content and loop_end_marker in inc_content:
                parts = inc_content.split(loop_start_marker)
                pre_loop = parts[0]
                rest = parts[1]
                loop_body_parts = rest.split(loop_end_marker)
                loop_body = loop_body_parts[0]
                post_loop = loop_body_parts[1]
                
                generated_html = ""
                for evt in events:
                    item_html = loop_body
                    item_html = item_html.replace("{{ event.date }}", evt.get('date', ''))
                    item_html = item_html.replace("{{ event.title }}", evt.get('title', ''))
                    item_html = item_html.replace("{{ event.location }}", evt.get('location', ''))
                    item_html = item_html.replace("{{ event.description }}", evt.get('description', ''))
                    item_html = item_html.replace("{{ event.transport }}", evt.get('transport', ''))
                    
                    # Handle Time Condition
                    time_val = evt.get('time', '')
                    
                    # Regex for the IF block
                    # Note: We need to match lazily across newlines
                    if_pattern = re.compile(r'{%\s*if event.time.*?%}(.*?){%\s*endif\s*%}', re.DOTALL)
                    
                    def time_replacer(match):
                        content = match.group(1)
                        if time_val and "non indicato" not in time_val.lower() and "non specificato" not in time_val.lower():
                            return content.replace("{{ event.time }}", time_val)
                        return "" # Remove block if no valid time
                    
                    item_html = if_pattern.sub(time_replacer, item_html)
                    
                    generated_html += item_html
                
                inc_content = pre_loop + generated_html + post_loop

        content_html += inc_content + "\n"

    # 6. Final Assembly
    final_html = layout.replace('{{ page.title | default: "Giubileo Roma: 3 Gennaio 2026" }}', "Giubileo Roma: 3 Gennaio 2026")
    final_html = final_html.replace('{{ content }}', content_html)

    # 7. Write Output
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

    print("Build complete. index.html generated.")

if __name__ == "__main__":
    main()
