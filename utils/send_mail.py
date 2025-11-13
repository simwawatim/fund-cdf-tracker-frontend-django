import requests


def send_welcome_email(recipient, username, password):
    """Send login details via external email API and return True only if delivery succeeds."""
    try:
        url = "https://timmails.pythonanywhere.com/api/send-email/"
        payload = {
            "subject": "Your Login Details",
            "header": "Welcome Onboard",
            "recipient": recipient,
            "message": (
                f"Hello <b>{username}</b>,<br><br>"
                f"Your account has been created.<br>"
                f"<b>Username:</b> {username}<br>"
                f"<b>Password:</b> {password}<br><br>"
                
                "Please log in and change your password."
            ),
            "action_url": "https://yourapp.com/login",
            "action_text": "Login Now",
            "system_name": "YourApp",
            "support_email": "help@yourapp.com"
        }

        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if response.status_code == 200 and data.get("status_code") == 200:
            return True

        return False

    except Exception as e:
        print("Email failed:", e)
        return False
