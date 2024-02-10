from flask import request
from flask import Flask
import gitlab
import fnmatch
import requests

app = Flask(__name__)

gl = gitlab.Gitlab('https://gitlab.com', private_token='GITLAB_PRIVATE_TOKEN_HERE')
project_id="project_host/projact_name"

@app.route('/')
def root():
    return "Hello world"

@app.route("/webhook",methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        print("data object_kind: ",data['object_kind'])
        if 'object_kind' in data and data['object_kind'] == 'push':
            handle_push_event(data)
        if 'object_kind' in data and data['object_kind'] == 'merge_request':
            handle_merge_request_event(data)
        return "Data received! POST"
    else:
        return "Data received! GET"
    
def handle_merge_request_event(data):
    if 'object_attributes' in data and 'action' in data['object_attributes']:
        action = data['object_attributes']['action']
        print("action: ",action)
        if action == 'open':
            details = get_merge_request_details(data)
            print("details: ",details)
            message = get_merge_message(details)
            print("message: ",message)
            send_message(message)

def send_message(message):
    headers = {
        'Content-Type': 'application/json',
    }   
    json_data = {"chat_id": CHAT_ID, "text":message} # Replace CHAT_ID by target chat
    response = requests.post("https://tapi.bale.ai/bot{BALE_BOT_TOKEN_HERE}/sendMessage", json=json_data,headers=headers)

def get_merge_request_details(data):
    # Merge Request Attributes
    attributes = data['object_attributes']
    title = attributes['title']
    address = attributes['url']
    description = attributes['description']
    
    # User Who Created Merge Request
    user = data['user']
    created_by = user['username']
    reviewers = []
    assignees = []
    if 'reviewers' in data:
        reviewers = data['reviewers']
    if 'assignees' in data:
        assignees = data['assignees']

    return {"title":title,"address":address,"description":description,"created_by":created_by,"assignees":assignees,"reviewers":reviewers}

def get_merge_message(details):
    message = details['address'] + "\nمرج‌دهنده: " + details['created_by']+ "\nعنوان: " + details['title'] + "\nتوضیحات: \n" + details['description'] + "\n"
    reviwer_info = ""
    for reviewer in details['reviewers']:
        reviwer_info += (get_user_string(reviewer) + "\n")
    if len(reviwer_info) > 0:
        message += ("ریویوکنندگان: \n" + reviwer_info)
    assignees_info = ""
    for assignee in details['assignees']:
        assignees_info += (get_user_string(assignee) + "\n")
    if len(assignees_info) > 0:
        message += ("اساین شدگان: \n" + assignees_info)
    return message

def get_user_string(user):
    return user['name'] + "  @" + user['username']

def handle_push_event(data):
    pushed_branch = data["ref"].replace("refs/heads/","")
    print("pushed branch: ",pushed_branch)
    open_merge_requests = gl.projects.get(project_id).mergerequests.list(state='opened')
    mr_found = False
    for mr in open_merge_requests:
        if mr_found:
            break
        if mr.source_branch == pushed_branch:
            print("Found a merge request!",pushed_branch)
            modified_files = mr.changes()['changes']
            codeowners_file_lines = get_codeowners_content()
            for change in modified_files:
                file_path = change['old_path']
                print("file_path: ",file_path)
                code_owners = get_code_owners(file_path, codeowners_file_lines)
                if "@" + mr.author['username'] in code_owners:
                    mr.approve()
                    mr_found = True
                    break

def get_codeowners_content():
    lines = gl.projects.get(project_id).files.get("CODEOWNERS","main").decode().decode("utf-8")
    lines = lines.split("\n")
    print("get_codeowners_content: ",lines)
    return lines

def get_code_owners(file_path, code_owners_lines):
    print("file_path", file_path)
    lines = code_owners_lines
    print("lines", lines)
    code_owners = []
    for line in lines:
        if line.strip().startswith('#') or not line.strip():
            continue
        parts = line.strip().split()
        file_pattern = parts[0]
        owners = parts[1:]

        if fnmatch.fnmatch(file_path, file_pattern):
            code_owners.extend(owners)
    print("code_owners",code_owners)
    return code_owners