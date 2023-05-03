# SMS Bulk Sender Reminder Service

Via an existing spreadsheet driven business process, automate the sending of SMS
reminders without impacting on existing processes (don't change the template),
but do same the business time by automating the sending of SMS reminders.

# Install


```
cp .env.example .env
```

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

# Run

```
. venv/bin/activate
cd src/web
flask --debug run
```
