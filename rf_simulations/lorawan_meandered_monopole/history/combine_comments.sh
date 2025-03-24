#!/usr/bin/env bash

# Name of the file to gather everything in
OUTPUT_FILE="combined_notes.md"

# Start fresh
> "$OUTPUT_FILE"

# Loop through each attempt_* folder
for folder in attempt_*; do
  # Only proceed if it's actually a directory
  if [ -d "$folder" ]; then
    NOTES_FILE="$folder/notes.md"
    # Check if notes.md exists
    if [ -f "$NOTES_FILE" ]; then
      # Add a Markdown heading with the folder name
      echo "# $folder" >> "$OUTPUT_FILE"
      # Append the contents of notes.md
      cat "$NOTES_FILE" >> "$OUTPUT_FILE"
      # Add a blank line after each section
      echo "" >> "$OUTPUT_FILE"
    fi
  fi
done

echo "All notes combined into $OUTPUT_FILE"