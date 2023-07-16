# Work Scripts Repository
A central storage for synchronizing scripts across various workstations.

---

### GSM Integration Script
This script receives data from the GSM site and records it to a file. It then forwards this file to the Itigris servers. The resulting information is dispatched to Telegram via a bot.

### Payment Registry Scripts
These scripts take hard-coded data, format it, and store it in the clipboard for future use.

### Tilda Integration
This is a Flask server that receives data from Tilda and subsequently sends it to Bitrix.

### BXBD Comparison Script
This script compares two data dumps. It identifies and logs any disparities or missing elements and sends this information to the database.

### Bonuses Script
This script extracts phone numbers from a CSV file and generates requests to retrieve the rest of the client's bonus information.

### Client Duplicate Finder
This script identifies client duplicates in a CSV file based on phone numbers.

###  Get Client ID Script
This script accepts the client number as input and returns the corresponding ID from Optima.

Please ensure the scripts are updated to the latest versions in all workstations for optimal performance and synchronization.
