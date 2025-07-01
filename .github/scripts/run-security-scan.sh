#!/bin/bash
set -e

echo "Running Bandit security scan..."

# Run bandit and capture the exit code, but don't fail the workflow immediately
echo "Generating JSON report..."
bandit -r src/ -f json -o bandit-report.json || true

# Also generate a human-readable report for easier review
echo "Generating text report..."
bandit -r src/ -f txt -o bandit-report.txt || true

# Show summary in the workflow log
echo "Bandit security scan completed. Check artifacts for detailed report."
if [ -f bandit-report.json ]; then
    echo "Report generated successfully."

    # Optional: Parse the JSON report and count high-severity issues
    if command -v python3 >/dev/null 2>&1; then
        high_severity=$(python3 -c "
import json
try:
    with open('bandit-report.json', 'r') as f:
        data = json.load(f)
    high_issues = [r for r in data.get('results', []) if r.get('issue_severity') == 'HIGH']
    print(len(high_issues))
except:
    print(0)
")
        echo "High-severity security issues found: $high_severity"

        # Uncomment the line below if you want to fail the workflow on high-severity issues
        # if [ "$high_severity" -gt 0 ]; then exit 1; fi
    fi
else
    echo "Warning: Reports may not have been generated properly."
fi

echo "Security scan completed."
