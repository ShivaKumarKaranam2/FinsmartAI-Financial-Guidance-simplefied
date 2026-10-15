import json
import os

# --- CONFIGURATION ---
# Replace these names with your actual JSON filenames
files_to_merge = ["finance_finetune_data.json", "dataset.json"] 
output_file = "final_merged_dataset.json"

def merge_json_files():
    combined_data = []
    
    print(f"🔄 Starting merge process...")

    for filename in files_to_merge:
        if not os.path.exists(filename):
            print(f"⚠️ Warning: '{filename}' not found. Skipping.")
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check if the file contains a list (which it should)
                if isinstance(data, list):
                    combined_data.extend(data)
                    print(f"✅ Loaded {len(data)} items from '{filename}'")
                else:
                    print(f"⚠️ Warning: '{filename}' is not a list of Q&A pairs. Skipped.")
                    
        except json.JSONDecodeError:
            print(f"❌ Error: '{filename}' is not a valid JSON file.")

    # Save the final merged file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4, ensure_ascii=False)

    print(f"\n🎉 Merge Complete!")
    print(f"📊 Total items in merged file: {len(combined_data)}")
    print(f"💾 Saved as: {output_file}")

if __name__ == "__main__":
    merge_json_files()