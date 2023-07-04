#!/bin/bash

# Change to the directory with your repository if necessary
# cd /path/to/your/repository

# Run chmod +x 00_auto_commit.sh to make your script executable.
# Now you can run the script with ./00_auto_commit.sh

# Check the status first
git status

# Add changes to the index
git add .

# Commit the changes
git commit -m "Auto Commit"

# Push the changes
git push origin master